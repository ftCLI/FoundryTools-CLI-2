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
    output_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite, suffix=suffix)
    font.save(output_file, reorder_tables=reorder_tables)
    log_file_saved(output_file=output_file)


def log_current_font(font: Font):
    if hasattr(font, "file"):
        logger.info(f"Current file: {font.file}")
    elif hasattr(font, "bytesio"):
        logger.info(f"Current buffer: {font.bytesio}")
    else:
        logger.info(f"Current font: {font.ttfont}")


def log_file_saved(output_file: Path):
    logger.success(f"File saved to {output_file}")


def log_file_not_saved(input_file: Path):
    logger.warning(f"No changes made to {input_file}")
