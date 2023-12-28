from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def decomponentize(font: TTFont) -> None:
    """
    This method takes a TrueType font as input and decomposes all composite glyphs in the font.

    Parameters:
        font (TTFont): The TrueType font object to decompose.

    Returns:
    None
    """
    glyph_set = font.getGlyphSet()
    glyf_table = font["glyf"]
    dr_pen = DecomposingRecordingPen(glyph_set)
    tt_pen = TTGlyphPen(None)

    for glyph_name in font.glyphOrder:
        glyph = glyf_table[glyph_name]
        if not glyph.isComposite():
            continue
        dr_pen.value = []
        tt_pen.init()
        glyph.draw(dr_pen, glyf_table)
        dr_pen.replay(tt_pen)
        glyf_table[glyph_name] = tt_pen.glyph()
