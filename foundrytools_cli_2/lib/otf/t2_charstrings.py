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
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
        try:
            glyph_set[k].draw(qu2cu_pen)
            # qu2cu_charstrings[k] = t2_pen.getCharString()
        except NotImplementedError as e:
            # Draw the glyph with the T2CharStringPen as first step
            glyph_set[k].draw(t2_pen)

            # We have to initialize a PrivateDict object to pass it to the T2CharString,
            # otherwise it will raise an exception when drawing the charstring with the Cu2QuPen
            private = PrivateDict()
            t2_charstring = t2_pen.getCharString(private=private)

            # Initialize a TTGlyphPen object with the T2CharString object
            tt_pen = TTGlyphPen(glyphSet={k: t2_charstring})

            # Initialize a Cu2QuPen object with the TTGlyphPen object, the max error and the
            # reverse_direction=False to keep the original direction of the contours.
            # Since the T2CharStringPen doesn't reverse the direction of the contours, we're still
            # keeping the original direction of the contours.
            cu2qu_pen = Cu2QuPen(tt_pen, max_err=tolerance, reverse_direction=False)

            # Draw the T2CharString object with the Cu2QuPen, converting the contours to quadratic
            t2_charstring.draw(cu2qu_pen)
            tt_glyph = tt_pen.glyph()
            # At this point, whe have a new quadratic glyph (a fontTools.ttLib.tables._g_l_y_f.Glyph
            # object) that we have to convert back to cubic with the Qu2CuPen

            # Draw the quadratic glyph with the Qu2CuPen
            t2_pen = T2CharStringPen(v.width, glyphSet={k: tt_glyph})
            qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
            tt_glyph.draw(qu2cu_pen, None)
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
