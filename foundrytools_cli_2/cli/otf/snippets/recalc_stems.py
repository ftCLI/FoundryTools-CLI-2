from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.stems import get_current_stems, recalc_stems, set_font_stems
from foundrytools_cli_2.lib.utils.path_tools import get_temp_file_path


def main(font: Font) -> None:
    """
    Recalculates the hinting stems of an OTF font.

    :param font: the Font object
    :return: None
    """
    if not font.is_ps:
        logger.error("Font is not a PostScript font")
        return

    if font.file is None:
        logger.error("Font has no file path")
        return

    flavor = font.ttfont.flavor
    temp_file = get_temp_file_path()
    if flavor is not None:
        font.ttfont.flavor = None
        font.save(temp_file)
        input_file = temp_file
    else:
        input_file = font.file

    logger.info("Getting stems...")
    current_std_h_w, current_std_v_w = get_current_stems(font.ttfont)
    std_h_w, std_v_w = recalc_stems(input_file)
    logger.info(f"StdHW: {current_std_h_w} -> {std_h_w}")
    logger.info(f"StdVW: {current_std_v_w} -> {std_v_w}")
    temp_file.unlink(missing_ok=True)

    if current_std_h_w == std_h_w and current_std_v_w == std_v_w:
        logger.info("Stems are already up-to-date")
    else:
        set_font_stems(font.ttfont, std_h_w, std_v_w)
        font.ttfont.flavor = flavor
        font.modified = True
