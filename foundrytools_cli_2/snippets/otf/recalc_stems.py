from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def main(font: Font) -> None:
    """
    Recalculates the hinting stems of an OTF font.

    :param font: the Font object
    :return: None
    """
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
