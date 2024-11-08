from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_HMTX
from foundrytools_cli_2.lib.tables.default import DefaultTbl


class HmtxTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``hmtx`` table.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``GSUB`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_HMTX)

    def fix_non_breaking_space_width(self) -> None:
        """
        Fixes the width of the non-breaking space glyph to be the same as the space glyph.
        """
        best_cmap = self.ttfont.getBestCmap()
        space_glyph = best_cmap.get(0x0020)
        nbsp_glyph = best_cmap.get(0x00A0)
        if nbsp_glyph is None or space_glyph is None:
            raise ValueError("Both the space and non-breaking space glyphs must exist.")

        # Set the width of the non-breaking space glyph
        if self.table.metrics[nbsp_glyph] != self.table.metrics[space_glyph]:
            self.table.metrics[nbsp_glyph] = self.table.metrics[space_glyph]
