import itertools
import typing as t

import pathops
from fontTools.cffLib import CFFFontSet
from fontTools.misc.psCharStrings import T2CharString
from fontTools.misc.roundTools import noRound, otRound
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import _g_l_y_f, _h_m_t_x
from fontTools.ttLib.ttGlyphSet import _TTGlyph

from foundrytools_cli_2.lib.constants import T_CFF, T_GLYF, T_HMTX

_TTGlyphMapping = t.Mapping[str, _TTGlyph]


class CorrectContoursError(Exception):
    """Raised when an error occurs while correcting the contours of a TrueType font."""


def skia_path_from_glyph(glyph_name: str, glyph_set: _TTGlyphMapping) -> pathops.Path:
    """
    Returns a pathops.Path from a glyph.

    Args:
        glyph_name (str): The glyph name.
        glyph_set (_TTGlyphMapping): The glyph set to which the glyph belongs.

    Returns:
        pathops.Path: The pathops.Path object.
    """

    path = pathops.Path()
    pen = path.getPen(glyphSet=glyph_set)
    glyph_set[glyph_name].draw(pen)
    return path


def skia_path_from_glyph_component(
    component: _g_l_y_f.GlyphComponent, glyph_set: _TTGlyphMapping
) -> pathops.Path:
    """
    Returns a ``pathops.Path`` from a glyph component.

    Args:
        component (_g_l_y_f.GlyphComponent): The glyph component.
        glyph_set (_TTGlyphMapping): The glyph set to which the glyph belongs.

    Returns:
        pathops.Path: The ``pathops.Path`` object.
    """

    base_glyph_name, transformation = component.getComponentInfo()
    path = skia_path_from_glyph(glyph_name=base_glyph_name, glyph_set=glyph_set)
    return path.transform(*transformation)


def ttf_components_overlap(glyph: _g_l_y_f.Glyph, glyph_set: _TTGlyphMapping) -> bool:
    """
    Checks if a TrueType composite glyph has overlapping components.

    Args:
        glyph (_g_l_y_f.Glyph): The glyph to check.
        glyph_set (_TTGlyphMapping): The glyph set to which the glyph belongs.

    Returns:
        bool: ``True`` if the glyph has overlapping components, ``False`` otherwise.
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
        )
        for i, j in itertools.combinations(range(len(glyph.components)), 2)
    )


def tt_glyph_from_skia_path(path: pathops.Path) -> _g_l_y_f.Glyph:
    """
    Returns a TrueType glyph from a ``pathops.Path``

    Args:
        path (pathops.Path): The ``pathops.Path``

    Returns:
        _g_l_y_f.Glyph: The TrueType glyph
    """

    tt_pen = TTGlyphPen(glyphSet=None)
    path.draw(tt_pen)
    glyph = tt_pen.glyph()
    glyph.recalcBounds(glyfTable=None)
    return glyph


def t2_charstring_from_skia_path(
    path: pathops.Path,
    charstring: T2CharString,
) -> T2CharString:
    """
    Returns a ``T2CharString`` from a ``pathops.Path``

    Args:
        path (pathops.Path): The ``pathops.Path``
        charstring (T2CharString): The original ``T2CharString``

    Returns:
        T2CharString: The ``T2CharString`` object
    """

    # https://github.com/fonttools/fonttools/commit/40b525c1e3cc20b4b64004b8e3224a67adc2adf1
    # The width argument of `T2CharStringPen()` is inserted directly into the CharString
    # program, so it must be relative to Private.nominalWidthX.
    if charstring.width == charstring.private.defaultWidthX:
        width = None
    else:
        width = charstring.width - charstring.private.nominalWidthX

    t2_pen = T2CharStringPen(width=width, glyphSet=None)
    path.draw(t2_pen)
    charstring = t2_pen.getCharString(charstring.private, charstring.globalSubrs)
    return charstring


def _round_path(path: pathops.Path, rounder: t.Callable[[float], float] = otRound) -> pathops.Path:
    """
    Rounds the points coordinate of a ``pathops.Path``

    Args:
        path (pathops.Path): The ``pathops.Path``
        rounder (Callable[[float], float], optional): The rounding function. Defaults to otRound.

    Returns:
        pathops.Path: The rounded path
    """

    rounded_path = pathops.Path()
    for verb, points in path:
        rounded_path.add(verb, *((rounder(p[0]), rounder(p[1])) for p in points))
    return rounded_path


def _simplify(path: pathops.Path, glyph_name: str, clockwise: bool) -> pathops.Path:
    """
    Simplify a ``pathops.Path`` by removing overlaps, fixing contours direction and, optionally,
    removing tiny paths

    Args:
        path (pathops.Path): The ``pathops.Path`` to simplify
        glyph_name (str): The glyph name
        clockwise (bool): The winding direction. Must be ``True`` for TrueType glyphs and ``False``
            for OpenType-PS fonts.

    Returns:
        pathops.Path: The simplified path
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

    path = _round_path(path, rounder=noRound)
    try:
        path = pathops.simplify(path, fix_winding=True, clockwise=clockwise)
        return path
    except pathops.PathOpsError as e:
        raise CorrectContoursError(f"Failed to remove overlaps from glyph {glyph_name!r}") from e


