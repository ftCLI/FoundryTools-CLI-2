from pathlib import Path
import typing as t

from afdko.checkoutlinesufo import run as check_outlines

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


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
    in_file = font.file
    out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    if flavor is not None:
        font.ttfont.flavor = None
        font.ttfont.save(out_file)

    if in_file != out_file:
        font.ttfont.save(out_file)

    check_outlines([out_file.as_posix(), "--error-correction-mode"])

    if flavor is not None:
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        font.ttfont.flavor = flavor
        font.ttfont.save(out_file)

    logger.success(f"File saved to {out_file}")
