import typing as t

import defcon
import extractor

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import CFFTable


def create_new_glyph_order(font: Font) -> t.List[str]:
    """
    Creates the new glyph order.
    """
    ufo = defcon.Font()
    extractor.extractUFO(
        font.file, destination=ufo, doFeatures=False, doInfo=False, doKerning=False
    )
    new_glyph_order = ufo.unicodeData.sortGlyphNames(glyphNames=font.ttfont.getGlyphOrder())
    if ".notdef" in new_glyph_order:
        new_glyph_order.remove(".notdef")
        new_glyph_order.insert(0, ".notdef")

    return new_glyph_order


def main(font: Font) -> None:
    """
    Reorders the glyphs based on the Unicode values.
    """

    ufo = defcon.Font()
    extractor.extractUFO(
        font.file, destination=ufo, doFeatures=False, doInfo=False, doKerning=False
    )
    original_glyph_order = font.ttfont.getGlyphOrder()
    new_glyph_order = create_new_glyph_order(font)
    font.ttfont.reorderGlyphs(new_glyph_order=new_glyph_order)
    font.ttfont.setGlyphOrder(new_glyph_order)

    if font.is_ps:
        cff_table = CFFTable(font.ttfont)
        charstrings = cff_table.charstrings.charStrings
        cff_table.top_dict.charset = new_glyph_order
        cff_table.charstrings.charStrings = {k: charstrings.get(k) for k in new_glyph_order}

    font.modified = new_glyph_order != original_glyph_order
