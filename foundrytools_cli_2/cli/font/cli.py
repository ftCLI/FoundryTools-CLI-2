from pathlib import Path
from typing import Any

import click
from foundrytools.core.font import Font

from foundrytools_cli_2.cli.base_command import BaseCommand
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.cli.logger import logger

cli = click.Group(help="Font level utilities.")


@cli.command("rebuild", cls=BaseCommand, help=Font.rebuild.__doc__)
def rebuild(input_path: Path, **options: dict[str, Any]) -> None:
    def task(font: Font) -> bool:
        logger.info("Rebuilding font...")
        font.rebuild()
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
