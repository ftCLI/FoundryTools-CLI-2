# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group("cff", help="CFF table utilities.")


@cli.command("test")
@base_options()
def test(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Print the CFF table of a font.
    """
    from foundrytools_cli_2.cli.cff.snippets.test import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()
