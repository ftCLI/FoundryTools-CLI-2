import typing as t

import defcon
import extractor

from foundrytools_cli_2.lib.font import Font


def create_new_glyph_order(font: Font) -> t.List[str]:
    """
    Creates the new glyph order.
    """
    ufo = defcon.Font()
    extractor.extractUFO(
        font.file, destination=ufo, doFeatures=False, doInfo=False, doKerning=False
    )
    new_glyph_order = ufo.unicodeData.sortGlyphNames(
        glyphNames=font.ttfont.getGlyphOrder(),
        sortDescriptors=[dict(type="unicode")],
    )
    if ".notdef" in new_glyph_order:
        new_glyph_order.remove(".notdef")
        new_glyph_order.insert(0, ".notdef")

    return new_glyph_order


def main(font: Font) -> None:
    """
    Reorders the glyphs based on the Unicode values.
    """

    original_glyph_order = font.ttfont.getGlyphOrder()
    new_glyph_order = create_new_glyph_order(font)
    if new_glyph_order == original_glyph_order:
        return
    font.sort_glyphs(new_glyph_order=new_glyph_order)
    font.modified = True
