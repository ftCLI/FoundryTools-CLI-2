from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(font: Font, recalc_timestamp: bool = False) -> None:
    """
    Removes unreachable glyphs from the font.
    Args:
        font: The font to remove the unreachable glyphs from.
        recalc_timestamp: Whether to recalculate the font's timestamp.

    Returns:
        None
    """
    removed_glyphs = font.remove_unused_glyphs(recalc_timestamp=recalc_timestamp)

    if removed_glyphs:
        logger.info(f"Removed {len(removed_glyphs)} unreachable glyphs")
        font.is_modified = True
