import typing as t
from copy import deepcopy

from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.otf_builder import build_otf
from foundrytools_cli_2.lib.ttf.ttf_builder import build_ttf

__all__ = ["quadratics_to_cubics", "get_t2_charstrings"]


def quadratics_to_cubics(font: TTFont, tolerance: float = 1.0) -> t.Dict[str, T2CharString]:
    """
    Get CFF charstrings using Qu2CuPen, falling back to T2CharStringPen if Qu2CuPen fails.

    Args:
        font (TTFont): The TTFont object.
        tolerance (float, optional): The tolerance for the conversion. Defaults to 1.0.

    Returns:
        dict: The T2 charstrings.
    """

    charstrings: t.Dict = {}
    try:
        tolerance = tolerance / 1000 * font["head"].unitsPerEm
        failed, charstrings = get_qu2cu_charstrings(font, tolerance=tolerance)

        if len(failed) > 0:
            logger.info(f"Retrying to get {len(failed)} charstrings...")
            fallback_charstrings = get_fallback_charstrings(font, tolerance=tolerance)

            for c in failed:
                try:
                    charstrings[c] = fallback_charstrings[c]
                    logger.info(f"Successfully got charstring for {c}")
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"Failed to get charstring for {c}: {e}")

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Failed to get charstrings: {e}")

    return charstrings


def get_qu2cu_charstrings(
    font: TTFont, tolerance: float = 1.0
) -> t.Tuple[t.List[str], t.Dict[str, T2CharString]]:
    """
    Get CFF charstrings using Qu2CuPen

    Args:
        font (TTFont): The TTFont object.
        tolerance (float, optional): The tolerance for the conversion. Defaults to 1.0.

    Returns:
        tuple: A tuple containing the list of failed glyphs and the T2 charstrings.
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
            logger.error(f"Failed to get charstring for {k}: {e}")
            failed.append(k)

    return failed, qu2cu_charstrings


def get_t2_charstrings(font: TTFont) -> t.Dict[str, T2CharString]:
    """
    Get CFF charstrings using T2CharStringPen

    Args:
        font (TTFont): The TTFont object.

    Returns:
        dict: The T2 charstrings.
    """
    t2_charstrings = {}
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstring = t2_pen.getCharString()
        t2_charstrings[k] = charstring

    return t2_charstrings


def get_fallback_charstrings(font: TTFont, tolerance: float = 1.0) -> t.Dict[str, T2CharString]:
    """
    Get the charstrings from a fallback OTF font.

    Args:
        font (TTFont): The TTFont object.
        tolerance (float, optional): The tolerance for the conversion. Defaults to 1.0.

    Returns:
        dict: The fallback charstrings.
    """
    temp_font = deepcopy(font)
    t2_charstrings = get_t2_charstrings(font=temp_font)
    build_otf(font=temp_font, charstrings_dict=t2_charstrings)
    build_ttf(font=temp_font, max_err=tolerance, reverse_direction=False)
    _, fallback_charstrings = get_qu2cu_charstrings(temp_font, tolerance=tolerance)
    return fallback_charstrings
