from foundrytools_cli_2.lib.beziers import add_extremes
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.otf_builder import build_otf


def main(font: Font, subroutinize: bool = True) -> None:
    """
    Adds extreme points to the outlines of an OpenType-PS font.

    Args:
        font (Font): The font to add extreme points to.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Adding extremes")
    charstrings = add_extremes(font.ttfont)
    logger.info("Rebuilding OTF")
    build_otf(font=font.ttfont, charstrings_dict=charstrings)
    font.ps_correct_contours()
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True
