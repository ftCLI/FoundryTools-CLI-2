import itertools
from typing import Mapping, Callable

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.roundTools import otRound
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import ttFont
from fontTools.ttLib.tables import _g_l_y_f, C_F_F_
import pathops

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger

_TTGlyphMapping = Mapping[str, ttFont._TTGlyph]


def skia_path_from_glyph(glyph_name: str, glyph_set: _TTGlyphMapping) -> pathops.Path:
    """
    Returns a pathops.Path from a glyph

    :param glyph_name: the glyph name
    :param glyph_set: the glyphSet to which the glyph belongs
    :return: a pathops.Path object
    """
    path = pathops.Path()
    pen = path.getPen(glyphSet=glyph_set)
    glyph_set[glyph_name].draw(pen)
    return path


def skia_path_from_glyph_component(
    component: _g_l_y_f.GlyphComponent, glyph_set: _TTGlyphMapping
) -> pathops.Path:
    """
    Returns a pathops.Path from a glyph component

    :param component: the glyph component
    :param glyph_set: the glyphSet to which the glyph belongs
    :return: a pathops.Path object
    """
    base_glyph_name, transformation = component.getComponentInfo()
    path = skia_path_from_glyph(glyph_name=base_glyph_name, glyph_set=glyph_set)
    return path.transform(*transformation)


def ttf_components_overlap(glyph: _g_l_y_f.Glyph, glyph_set: _TTGlyphMapping) -> bool:
    """
    Checks if a TrueType composite glyph has overlapping components.

    :param glyph: the glyph
    :param glyph_set: the glyphSet to which the glyph belongs
    :return: True if the glyph has overlapping components, False otherwise
    """
    if not glyph.isComposite():
        raise ValueError("This method only works with TrueType composite glyphs")
    if len(glyph.components) < 2:
        return False

    component_paths = {}

    def _get_nth_component_path(index: int) -> pathops.Path:
        if index not in component_paths:
            component_paths[index] = skia_path_from_glyph_component(
                glyph.components[index], glyph_set
            )
        return component_paths[index]

    return any(
        pathops.op(
            _get_nth_component_path(i),
            _get_nth_component_path(j),
            pathops.PathOp.INTERSECTION,
            clockwise=True,
            fix_winding=True,
            keep_starting_points=False,
        )
        for i, j in itertools.combinations(range(len(glyph.components)), 2)
    )


def ttf_glyph_from_skia_path(path: pathops.Path) -> _g_l_y_f.Glyph:
    """
    Returns a TrueType glyph from a pathops.Path

    :param path: the pathops.Path
    :return: a TrueType glyph
    """
    tt_pen = TTGlyphPen(glyphSet=None)
    path.draw(tt_pen)
    glyph = tt_pen.glyph()
    glyph.recalcBounds(glyfTable=None)
    return glyph


def t2_charstring_from_skia_path(path: pathops.Path, width: int) -> T2CharString:
    """
    Returns a T2CharString from a pathops.Path

    :param path: the pathops.Path
    :param width: the glyph width
    :return: a T2CharString
    """
    t2_pen = T2CharStringPen(width, glyphSet=None)
    path.draw(t2_pen)
    charstring = t2_pen.getCharString()
    return charstring


def round_path(path: pathops.Path, rounder: Callable[[float], float] = otRound) -> pathops.Path:
    """
    Rounds the points coordinate of a pathops.Path

    :param path: the path to round
    :param rounder: the function to call
    :return: the path with rounded points
    """
    rounded_path = pathops.Path()
    for verb, points in path:
        rounded_path.add(verb, *((rounder(p[0]), rounder(p[1])) for p in points))
    return rounded_path


def simplify_path(path: pathops.Path, glyph_name: str, clockwise: bool) -> pathops.Path:
    """
    Simplify a pathops.Path by removing overlaps, fixing contours direction and, optionally,
    removing tiny paths

    :param path: the pathops.Path to simplify
    :param glyph_name: the glyph name
    :param clockwise: must be True for TTF fonts, False for OTF fonts
    :return: the simplified path
    """

    # skia-pathops has a bug where it sometimes fails to simplify paths when there
    # are float coordinates and control points are very close to one another.
    # Rounding coordinates to integers works around the bug.
    # Since we are going to round glyf coordinates later on anyway, here it is
    # ok(-ish) to also round before simplify. Better than failing the whole process
    # for the entire font.
    # https://bugs.chromium.org/p/skia/issues/detail?id=11958
    # https://github.com/google/fonts/issues/3365

    try:
        return pathops.simplify(path, fix_winding=True, clockwise=clockwise)
    except pathops.PathOpsError:
        pass

    path = round_path(path)
    try:
        path = pathops.simplify(path, fix_winding=True, clockwise=clockwise)
        logger.info(
            f"skia-pathops failed to simplify glyph '{glyph_name}' with float coordinates, but "
            f"succeeded using rounded integer coordinates"
        )
        return path
    except pathops.PathOpsError as e:
        logger.error(f"skia-pathops failed to simplify glyph '{glyph_name}': {e}")

    raise AssertionError("Unreachable")


def same_path(path_1: pathops.Path, path_2: pathops.Path) -> bool:
    """
    Checks if two pathops paths are the same

    :param path_1: the first path
    :param path_2: the second path
    :return: True if the paths are the same, False if the paths are different
    """
    if {tuple(c) for c in path_1.contours} != {tuple(c) for c in path_2.contours}:
        return False
    return True


def remove_tiny_paths(path: pathops.Path, glyph_name, min_area: int = 25):
    """
    Removes tiny paths from a pathops.Path.

    :param path: the path from which to remove the tiny paths
    :param glyph_name: the glyph name
    :param min_area: the minimum are of a path to keep it
    :return: the cleaned path
    """
    cleaned_path = pathops.Path()
    for contour in path.contours:
        if contour.area >= min_area:
            cleaned_path.addPath(contour)
        else:
            logger.debug(f"Tiny path removed from glyph '{glyph_name}'")
    return cleaned_path


def correct_otf_contours(font: Font, min_area: int = 25) -> None:
    """
    Corrects the contours of an OTF font.

    :param font: the font
    :param min_area: the minimum area of a path
    :return: None
    """

    if not font.is_ps:
        raise NotImplementedError("Not an OTF font")

    cff_table: C_F_F_.table_C_F_F_ = font["CFF "]
    glyph_set = font.getGlyphSet()
    charstrings = {}
    modified = []

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(width=v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstrings[k] = t2_pen.getCharString()

        path_1 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = simplify_path(path=path_2, glyph_name=k, clockwise=False)

        if min_area > 0:
            path_2 = remove_tiny_paths(path=path_2, glyph_name=k, min_area=min_area)

        if not same_path(path_1=path_1, path_2=path_2):
            cs = t2_charstring_from_skia_path(path=path_2, width=v.width)
            logger.debug(f"Corrected contours for glyph '{k}'")
            charstrings[k] = cs
            modified.append(k)

    if not modified:
        logger.info("No glyphs modified")
        return

    ps_name = cff_table.cff.fontNames[0]
    font_info = {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }
    private_dict = {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].Private.rawDict.items()
        if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
    }
    fb = FontBuilder(font=font)
    fb.setupCFF(
        psName=ps_name, fontInfo=font_info, privateDict=private_dict, charStringsDict=charstrings
    )
