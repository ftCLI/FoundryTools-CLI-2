import typing as t

import click

from foundrytools_cli_2.cli.shared_options import add_options


def remove_hinting_flag() -> t.Callable:
    """
    Returns a decorator that adds the --no-remove-hinting option to a click command. The option is
    a flag that can be used to keep the hinting of a TrueType font when the contours are modified.

    Returns:
        t.Callable: The decorator to add the option to a click command
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
