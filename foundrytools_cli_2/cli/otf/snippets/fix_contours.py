from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(font: Font, min_area: int = 25, subroutinize: bool = True) -> None:
    """
    Corrects contours of the given font by removing overlaps, correcting the direction of the
    contours, and removing tiny paths. Optionally, subroutinizes the font after correcting the
    contours.

    Args:
        font (Font): The font object to be corrected.
        min_area (int, optional): The minimum area of a contour to be considered. Defaults to 25.
        subroutinize (bool, optional): Flag to indicate whether to subroutinize the font.
            Defaults to True.
    """
    logger.info("Correcting contours...")
    modified_glyphs = font.ps_correct_contours(min_area=min_area)

    if not modified_glyphs:
        logger.info("No glyphs were modified")
        return

    font.modified = True
    logger.info(f"{len(modified_glyphs)} glyphs were modified")

    if subroutinize:
        logger.info("Subroutinizing...")
        font.ps_subroutinize()
