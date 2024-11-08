from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables import GlyfTable


def main(font: Font) -> None:
    """Decompose composite glyphs that have transformed components."""
    glyf = GlyfTable(ttfont=font.ttfont)
    transformed = glyf.decompose_transformed()
    if transformed:
        logger.info(
            f"Decomposed transformed components in the following glyphs: {', '.join(transformed)}"
        )
        font.is_modified = True
