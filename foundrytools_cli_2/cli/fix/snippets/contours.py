from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(
    font: Font,
    min_area: int = 25,
    remove_hinting: bool = True,
    ignore_errors: bool = False,
    remove_unused_subroutines: bool = True,
) -> None:
    """
    Corrects contours of the given TrueType font by removing overlaps, correcting the direction of
    the contours, and removing tiny paths.

    Args:
        font (Font): The font to correct
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.
        remove_hinting (bool, optional): Whether to remove hinting from the font. Defaults to True.
        ignore_errors (bool, optional): Whether to ignore errors while correcting contours. Defaults
            to False.
        remove_unused_subroutines (bool, optional): Whether to remove unused subroutines from the
            font. Defaults to True.
    """
    logger.info("Correcting contours...")
    modified_glyphs = font.correct_contours(
        min_area=min_area,
        remove_hinting=remove_hinting,
        ignore_errors=ignore_errors,
        remove_unused_subroutines=remove_unused_subroutines,
    )

    if not modified_glyphs:
        logger.info("No glyphs were modified")
        return

    font.modified = True
    logger.info(f"{len(modified_glyphs)} glyphs were modified: {', '.join(modified_glyphs)}")
