import typing as t
from copy import deepcopy

from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.pathops.skia_tools import (
    skia_path_from_glyph,
    simplify_path,
    remove_tiny_paths,
    same_path,
    t2_charstring_from_skia_path,
)

from foundrytools_cli_2.lib.font_builder.font_builder_tools import build_otf
from foundrytools_cli_2.lib.ttf.from_otf import build_ttf


def from_true_type(font: TTFont, tolerance: float = 1.0) -> t.Dict:
    """
    Get CFF charstrings using Qu2CuPen, falling back to T2CharStringPen if Qu2CuPen fails.

    :return: CFF charstrings.
    """

    charstrings: t.Dict = {}
    try:
        tolerance = tolerance / 1000 * font["head"].unitsPerEm
        failed, charstrings = get_qu2cu_charstrings(font, tolerance=tolerance)

        if len(failed) > 0:
            logger.debug(f"Retrying to get {len(failed)} charstrings...")
            fallback_charstrings = get_fallback_charstrings(font, tolerance=tolerance)

            for c in failed:
                try:
                    charstrings[c] = fallback_charstrings[c]
                    logger.debug(f"Successfully got charstring for {c}")
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"Failed to get charstring for {c}: {e}")

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Failed to get charstrings: {e}")

    return charstrings


def get_qu2cu_charstrings(font: TTFont, tolerance: float = 1.0) -> t.Tuple[t.List, t.Dict]:
    """
    Get CFF charstrings using Qu2CuPen

    :return: CFF charstrings.
    """

    qu2cu_charstrings = {}
    failed = []
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
        try:
            glyph_set[k].draw(qu2cu_pen)
            qu2cu_charstrings[k] = t2_pen.getCharString()
        except NotImplementedError as e:
            logger.debug(f"Failed to get charstring for {k}: {e}")
            failed.append(k)

    return failed, qu2cu_charstrings


def get_t2_charstrings(font: TTFont) -> dict:
    """
    Get CFF charstrings using T2CharStringPen

    :return: CFF charstrings.
    """
    t2_charstrings = {}
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstring = t2_pen.getCharString()
        t2_charstrings[k] = charstring

    return t2_charstrings


def get_fallback_charstrings(font: TTFont, tolerance: float = 1.0) -> dict:
    """
    Get the charstrings from a fallback OTF font.
    """
    temp_font = deepcopy(font)
    t2_charstrings = get_t2_charstrings(font=temp_font)
    build_otf(font=temp_font, charstrings_dict=t2_charstrings)
    build_ttf(font=temp_font, max_err=tolerance, reverse_direction=False)
    _, fallback_charstrings = get_qu2cu_charstrings(temp_font, tolerance=tolerance)
    return fallback_charstrings


def fix_charstrings(
    font: TTFont, min_area: int = 25
) -> t.Tuple[t.Dict[str, T2CharString], t.List[str]]:
    """
    Get CFF charstrings using T2CharStringPen

    :return: CFF charstrings.
    """

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
            charstrings[k] = cs
            modified.append(k)

    return charstrings, modified
