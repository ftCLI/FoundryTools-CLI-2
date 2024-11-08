from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.cmap import CmapTable


def main(font: Font) -> None:
    """
    Fixes the missing non-breaking space glyph by double mapping the space glyph.
    """
    cmap_table = CmapTable(ttfont=font.ttfont)
    cmap_table.add_missing_nbsp()
    font.is_modified = cmap_table.is_modified
