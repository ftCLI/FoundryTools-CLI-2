# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options, target_upm_option
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.lib.font import Font

cli = click.Group(help="Utilities for editing OpenType-TT fonts.")


@cli.command("autohint")
@base_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Auto-hints the given TrueType fonts using ttfautohint-py.
    """

    runner = TaskRunner(input_path=input_path, task=Font.tt_autohint, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()


@cli.command("dehint")
@base_options()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Removes hinting from the given TrueType fonts.
    """

    runner = TaskRunner(input_path=input_path, task=Font.tt_dehint, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()


@cli.command("decompose")
@base_options()
def decompose(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Decomposes the composite glyphs of the given TrueType fonts.
    """

    runner = TaskRunner(input_path=input_path, task=Font.tt_decomponentize, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()


@cli.command("scale-upm")
@target_upm_option(required=True)
@base_options()
def scale_upm(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Scales the given TrueType fonts to the specified UPM.
    """

    runner = TaskRunner(input_path=input_path, task=Font.tt_scale_upem, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()
