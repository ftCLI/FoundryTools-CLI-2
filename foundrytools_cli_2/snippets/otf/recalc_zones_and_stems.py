from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def main(font: Font, zones: bool = True, stems: bool = True) -> None:
    """
    Recalculates the hinting zones and stems of an OTF font.

    :param font: the Font object
    :param zones: whether to recalculate the zones
    :param stems: whether to recalculate the stems
    :return: None
    """
    if not (zones or stems):
        logger.info("Both zones and stems are disabled, nothing to do")
        return

    if stems:
        logger.info("Getting stems...")
        current_std_h_w, current_std_v_w = font.ps_get_stems()
        std_h_w, std_v_w = font.ps_recalc_stems()
        logger.info(f"StdHW: {std_h_w}")
        logger.info(f"StdVW: {std_v_w}")

        if current_std_h_w == std_h_w and current_std_v_w == std_v_w:
            logger.info("Stems are already up-to-date")
        else:
            font.ps_set_stems(std_h_w, std_v_w)
            font.modified = True

    if zones:
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
