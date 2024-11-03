import typing as t

import defcon
import extractor

from foundrytools_cli_2.lib.font import Font


def create_new_glyph_order(
    font: Font,
    sort_method: t.Literal["unicode", "alphabetical", "cannedDesign"] = "unicode",
) -> t.List[str]:
    """
    Creates the new glyph order.
    """
    ufo = defcon.Font()
    extractor.extractUFO(
        font.file, destination=ufo, doFeatures=False, doInfo=False, doKerning=False
    )
    new_glyph_order = ufo.unicodeData.sortGlyphNames(
        glyphNames=font.ttfont.getGlyphOrder(),
        sortDescriptors=[{"type": sort_method}],
    )
    if ".notdef" in new_glyph_order:
        new_glyph_order.remove(".notdef")
        new_glyph_order.insert(0, ".notdef")

    return new_glyph_order


def main(
    font: Font,
    sort_method: t.Literal["unicode", "alphabetical", "cannedDesign"] = "unicode",
) -> None:
    """
    Reorders the glyphs based on the Unicode values.
    """

    original_glyph_order = font.ttfont.getGlyphOrder()
    new_glyph_order = create_new_glyph_order(font, sort_method=sort_method)
    if new_glyph_order == original_glyph_order:
        return
    font.sort_glyphs(new_glyph_order=new_glyph_order)
    font.is_modified = True
