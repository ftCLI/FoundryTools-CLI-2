# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.cli.utils.options import rename_source_option

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("font-renamer")
@rename_source_option()
@base_options()
def font_renamer(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Renames the given font files.
    """
    from foundrytools_cli_2.cli.utils.snippets.font_renamer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()
