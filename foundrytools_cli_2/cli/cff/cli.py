# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click
from foundrytools import Font
from foundrytools.constants import TOP_DICT_NAMES

from foundrytools_cli_2.cli.base_command import BaseCommand
from foundrytools_cli_2.cli.shared_callbacks import ensure_at_least_one_param
from foundrytools_cli_2.cli.shared_options import add_options
from foundrytools_cli_2.cli.task_runner import TaskRunner


def _top_dict_names_flags() -> t.Callable:
    flags = [
        click.option(
            f"--{option_param}",
            var_name,
            is_flag=True,
            default=None,
            help=f"Deletes the ``{var_name}`` value",
        )
        for option_param, var_name in sorted(TOP_DICT_NAMES.items())
    ]

    return add_options(flags)


def _top_dict_names_options() -> t.Callable:
    options = [
        click.option(
            f"--{option_param}",
            var_name,
            type=str,
            help=f"Sets the ``cff.topDictIndex[0].{var_name}`` value",
        )
        for option_param, var_name in sorted(TOP_DICT_NAMES.items())
    ]

    return add_options(options)


cli = click.Group("cff", help="Utilities for editing the ``CFF`` table.")


@cli.command("set-names", cls=BaseCommand)
@click.option(
    "--font-name",
    "fontNames",
    type=str,
    help="Sets the ``cff.fontNames`` value",
)
@_top_dict_names_options()
def set_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets the ``cff.fontNames[0]`` and/or ``topDictIndex[0]`` values.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, str]) -> bool:
        font.t_cff_.set_names(**kwargs)
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("del-names", cls=BaseCommand)
@_top_dict_names_flags()
@click.option(
    "--unique-id",
    "UniqueID",
    is_flag=True,
    default=None,
    help="Deletes the ``UniqueID`` value",
)
def del_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Deletes attributes from ``topDictIndex[0]`` using the provided keyword arguments.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, str]) -> bool:
        font.t_cff_.del_names(**kwargs)
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("find-replace", cls=BaseCommand)
@click.option(
    "-os",
    "--old-string",
    required=True,
    help="The string to be replaced in th CFF TopDictIndex[0] fields.",
)
@click.option(
    "-ns",
    "--new-string",
    required=True,
    help="The string to replace the old string with in the CFF TopDictIndex[0] fields.",
)
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Finds and replaces a string in the ``CFF`` table. It performs the replacement in
    ``cff.fontNames[0]`` and in the following ``topDictIndex[0]`` fields:

    \b
    * version
    * FullName
    * FamilyName
    * Weight
    * Copyright
    * Notice
    """

    def task(font: Font, old_string: str, new_string: str) -> bool:
        font.t_cff_.find_replace(old_string, new_string)
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()
