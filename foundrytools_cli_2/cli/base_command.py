import os
from pathlib import Path
from typing import Optional

import click


class BaseCommand(click.Command):
    """
    Base command for all commands in the CLI.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        shared_options = [
            click.Argument(
                ["input_path"],
                type=click.Path(exists=True, resolve_path=True, path_type=Path),
            ),
            click.Option(
                ["-r", "--recursive"],
                is_flag=True,
                default=False,
                help="""
                Recursively find font files both in input directory and its subdirectories.

                Only applicable if ``INPUT_PATH`` is a directory.
                """,
            ),
            click.Option(
                ["-out", "--output-dir"],
                type=click.Path(path_type=Path, file_okay=False, writable=True),
                callback=output_dir_callback,
                help="""
                The directory where output files are to be saved.

                If not specified, files will be saved to the same folder.

                If the output directory doesn't exist, it will be created, as well as any missing
                parent directories.
                """,
            ),
            click.Option(
                ["-no-ow", "--no-overwrite", "overwrite"],
                is_flag=True,
                default=True,
                help="""
                Do not overwrite existing files on save.

                If a file with the same name as the output file already exists, the command will
                suffix the filename with a number (``#1``, ``#2``, etc.).

                By default, existing files are overwritten.
                """,
            ),
            click.Option(
                ["-no-rbb", "--no-recalc-bboxes", "recalc_bboxes"],
                is_flag=True,
                default=True,
                help="""
                Do not recalculate the font's bounding boxes on save.

                By default, ``glyf``, ``CFF ``, ``head`` bounding box values and ``hhea``/``vhea``
                min/max values are recalculated on save. Also, the glyphs are compiled on importing,
                which saves memory consumption and time.
                """,
            ),
            click.Option(
                ["-no-rtb", "--no-reorder-tables", "reorder_tables"],
                is_flag=True,
                default=True,
                help="""
                Do not reorder the font's tables on save.

                By default, tables are sorted by tag on save (recommended by the OpenType
                specification).
                """,
            ),
            click.Option(
                ["-rts", "--recalc-timestamp"],
                is_flag=True,
                default=False,
                help="""
                Set the ``modified`` timestamp in the ``head`` table on save.

                By default, the original ``modified`` timestamp is kept.
                """,
            ),
        ]
        kwargs.setdefault("params", []).extend(shared_options)
        kwargs.setdefault("no_args_is_help", True)
        kwargs.setdefault("context_settings", {"help_option_names": ["-h", "--help"]})
        super().__init__(*args, **kwargs)


def output_dir_callback(
    ctx: click.Context, _: click.Parameter, value: Optional[Path]
) -> Optional[Path]:
    """
    Callback for ``--output-dir option``.

    Tries to create the output directory if it doesn't exist. Checks if the output directory is
    writable. Returns a Path object. If the callback fails, raises a click.BadParameter exception.

    Args:
        ctx (click.Context): click Context
        _: click Parameter
        value (t.Optional[Path]): The value to convert

    Returns:
        t.Optional[Path]: The converted value
    """

    # if the value is None or the click context is resilient, return None
    if not value or ctx.resilient_parsing:
        return None
    # try to create the output directory if it doesn't exist
    try:
        value.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise click.BadParameter(f"Could not create output directory: {e}") from e
    # check if the output directory is writable
    if not os.access(value, os.W_OK):
        raise click.BadParameter(f"Output directory is not writable: {value}")
    return value
