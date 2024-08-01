import typing as t

import pathops
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_FPGM, T_GLYF
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class GlyfTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``glyf`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``glyf`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_GLYF)

    def decompose_glyph(self, glyph_name: str) -> None:
        """
        Decompose the glyph components of a given glyph name.

        Args:
            glyph_name (str): The glyph name to decompose.
        """
        glyph_set = self.ttfont.getGlyphSet()
        dc_pen = DecomposingRecordingPen(glyph_set)
        glyph_set[glyph_name].draw(dc_pen)

        path = pathops.Path()
        path_pen = path.getPen()
        dc_pen.replay(path_pen)

        path.simplify()

        tt_pen = TTGlyphPen(None)
        path.draw(tt_pen)
        self.table[glyph_name] = tt_pen.glyph()

    def decompose_transformed(self) -> t.Set[str]:
        """
        Decompose composite glyphs that have transformed components.
        """
        decomposed_glyphs = set()
        for glyph_name in self.ttfont.getGlyphOrder():
            decompose = False
            glyph = self.table[glyph_name]
            if not glyph.isComposite():
                continue
            for component in glyph.components:
                _, transform = component.getComponentInfo()

                # Font is hinted, decompose glyphs with *any* transformations
                if T_FPGM in self.ttfont:
                    if transform[0:4] != (1, 0, 0, 1):
                        decompose = True
                # Font is unhinted, decompose only glyphs with transformations where only one
                # dimension is flipped while the other isn't. Otherwise the outline direction
                # is intact and since the font is unhinted, no rendering problems are to be
                # expected
                else:
                    if transform[0] * transform[3] < 0:
                        decompose = True

            if decompose:
                self.decompose_glyph(glyph_name)
                decomposed_glyphs.add(glyph_name)

        return decomposed_glyphs
