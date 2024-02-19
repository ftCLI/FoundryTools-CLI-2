import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.font import Font


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
        font.to_sfnt()

    if in_file != out_file or flavor is not None:
        font.save(out_file)

    return out_file
