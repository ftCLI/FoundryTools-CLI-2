import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.font import Font

from .add_extremes import main as add_extremes
from .autohint import main as autohint
from .check_outlines import main as check_outlines
from .fix_contours import main as fix_contours
from .recalc_stems import main as recalc_stems
from .recalc_zones import main as recalc_zones

__all__ = [
    "add_extremes",
    "autohint",
    "check_outlines",
    "fix_contours",
    "recalc_stems",
    "recalc_zones",
    "get_file_to_process",
]


def get_file_to_process(
    font: Font, output_dir: t.Optional[Path] = None, overwrite: bool = True
) -> Path:
    """
    Returns the file to process.

    :param font: the Font object
    :param output_dir: the output directory
    :param overwrite: whether to overwrite the output file if it already exists

    :return: the file be processed (Path) by AFDKO's modules
    """
    in_file = font.file
    out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    if flavor is not None:
        font.ttfont.flavor = None

    if in_file != out_file or flavor is not None:
        font.save(out_file)

    return out_file
