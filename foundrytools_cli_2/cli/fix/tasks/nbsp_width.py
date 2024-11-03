from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables.hmtx import HmtxTable


def main(font: Font) -> None:
    """
    Fixes the width of the non-breaking space glyph to be the same as the space glyph.
    """
    hmtx_table = HmtxTable(ttfont=font.ttfont)
    hmtx_table.fix_non_breaking_space_width()
    font.is_modified = hmtx_table.is_modified
