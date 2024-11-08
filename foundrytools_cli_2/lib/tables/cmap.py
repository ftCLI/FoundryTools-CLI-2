import typing as t

from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CMAP
from foundrytools_cli_2.lib.tables.default import DefaultTbl


class CmapTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``cmap`` table.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``cmap`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_CMAP)

    def get_codepoints(self) -> t.Set[int]:
        """
        Returns all the codepoints in the cmap table.
        """
        codepoints = set()
        for table in self.table.tables:
            if table.isUnicode():
                codepoints.update(table.cmap.keys())
        return codepoints

    def add_missing_nbsp(self) -> None:
        """
        Fixes the missing non-breaking space glyph by double mapping the space glyph.
        """
        # Get the space glyph
        best_cmap = self.table.getBestCmap()
        space_glyph = best_cmap.get(0x0020)
        if space_glyph is None:
            return

        # Get the non-breaking space glyph
        nbsp_glyph = best_cmap.get(0x00A0)
        if nbsp_glyph is not None:
            return

        # Copy the space glyph to the non-breaking space glyph
        for table in self.table.tables:
            if table.isUnicode():
                table.cmap[0x00A0] = space_glyph
