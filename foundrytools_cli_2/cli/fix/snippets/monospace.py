from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import CFFTable, HheaTable, OS2Table, PostTable
from foundrytools_cli_2.lib.utils.misc import get_glyph_metrics_stats


def main(font: Font) -> None:
    """
    Fix the monospace attribute of a font.

    Args:
        font (Font): The font to fix.
    """
    glyph_metrics = get_glyph_metrics_stats(font.ttfont)
    seems_monospaced = glyph_metrics["seems_monospaced"]
    width_max = glyph_metrics["width_max"]
    post_table = PostTable(ttfont=font.ttfont)
    os2_table = OS2Table(ttfont=font.ttfont)
    hhea_table = HheaTable(ttfont=font.ttfont)

    if seems_monospaced:
        post_table.fixed_pitch = True
        os2_table.table.panose.bFamilyType = 2
        os2_table.table.panose.bProportion = 9
        hhea_table.advance_width_max = width_max

        modified = os2_table.modified or post_table.modified or hhea_table.modified

        if font.is_ps:
            cff_table = CFFTable(ttfont=font.ttfont)
            cff_table.top_dict.isFixedPitch = True
            modified = cff_table.modified or modified

        font.modified = modified
