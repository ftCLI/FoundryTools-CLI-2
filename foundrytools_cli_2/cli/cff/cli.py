# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.cff.options import (
    font_names_option,
    top_dict_names_flags,
    top_dict_names_options,
)
from foundrytools_cli_2.cli.shared_callbacks import validate_params
from foundrytools_cli_2.cli.shared_options import base_options
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
