# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click
from foundrytools import Font

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``GSUB`` table.")


@cli.command("rename-feature")
@click.option(
    "-old",
    "--old-feature-name",
    "old_feature_name",
    required=True,
    help="The old feature name.",
)
@click.option(
    "-new",
    "--new-feature-name",
    "new_feature_name",
    required=True,
    help="The new feature name.",
)
@base_options()
def rename_feature(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Remaps the feature tags in the GSUB table.
    """

    def _task(font: Font, old_feature_name: str, new_feature_name: str) -> bool:
        if "GSUB" not in font.ttfont:
            logger.error("GSUB table not found")
            return False

        if old_feature_name == new_feature_name:
            logger.warning("Old and new feature tags are the same. No changes made.")
            return False

        if new_feature_name in font.t_gsub.get_feature_tags():
            logger.warning(f"Feature tag '{new_feature_name}' already exists")
            return False

        return font.t_gsub.rename_feature(old_feature_name, new_feature_name)

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.run()
