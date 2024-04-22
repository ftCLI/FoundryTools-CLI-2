import typing as t

from foundrytools_cli_2.lib.font import Font


def create_new_glyph_order(font: Font) -> t.List[str]:
    """
    Creates the new glyph order.
    """
    new_glyph_order: t.List[str] = []
    encoded_glyphs = list(font.ttfont.getBestCmap().values())
    unencoded_glyphs = [
        glyph_name for glyph_name in font.ttfont.getGlyphOrder() if glyph_name not in encoded_glyphs
    ]

    if ".notdef" in unencoded_glyphs:
        new_glyph_order.extend([".notdef"])
        unencoded_glyphs.remove(".notdef")

    # Add support for other ordering methods
    new_glyph_order.extend(sorted(encoded_glyphs))
    new_glyph_order.extend(sorted(unencoded_glyphs))

    return new_glyph_order


def main(font: Font) -> None:
    """
    Reorders the glyphs
    """
    new_glyph_order = create_new_glyph_order(font)
    font.ttfont.reorderGlyphs(new_glyph_order=new_glyph_order)
    font.modified = True
