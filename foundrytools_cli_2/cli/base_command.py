from pathlib import Path
from typing import Optional

import click


class BaseCommand(click.Command):
    def __init__(self, *args, **kwargs) -> None:
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
                type=click.Path(file_okay=False, writable=True),
                callback=output_dir_callback,
                help="""
                The directory where output files are to be saved.

                If not specified, files will be saved to the same folder.

                If the output directory doesn't exist, it will be created, as well as any missing
                parent directories.
                """,
            ),
            click.Option(
                ["--no-overwrite"],
                is_flag=True,
                default=False,
                show_default=True,
                help="""
                Do not overwrite existing files.

                If a file with the same name as the output file already exists, the command will
                suffix the filename with a number (``#1``, ``#2``, etc.) to avoid overwriting an
                existing file.
                """,
            ),
            click.Option(
                ["--recalc-timestamp"],
                is_flag=True,
                default=False,
                help="""
                Set the font's 'modified' timestamp current time.
                """,
            ),
            click.Option(
                ["--no-recalc-bboxes", "recalc_bboxes"],
                is_flag=True,
                default=True,
                help="""
                Use this flag to avoid recalculating the bounding boxes of all glyphs on save. By
                default, bounding boxes are recalculated.
                """,
            ),
            click.Option(
                ["--reorder-tables/--no-reorder-tables"],
                default=True,
                help="""
                Reorder the font's tables on save. If ``True`` (the default), reorder the tables,
                sorting them by tag (recommended by the OpenType specification). If ``False``,
                retain the original font order. If ``None``, reorder by table dependency (fastest).
                """,
            )
        ]
        kwargs.setdefault("params", []).extend(shared_options)
        kwargs.setdefault("no_args_is_help", True)
        kwargs.setdefault("context_settings", {"help_option_names": ["-h", "--help"]})
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Writes the help into the formatter if it exists.

        This is a low-level method called by :meth:`get_help`.

        This calls the following methods:

        -   :meth:`format_usage`
        -   :meth:`format_help_text`
        -   :meth:`format_input_path`
        -   :meth:`format_options`
        -   :meth:`format_epilog`
        """
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_input_path(formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    @staticmethod
    def format_input_path(formatter: click.HelpFormatter) -> None:
        formatter.write_text("\n")
        formatter.indent()
        formatter.write_text(
            "INPUT_PATH can be a file or a directory. If it's a directory, the command will "
            "process all files in the directory, and eventually in subdirectories if the "
            "``--recursive`` option is used. If it's a file, only that file will be processed."
        )
        formatter.dedent()


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