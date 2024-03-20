# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.lib.font_runner import FontRunner


@click.command(no_args_is_help=True)
@click.option(
    "--italic-angle",
    "italic_angle",
    type=float,
    help="""Sets the `italicAngle` value.""",
)
@click.option(
    "--ul-position",
    "underline_position",
    type=int,
    help="""Sets the `underlinePosition` value.""",
)
@click.option(
    "--ul-thickness",
    "underline_thickness",
    type=click.IntRange(min=0),
    help="""Sets the `underlineThickness` value.""",
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    "fixed_pitch",
    is_flag=True,
    default=None,
    help="""Sets or clears the `isFixedPitch` value.""",
)
@base_options()
def cli(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    A command line tool to manipulate the ``post`` table.
    """
    from foundrytools_cli_2.cli.post.snipptes import set_attrs as task

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.run()
