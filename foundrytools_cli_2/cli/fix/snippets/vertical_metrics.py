from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import HheaTable, OS2Table


def main(font: Font, safe_bottom: int, safe_top: int) -> None:
    """
    Adjusts the vertical metrics of a font to ensure consistency across the family.

    Args:
        font (Font): The font object to be modified.
        safe_bottom (int): The safe bottom value for the font's vertical metrics.
        safe_top (int): The safe top value for the font's vertical metrics.
    """

    os_table = OS2Table(font.ttfont)
    hhea_table = HheaTable(font.ttfont)

    os_table.win_ascent = safe_top
    os_table.win_descent = abs(safe_bottom)
    os_table.typo_ascender = safe_top
    os_table.typo_descender = safe_bottom
    os_table.typo_line_gap = 0
    hhea_table.ascent = safe_top
    hhea_table.descent = safe_bottom
    hhea_table.line_gap = 0

    # Set the USE_TYPO_METRICS bit
    if os_table.version >= 4:
        os_table.fs_selection.use_typo_metrics = True

    font.modified = os_table.modified or hhea_table.modified
