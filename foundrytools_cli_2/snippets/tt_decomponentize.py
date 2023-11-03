from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

from foundrytools_cli_2.lib.font import Font


def decomponentize(font: Font) -> None:
    """
    Decomponentize a TrueType font.
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