def _same_path(path_1: pathops.Path, path_2: pathops.Path) -> bool:
    """
    Checks if two pathops paths are the same

    Args:
        path_1 (pathops.Path): The first path
        path_2 (pathops.Path): The second path

    Returns:
        bool: ``True`` if the paths are the same, ``False`` if the paths are different
    """

    return {tuple(c) for c in path_1.contours} == {tuple(c) for c in path_2.contours}


def remove_tiny_paths(path: pathops.Path, min_area: int = 25) -> pathops.Path:
    """
    Removes tiny paths from a ``pathops.Path``.

    Args:
        path (pathops.Path): The ``pathops.Path``
        min_area (int, optional): The minimum area of a contour to be retained. Defaults to 25.
    """

    cleaned_path = pathops.Path()
    for contour in path.contours:
        if contour.area >= min_area:
            cleaned_path.addPath(contour)
    return cleaned_path


def correct_tt_glyph_contours(
    glyph_name: str,
    glyph_set: _TTGlyphMapping,
    glyf_table: _g_l_y_f.table__g_l_y_f,
    hmtx_table: _h_m_t_x.table__h_m_t_x,
    remove_hinting: bool = True,
    min_area: int = 25,
) -> bool:
    """
    Corrects the contours of a TrueType glyph by removing overlaps, correcting the direction of the
    contours, and removing tiny paths.

    Args:
        glyph_name (str): The name of the glyph.
        glyph_set (_TTGlyphMapping): The glyph set to which the glyph belongs.
        glyf_table (_g_l_y_f.table__g_l_y_f): The glyf table of the font.
        hmtx_table (_h_m_t_x.table__h_m_t_x): The hmtx table of the font.
        remove_hinting (bool, optional): Whether to remove hinting instructions. Defaults to True.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.

    Returns:
        bool: True if the glyph was modified, False otherwise.
    """

    glyph: _g_l_y_f.Glyph = glyf_table[glyph_name]
    # decompose composite glyphs only if components overlap each other
    if (
        glyph.numberOfContours > 0
        or glyph.isComposite()
        and ttf_components_overlap(glyph=glyph, glyph_set=glyph_set)
    ):
        path = skia_path_from_glyph(glyph_name, glyph_set)
        path_2 = _simplify(path, glyph_name, clockwise=True)
        if min_area > 0:
            path_2 = remove_tiny_paths(path_2, min_area=min_area)

        if not _same_path(path_1=path, path_2=path_2):
            glyf_table[glyph_name] = glyph = tt_glyph_from_skia_path(path_2)
            width, lsb = hmtx_table[glyph_name]
            if lsb != glyph.xMin:
                hmtx_table[glyph_name] = (width, glyph.xMin)
            return True

    if remove_hinting:
        glyph.removeHinting()
    return False


