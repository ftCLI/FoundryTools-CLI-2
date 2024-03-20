from dehinter.font import dehint

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def main(font: Font, min_area: int = 25, remove_hinting: bool = True) -> None:
    """
    Corrects contours of the given TrueType font by removing overlaps, correcting the direction of
    the contours, and removing tiny paths.

    Args:
        font (Font): The font to correct
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.
        remove_hinting (bool, optional): Whether to remove hinting from the font. Defaults to True.
    """
    logger.info("Correcting contours...")
    modified_glyphs = font.tt_correct_contours(min_area=min_area)

    if not modified_glyphs:
        logger.info("No glyphs were modified")
        return

    font.modified = True
    logger.info(f"{len(modified_glyphs)} glyphs were modified")

    if remove_hinting:
        dehint(font.ttfont, verbose=False)
