from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables.cmap import CmapTable


def fix_missing_nbsp(font: Font) -> None:
    """
    Fixes the missing non-breaking space glyph by double mapping the space glyph.
    """
    cmap_table = CmapTable(ttfont=font.ttfont)
    cmap_table.add_missing_non_breaking_space()
    font.modified = cmap_table.modified
