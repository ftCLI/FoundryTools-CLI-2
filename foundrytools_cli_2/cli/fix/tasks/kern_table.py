from foundrytools_cli_2.lib.constants import T_KERN
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.kern import KernTable


def main(font: Font) -> None:
    """
    Fixes the missing non-breaking space glyph by double mapping the space glyph.
    """
    if T_KERN not in font.ttfont:
        return
    kern_table = KernTable(ttfont=font.ttfont)
    kern_table.remove_unmapped_glyphs()
    font.is_modified = kern_table.is_modified
