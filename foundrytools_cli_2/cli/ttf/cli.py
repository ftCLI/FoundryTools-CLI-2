# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options, min_area_option
from foundrytools_cli_2.cli.ttf.options import remove_hinting_flag
from foundrytools_cli_2.lib import FontRunner
from foundrytools_cli_2.lib.font import Font

cli = click.Group(help="Utilities for editing OpenType-TT fonts.")


@cli.command("autohint")
@base_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Autohints the given TrueType fonts.
    """

    runner = FontRunner(input_path=input_path, task=Font.tt_autohint, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("dehint")
@base_options()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Removes hinting from the given TrueType fonts.
    """

    runner = FontRunner(input_path=input_path, task=Font.tt_remove_hints, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("fix-contours")
@min_area_option()
@remove_hinting_flag()
@base_options()
def fix_contours(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Corrects contours of the given TrueType fonts by removing overlaps, correcting the direction of
    the contours, and removing tiny paths.
    """

    from foundrytools_cli_2.cli.ttf.snippets.fix_contours import main as task

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()
