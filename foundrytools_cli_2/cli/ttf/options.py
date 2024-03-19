import typing as t

import click

from foundrytools_cli_2.cli.shared_options import add_options


def remove_hinting_flag() -> t.Callable:
    """
    Add the remove_hinting option to a click command.

    :return: a decorator that adds the remove_hinting option to a click command
    """
    _remove_hinting_flag = [
        click.option(
            "--no-remove-hinting",
            "remove_hinting",
            is_flag=True,
            default=True,
            help="""
            If one or more glyphs have been modified, the hinting will be removed by default. Use
            ``--no-remove-hinting`` to keep the hinting.
            """,
        )
    ]
    return add_options(_remove_hinting_flag)
