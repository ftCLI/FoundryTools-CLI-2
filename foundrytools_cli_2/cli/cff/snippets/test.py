from foundrytools_cli_2.lib.font.font import Font
from foundrytools_cli_2.lib.font.tables.cff_ import CFFTable


def main(font: Font) -> None:
    """
    Print the CFF table of a font.

    Args:
        font (Font): The font to analyze
    """
    cff_table = CFFTable(ttfont=font.ttfont)
    print(cff_table)
    font.modified = False
