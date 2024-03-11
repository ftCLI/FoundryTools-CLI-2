# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.options.common_options import base_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the GSUB table.")


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
    from foundrytools_cli_2.snippets.gsub import rename_gsub_feature as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
