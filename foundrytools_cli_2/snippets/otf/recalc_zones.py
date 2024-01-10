from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def main(font: Font) -> None:
    """
    Recalculates the hinting zones of an OTF font.

    :param font: the Font object
    :return: None
    """
    logger.info("Getting zones...")
    current_other_blues, current_blue_values = font.ps_get_zones()
    other_blues, blue_values = font.ps_recalc_zones()
    logger.info(f"OtherBlues: {other_blues}")
    logger.info(f"BlueValues: {blue_values}")

    if current_other_blues == other_blues and current_blue_values == blue_values:
        logger.info("Zones are already up-to-date")
    else:
        font.ps_set_zones(other_blues, blue_values)
        font.modified = True
