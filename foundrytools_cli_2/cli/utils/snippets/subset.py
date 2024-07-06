import typing as t
from pathlib import Path

from afdko.fdkutils import run_shell_command

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def subset_font(
    font: Font,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False
) -> None:
    """
    Subsets a font file by removing all glyphs except the ones specified.

    Args:
        font (Font): The Font object representing the font file.
        output_dir (Path, optional): The directory to save the font file. Defaults to None.
        overwrite (bool, optional): Flag to indicate whether to overwrite the existing file.
            Defaults to True.
        recalc_timestamp (bool, optional): Flag to indicate whether to recalculate the timestamp
    """
    in_file = font.file
    out_file = font.make_out_file_name(file=in_file, output_dir=output_dir, overwrite=overwrite)
    if in_file == out_file:
        out_file = font.make_out_file_name(
            file=in_file, output_dir=output_dir, overwrite=True, suffix="_subset"
        )

    command = [
        "fonttools",
        "subset",
        in_file,
        f"--output-file={out_file}",
        "--unicodes=*",
        "--notdef-glyph",
        "--notdef-outline",
        "--layout-features=*",
        "--layout-scripts=*",
        "--drop-tables=",
        "--passthrough-tables",
        "--legacy-kern",
        "--name-IDs=*",
        "--name-legacy",
        "--name-languages=*",
        "--glyph-names",
        "--legacy-cmap",
        "--symbol-cmap",
        "--recalc-bounds",
        "--recalc-average-width",
        "--recalc-max-context",
    ]

    if recalc_timestamp:
        command.append("--recalc-timestamp")
    else:
        command.append("--no-recalc-timestamp")

    run_shell_command(command)
    logger.opt(colors=True).success(f"File saved to {out_file}")
