import typing as t
from pathlib import Path

from afdko.checkoutlinesufo import run as check_outlines

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font

from . import get_file_to_process


def main(
    font: Font,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = False,
    recalc_timestamp: bool = False,
) -> None:
    """
    Checks the outlines of an OpenType-PS font with afdko's checkoutlinesufo.

    Args:
        font (Font): The font to check.
        output_dir (t.Optional[Path]): The directory where the font will be saved.
        overwrite (bool): Whether to overwrite the output file if it already exists.
        recalc_timestamp (bool): Whether to recalculate the font's timestamp.
    """
    flavor = font.ttfont.flavor
    file_to_process = get_file_to_process(font, output_dir=output_dir, overwrite=overwrite)
    check_outlines(args=[file_to_process.as_posix(), "--error-correction-mode"])

    if flavor is not None:
        font = Font(file_to_process, recalc_timestamp=recalc_timestamp)
        font.ttfont.flavor = flavor
        font.save(file_to_process)

    logger.success(f"File saved to {file_to_process}")
