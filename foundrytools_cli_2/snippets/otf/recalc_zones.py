from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.zones import get_current_zones, recalc_zones, set_font_zones


def main(font: Font) -> None:
    """
    Recalculates the hinting zones of an OTF font.

    :param font: the Font object
    :return: None
    """
    if not font.is_ps:
        logger.error("Font is not a PostScript font")
        return

    if font.is_woff or font.is_woff2:
        logger.error("Font is a web font")
        return

    logger.info("Getting zones...")
    current_other_blues, current_blue_values = get_current_zones(font.ttfont)
    other_blues, blue_values = recalc_zones(font.ttfont)

    logger.info(f"OtherBlues: {current_other_blues} -> {other_blues}")
    logger.info(f"BlueValues: {current_blue_values} -> {blue_values}")

    if current_other_blues == other_blues and current_blue_values == blue_values:
        logger.info("Zones are already up-to-date")
    else:
        set_font_zones(font.ttfont, other_blues, blue_values)
        font.modified = True
