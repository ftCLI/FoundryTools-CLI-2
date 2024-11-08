from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CMAP, T_KERN
from foundrytools_cli_2.lib.tables.default import DefaultTbl


class KernTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``kern` table.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``GSUB`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_KERN)

    def remove_unmapped_glyphs(self) -> None:
        """
        Removes unmapped glyphs from the ``kern`` table.
        """
        if all(kernTable.format != 0 for kernTable in self.table.kernTables):
            return

        character_glyphs = set()
        for table in self.ttfont[T_CMAP].tables:
            character_glyphs.update(table.cmap.values())

        for table in self.table.kernTables:
            if table.format == 0:
                pairs_to_delete = []
                for left_glyph, right_glyph in table.kernTable:
                    if left_glyph not in character_glyphs or right_glyph not in character_glyphs:
                        pairs_to_delete.append((left_glyph, right_glyph))
                if pairs_to_delete:
                    for pair in pairs_to_delete:
                        del table.kernTable[pair]
