from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables import GlyfTable


def main(font: Font) -> None:
    """Decompose composite glyphs that have transformed components."""
    glyf = GlyfTable(ttfont=font.ttfont)
    fixed_glyphs = glyf.remove_duplicate_components()
    if fixed_glyphs:
        logger.info(
            f"Removed duplicate components in the following glyphs: {', '.join(fixed_glyphs)}"
        )
        font.is_modified = True
