# pylint: disable=import-outside-toplevel
from pathlib import Path
from typing import Any, Callable, cast

import click

from foundrytools_cli_2.cli import make_options
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.cli.utils.options import font_organizer_options, rename_source_option


def recursive_flag() -> Callable:
    """
    Add the ``recursive`` option to a click command.

    :return: A decorator that adds the ``recursive`` option to a click command
    :rtype: Callable
    """
    _recursive_flag = [
        click.option(
            "-r",
            "--recursive",
            is_flag=True,
            default=False,
            help="""
            If ``input_path`` is a directory, the font finder will search for fonts recursively in
            subdirectories.
            """,
        )
    ]
    return make_options(_recursive_flag)


cli = click.Group(help="Miscellaneous utilities.")


@cli.command("font-renamer")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@rename_source_option()
@recursive_flag()
def font_renamer(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Renames the given font files.
    """
    from foundrytools_cli_2.cli.utils.tasks.font_renamer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("font-organizer")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@font_organizer_options()
@recursive_flag()
def font_organizer(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Organizes the given font files based on specified sorting options.
    """
    # This is a workaround to make the task work with the current TaskRunner
    options["in_path"] = cast(Any, input_path)

    from foundrytools_cli_2.cli.utils.tasks.font_organizer import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()


@cli.command("sync-timestamps")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@recursive_flag()
def align_timestamps(input_path: Path, recursive: bool = False) -> None:
    """
    Syncs the modified and created timestamps of the font files in the given path with the
    created and modified timestamps stored in their head table.
    """

    from foundrytools_cli_2.cli.utils.tasks.sync_timestamps import main as task

    task(input_path, recursive=recursive)
