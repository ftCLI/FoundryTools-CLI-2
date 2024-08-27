# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.cff.options import (
    font_names_option,
    top_dict_names_flags,
    top_dict_names_options,
    unique_id_flag,
)
from foundrytools_cli_2.cli.shared_callbacks import validate_params
from foundrytools_cli_2.cli.shared_options import base_options, new_string, old_string
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group("cff", help="Utilities for editing the ``CFF`` table.")


@cli.command("set-names")
@font_names_option()
@top_dict_names_options()
@base_options()
def set_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets the provided values in the ``CFF`` table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.cff.snippets import set_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("del-names")
@top_dict_names_flags()
@unique_id_flag()
@base_options()
def del_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Deletes the provided names from the ``CFF`` table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.cff.snippets import del_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("find-replace")
@old_string()
@new_string()
@base_options()
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Replaces the provided string in the ``CFF`` table with a new string.

    It searches for the old string in the following attributes:
    - version
    - FullName
    - FamilyName
    - Weight

    If the old string is found in any of the above attributes, it is replaced with the new string.
    """
    from foundrytools_cli_2.cli.cff.snippets import find_replace as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()
