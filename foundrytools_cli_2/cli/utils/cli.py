# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import input_path_argument, recursive_flag
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.cli.utils.options import font_organizer_options, rename_source_option

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("font-renamer")
@input_path_argument()
@rename_source_option()
@recursive_flag()
def font_renamer(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Renames the given font files.
    """
    from foundrytools_cli_2.cli.utils.tasks.font_renamer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("font-organizer")
@input_path_argument()
@font_organizer_options()
@recursive_flag()
def font_organizer(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Organizes the given font files based on specified sorting options.
    """
    # This is a workaround to make the task work with the current TaskRunner
    options["in_path"] = t.cast(t.Any, input_path)

    from foundrytools_cli_2.cli.utils.tasks.font_organizer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("sync-timestamps")
@input_path_argument()
@recursive_flag()
def align_timestamps(input_path: Path, recursive: bool = False) -> None:
    """
    Syncs the modified and created timestamps of the font files in the given path with the
    created and modified timestamps stored in their head table.
    """

    from foundrytools_cli_2.cli.utils.tasks.sync_timestamps import main as task

    task(input_path, recursive=recursive)
