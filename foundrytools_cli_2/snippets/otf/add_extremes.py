from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.font_builder import build_otf
from foundrytools_cli_2.lib.otf.t2_charstrings import fix_charstrings, from_beziers


def main(font: Font, subroutinize: bool = True) -> None:
    """
    Adds extreme points to the outlines of an OpenType-PS font.

    Args:
        font (Font): The font to add extreme points to.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Adding extremes")
    charstrings = from_beziers(font.ttfont)
    logger.info("Rebuilding OTF")
    build_otf(font=font.ttfont, charstrings_dict=charstrings)
    logger.info("Fixing charstrings")
    fix_charstrings(font.ttfont)
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True
