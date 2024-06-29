from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CMAP
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class CmapTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``cmap`` table.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``cmap`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_CMAP)

    def rebuild_tables(self) -> None:
        """
        Rebuild the ``cmap`` table.
        """
        self.ttfont.getBestCmap()
        self.ttfont.getReverseGlyphMap()
