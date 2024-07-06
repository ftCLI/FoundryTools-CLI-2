# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import (
    base_options,
    input_path_argument,
    output_dir_option,
    overwrite_flag,
    recalc_timestamp_flag,
)
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("rebuild-cmap")
@base_options()
@click.option(
    "--remap-all",
    is_flag=True,
    help="Remap all characters in the cmap table.",
)
def rebuild_cmap_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rebuild the cmap table of a font. Optionally remap all characters, including those already in
    the cmap table.
    """
    from foundrytools_cli_2.cli.utils.snippets.rebuild_cmap import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("subset")
@input_path_argument()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
def subset_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subsets a font file by removing all glyphs except the ones specified.
    """
    from foundrytools_cli_2.cli.utils.snippets.subset import subset_font as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()
