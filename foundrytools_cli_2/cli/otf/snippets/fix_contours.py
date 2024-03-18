from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def main(font: Font, min_area: int = 25, subroutinize: bool = True) -> None:
    """
    Corrects contours of the given font by removing overlaps, correcting the direction of the
    contours, and removing tiny paths. Optionally, subroutinizes the font after correcting the
    contours.

    Parameters:
        font (Font): The font object to be corrected.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.
        subroutinize (bool, optional): Flag to indicate whether to subroutinize the font.
            Defaults to True.

    Returns:
        None
    """
    logger.info("Correcting contours...")
    modified = font.ps_correct_contours(min_area=min_area)

    if not modified:
        logger.info("No contours were modified")
        return

    font.modified = True
    logger.info(f"{len(modified)} contours were modified")

    if subroutinize:
        logger.info("Subroutinizing...")
        font.ps_subroutinize()
