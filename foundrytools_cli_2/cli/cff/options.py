import typing as t

import click

from foundrytools_cli_2.cli.shared_options import add_options
from foundrytools_cli_2.lib.constants import TOP_DICT_NAMES


def font_names_option() -> t.Callable:
    """
    Add the ``font-name`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``font-name`` option to a click command
    """
    _font_name_option = [
        click.option(
            "--font-name",
            "fontNames",
            type=str,
            help="Sets the ``cff.fontNames`` value",
        )
    ]
    return add_options(_font_name_option)


def top_dict_names_flags() -> t.Callable:
    """
    Add the ``full-name``, ``family-name``, ``weight``, and ``version`` flags to a click command.

    Returns:
        t.Callable: A decorator that adds the flags to a click command
    """

    flags = [
        click.option(
            f"--{option_param}",
            var_name,
            is_flag=True,
            default=None,
            help=f"Deletes the ``cff.topDictIndex[0].{var_name}`` value",
        )
        for option_param, var_name in sorted(TOP_DICT_NAMES.items())
    ]

    return add_options(flags)


def top_dict_names_options() -> t.Callable:
    """
    Add the ``full-name``, ``family-name``, ``weight``, and ``version`` options to a click command.

    Returns:
        t.Callable: A decorator that adds the options to a click command
    """

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
