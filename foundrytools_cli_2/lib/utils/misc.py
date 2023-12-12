import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def save_font(
    font: Font,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = False,
    reorder_tables: t.Optional[bool] = True,
    suffix: str = "",
) -> None:
    """
    Save a font to a file.

    Parameters:
        font (Font): The font to save.
        output_dir (Optional[Path], optional): The output directory. Defaults to None.
        overwrite (bool, optional): Flag indicating whether to overwrite existing files.
            Defaults to False.
        reorder_tables (Optional[bool], optional): Flag indicating whether to reorder the font
            tables. Defaults to True.
        suffix (str, optional): The suffix to append to the output file name. Defaults to "".
    """
    output_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite, suffix=suffix)
    font.save(output_file, reorder_tables=reorder_tables)
    log_file_saved(output_file=output_file)


def log_current_font(font: Font) -> None:
    """
    Logs the current font information.

    Parameters:
        font (Font): The font to log.
    """
    if hasattr(font, "file"):
        logger.info(f"Current file: {font.file}")
    elif hasattr(font, "bytesio"):
        logger.info(f"Current buffer: {font.bytesio}")
    else:
        logger.info(f"Current font: {font.ttfont}")


def log_file_saved(output_file: Path) -> None:
    """
    Log the information that a file has been saved to the specified output path.

    Parameters:
        output_file (Path): The path to the output file.
    """
    logger.success(f"File saved to {output_file}")


def log_file_not_saved(input_file: Path) -> None:
    """
    Log File Not Saved

    Logs a warning message indicating that no changes have been made to the specified input file.

    Parameters:
        input_file (Path): The path to the input file.
    """
    logger.warning(f"No changes made to {input_file}")
