# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Experimental utilities.")



@cli.command("recalc-zones")
@base_options()
def recalc_zones(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates hinting zones for the given font files.
    """
    from foundrytools_cli_2.cli.experimental.tasks.recalc_zones import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()
