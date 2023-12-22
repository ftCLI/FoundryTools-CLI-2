# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    name_id,
    name_ids,
    skip_name_ids,
    platform_id_option,
    string_option,
    old_string_option,
    new_string_option,
)
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the name table.")


@cli.command("find-replace")
@old_string_option()
@new_string_option()
@name_ids(required=False)
@skip_name_ids()
@platform_id_option()
@common_options()
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Find and replace text in the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import find_replace as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.auto_save = False
    runner.run()


@cli.command("set-name")
@string_option()
@name_id()
@platform_id_option()
@common_options()
def set_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the name table of the given font files.
    """
    from foundrytools_cli_2.snippets.name import set_name as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.auto_save = False
    runner.run()
