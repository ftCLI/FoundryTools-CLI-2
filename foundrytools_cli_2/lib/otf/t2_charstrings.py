import typing as t
from copy import deepcopy

from fontTools.cffLib import PrivateDict
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.otf_builder import build_otf
from foundrytools_cli_2.lib.ttf.ttf_builder import build_ttf

__all__ = ["quadratics_to_cubics", "get_t2_charstrings"]


def quadratics_to_cubics(font: TTFont, tolerance: float = 1.0) -> t.Dict[str, T2CharString]:
    """
    Get CFF charstrings using Qu2CuPen

    Args:
        font (TTFont): The TTFont object.
        tolerance (float, optional): The tolerance for the conversion. Defaults to 1.0.

    Returns:
        tuple: A tuple containing the list of failed glyphs and the T2 charstrings.
    """

    qu2cu_charstrings = {}
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        width = v.width

        try:
            t2_pen = T2CharStringPen(width=width, glyphSet={k: v})
            qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
            glyph_set[k].draw(qu2cu_pen)
            qu2cu_charstrings[k] = t2_pen.getCharString()

        except NotImplementedError as e:
            t2_pen = T2CharStringPen(width=width, glyphSet={k: v})
            glyph_set[k].draw(t2_pen)
            t2_charstring = t2_pen.getCharString()
            t2_charstring.private = PrivateDict()

            tt_pen = TTGlyphPen(glyphSet=None)
            cu2qu_pen = Cu2QuPen(other_pen=tt_pen, max_err=tolerance, reverse_direction=False)
            t2_charstring.draw(cu2qu_pen)
            tt_glyph = tt_pen.glyph()

            t2_pen = T2CharStringPen(width=width, glyphSet=None)
            qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
            tt_glyph.draw(pen=qu2cu_pen, glyfTable=None)
            logger.info(f"{e}. Successfully got charstring for {k} at second attempt")

        qu2cu_charstrings[k] = t2_pen.getCharString()

    return qu2cu_charstrings


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
    fallback_charstrings = quadratics_to_cubics(temp_font, tolerance=tolerance)
    return fallback_charstrings
