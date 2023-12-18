from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_builder.font_builder_tools import build_otf
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.t2_charstrings import from_beziers


def main(font: Font, subroutinize: bool = True) -> None:
    logger.info("Adding extremes")
    charstrings = from_beziers(font.ttfont)
    logger.info("Rebuilding OTF")
    build_otf(font=font.ttfont, charstrings_dict=charstrings)
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