def _correct_glyf_contours(
    font: TTFont,
    glyph_names: t.Iterable[str],
    glyph_set: _TTGlyphMapping,
    remove_hinting: bool,
    ignore_errors: bool,
    min_area: int = 25,
) -> t.Set[str]:
    """
    Corrects the contours of the given TrueType font by removing overlaps, correcting the direction
    of the contours, and removing tiny paths.

    Args:
        font (TTFont): The font object to be corrected.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.

    Returns:
        List[str]: The list of modified glyphs.
    """
    glyf_table = font[T_GLYF]
    hmtx_table = font[T_HMTX]

    # process all simple glyphs first, then composites with increasing component depth,
    # so that by the time we test for component intersections the respective base glyphs
    # have already been simplified
    glyph_names = sorted(
        glyph_names,
        key=lambda name: (
            (
                glyf_table[name].getCompositeMaxpValues(glyf_table).maxComponentDepth
                if glyf_table[name].isComposite()
                else 0
            ),
            name,
        ),
    )
    modified_glyphs = set()
    for glyph_name in glyph_names:
        try:
            if correct_tt_glyph_contours(
                glyph_name=glyph_name,
                glyph_set=glyph_set,
                glyf_table=glyf_table,
                hmtx_table=hmtx_table,
                remove_hinting=remove_hinting,
                min_area=min_area,
            ):
                modified_glyphs.add(glyph_name)
        except CorrectContoursError as e:
            if not ignore_errors:
                raise e

    return modified_glyphs


def _correct_charstring_contours(
    glyph_name: str,
    glyph_set: _TTGlyphMapping,
    cff_font_set: CFFFontSet,
    min_area: int = 25,
) -> bool:
    path = skia_path_from_glyph(glyph_name, glyph_set)
    path_2 = _simplify(path, glyph_name, clockwise=False)

    if min_area > 0:
        path_2 = remove_tiny_paths(path_2, min_area=min_area)

    if not _same_path(path_1=path, path_2=path_2):
        charstrings = cff_font_set[0].CharStrings
        charstrings[glyph_name] = t2_charstring_from_skia_path(path_2, charstrings[glyph_name])
        return True

    return False


def _correct_cff_contours(
    font: TTFont,
    glyph_names: t.Iterable[str],
    glyph_set: _TTGlyphMapping,
    remove_hinting: bool,
    ignore_errors: bool,
    remove_unused_subroutines: bool = True,
    min_area: int = 25,
) -> t.Set[str]:
    """
    Corrects the contours of the given OpenType-PS font by removing overlaps, correcting the
    direction of the contours, and removing tiny paths.

    Args:
        font (TTFont): The font object to be corrected.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.

    Returns:
        Tuple[Dict[str, T2CharString], List[str]]: The corrected charstrings dict and the list of
            modified glyphs.
    """
    cff_font_set: CFFFontSet = font[T_CFF].cff
    modified_glyphs = set()

    for glyph_name in glyph_names:
        try:
            if _correct_charstring_contours(
                glyph_name=glyph_name,
                glyph_set=glyph_set,
                cff_font_set=cff_font_set,
                min_area=min_area,
            ):
                modified_glyphs.add(glyph_name)
        except CorrectContoursError as e:
            if not ignore_errors:
                raise e

    if not modified_glyphs:
        return set()

    if remove_hinting:
        cff_font_set.remove_hints()

    if remove_unused_subroutines:
        cff_font_set.remove_unused_subroutines()

    return modified_glyphs


def correct_glyphs_contours(
    font: TTFont,
    remove_hinting: bool = True,
    ignore_errors: bool = False,
    remove_unused_subroutines: bool = True,
    min_area: int = 25,
) -> t.Set[str]:
    """
    Corrects the contours of the given font by removing overlaps, correcting the direction of the
    contours, and removing tiny paths.

    Args:
        font (TTFont): The font object to be corrected.
        remove_hinting (bool, optional): Whether to remove hinting instructions. Defaults to True.
        ignore_errors (bool, optional): Whether to ignore errors while correcting contours. Defaults
            to False.
        remove_unused_subroutines (bool, optional): Whether to remove unused subroutines from the
            font. Defaults to True.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.

    Returns:
        Set[str]: The set of modified glyphs.
    """
    if T_GLYF not in font and T_CFF not in font:
        raise NotImplementedError(
            "No outline data found in the font: missing 'glyf' or 'CFF ' table"
        )

    glyph_names = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()

    if T_GLYF in font:
        modified_glyphs = _correct_glyf_contours(
            font=font,
            glyph_names=glyph_names,
            glyph_set=glyph_set,
            remove_hinting=remove_hinting,
            ignore_errors=ignore_errors,
            min_area=min_area,
        )
    else:
        modified_glyphs = _correct_cff_contours(
            font=font,
            glyph_names=glyph_names,
            glyph_set=glyph_set,
            remove_hinting=remove_hinting,
            ignore_errors=ignore_errors,
            remove_unused_subroutines=remove_unused_subroutines,
            min_area=min_area,
        )

    return modified_glyphs
