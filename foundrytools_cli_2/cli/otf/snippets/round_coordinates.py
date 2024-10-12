from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables.cff_ import CFFTable
from foundrytools_cli_2.lib.otf.otf_builder import build_otf


def main(font: Font, subroutinize: bool = True) -> None:
    """
    Round the coordinates of the glyphs in a font.

    Args:
        font (Font): The font to round the coordinates of.
        subroutinize (bool): Whether to subroutinize the font.
    """

    glyph_set = font.glyph_set
    cff = CFFTable(font.ttfont)
    private = cff.top_dict.Private

    rounded_charstrings = {}

    for glyph_name, glyph in glyph_set.items():
        t2_pen = T2CharStringPen(width=glyph.width, glyphSet=glyph_set)
        rounding_pen = RoundingPen(outPen=t2_pen)
        glyph_set[glyph_name].draw(rounding_pen)
        rounded_charstring = t2_pen.getCharString(private=private)
        rounded_charstrings[glyph_name] = rounded_charstring

    build_otf(font=font.ttfont, charstrings_dict=rounded_charstrings)

    if subroutinize:
        font.ps_subroutinize()
    else:
        font.ps_desubroutinize()
    font.modified = True
