import typing as t

import pathops
from fontTools.cffLib import CFFFontSet, PrivateDict
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttGlyphSet import _TTGlyph

from foundrytools_cli_2.lib.skia.skia_tools import _simplify

__all__ = ["quadratics_to_cubics", "quadratics_to_cubics_2", "round_coordinates"]


_TTGlyphMapping = t.Mapping[str, _TTGlyph]


def _skia_path_from_charstring(charstring: T2CharString) -> pathops.Path:
    """
    Get a Skia path from a T2CharString.
    """
    path = pathops.Path()
    path_pen = path.getPen(glyphSet=None)
    charstring.draw(path_pen)
    return path


def _charstring_from_skia_path(path: pathops.Path, width: int) -> T2CharString:
    """
    Get a T2CharString from a Skia path.
    """
    t2_pen = T2CharStringPen(width=width, glyphSet=None)
    path.draw(t2_pen)
    return t2_pen.getCharString()


def quadratics_to_cubics(
    font: TTFont, tolerance: float = 1.0, correct_contours: bool = True
) -> t.Dict[str, T2CharString]:
    """
    Get CFF charstrings using Qu2CuPen

    Args:
        font (TTFont): The TTFont object.
        tolerance (float, optional): The tolerance for the conversion. Defaults to 1.0.
        correct_contours (bool, optional): Whether to correct the contours with pathops. Defaults to
            False.

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

        except NotImplementedError:
            temp_t2_pen = T2CharStringPen(width=width, glyphSet=None)
            glyph_set[k].draw(temp_t2_pen)
            t2_charstring = temp_t2_pen.getCharString()
            t2_charstring.private = PrivateDict()

            tt_pen = TTGlyphPen(glyphSet=None)
            cu2qu_pen = Cu2QuPen(other_pen=tt_pen, max_err=tolerance, reverse_direction=False)
            t2_charstring.draw(cu2qu_pen)
            tt_glyph = tt_pen.glyph()

            t2_pen = T2CharStringPen(width=width, glyphSet=None)
            qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
            tt_glyph.draw(pen=qu2cu_pen, glyfTable=None)

        charstring = t2_pen.getCharString()

        if correct_contours:
            charstring.private = PrivateDict()
            path = _skia_path_from_charstring(charstring)
            simplified_path = _simplify(path, glyph_name=k, clockwise=False)
            charstring = _charstring_from_skia_path(path=simplified_path, width=width)

        qu2cu_charstrings[k] = charstring

    return qu2cu_charstrings


def quadratics_to_cubics_2(font: TTFont) -> t.Dict[str, T2CharString]:
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


def round_coordinates(font: TTFont) -> None:
    """
    Round the coordinates of the glyphs in a font.

    Args:
        font (TTFont): The font to round the coordinates of.
    """
    glyph_names: t.List[str] = font.getGlyphOrder()
    glyph_set: _TTGlyphMapping = font.getGlyphSet()
    cff_font_set: CFFFontSet = font["CFF "].cff
    charstrings = cff_font_set[0].CharStrings

    for glyph_name in glyph_names:
        charstring = charstrings[glyph_name]

        glyph_width = glyph_set[glyph_name].width
        if glyph_width == charstring.private.defaultWidthX:
            width = None
        else:
            width = glyph_width - charstring.private.nominalWidthX

        t2_pen = T2CharStringPen(width=width, glyphSet=glyph_set)
        rounding_pen = RoundingPen(outPen=t2_pen)
        glyph_set[glyph_name].draw(rounding_pen)
        rounded_charstring = t2_pen.getCharString(private=charstring.private)
        charstrings[glyph_name] = rounded_charstring
