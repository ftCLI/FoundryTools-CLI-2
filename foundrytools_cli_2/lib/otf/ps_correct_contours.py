from fontTools.ttLib.ttFont import TTFont

from foundrytools_cli_2.lib.font_builder.font_builder_tools import build_otf
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.t2_charstrings import fix_charstrings


def correct_otf_contours(font: TTFont, min_area: int = 25) -> None:
    """
    Corrects the contours of an OTF font.

    Args:
        font (TTFont): The font to correct.
        min_area (int): The minimum area of a path to keep.
    """

    charstrings, modified = fix_charstrings(font=font, min_area=min_area)

    if not modified:
        logger.info("No glyphs modified")
        return

    logger.info(f"{len(modified)} glyphs modified")
    build_otf(font=font, charstrings_dict=charstrings)
