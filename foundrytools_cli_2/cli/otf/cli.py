# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.otf.options import drop_zones_stems_flag, otf_autohint_options
from foundrytools_cli_2.cli.shared_options import base_options, subroutinize_flag
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.lib.font import Font

cli = click.Group(help="Utilities for editing OpenType-PS fonts.")


@cli.command("autohint")
@otf_autohint_options()
@base_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Autohint OpenType-PS fonts with ``afdko.otfautohint``.
    """
    from foundrytools_cli_2.cli.otf.snippets.autohint import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("dehint")
@drop_zones_stems_flag()
@base_options()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Dehint OpenType-PS fonts.
    """
    from foundrytools_cli_2.cli.otf.snippets.dehint import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("recalc-stems")
@base_options()
def recalc_stems(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates hinting stems for the given font files.
    """
    from foundrytools_cli_2.cli.otf.snippets.recalc_stems import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("recalc-zones")
@base_options()
def recalc_zones(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates hinting zones for the given font files.
    """
    from foundrytools_cli_2.cli.otf.snippets.recalc_zones import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("subr")
@base_options()
def subr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = TaskRunner(input_path=input_path, task=Font.ps_subroutinize, **options)
    runner.filter.filter_out_tt = True
    runner.force_modified = True
    runner.run()


@cli.command("desubr")
@base_options()
def desubr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = TaskRunner(input_path=input_path, task=Font.ps_desubroutinize, **options)
    runner.filter.filter_out_tt = True
    runner.force_modified = True
    runner.run()


@cli.command("check-outlines")
@base_options()
def check_outlines(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Check the outlines of OpenType-PS fonts with ``afdko.checkoutlinesufo``.
    """
    from foundrytools_cli_2.cli.otf.snippets.check_outlines import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.save_if_modified = False
    runner.run()


@cli.command("add-extremes")
@base_options()
@subroutinize_flag()
def add_extremes(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Add missing extreme points to OpenType-PS fonts.
    """
    from foundrytools_cli_2.cli.otf.snippets.add_extremes import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("round-coordinates")
@base_options()
@subroutinize_flag()
def round_coordinates(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Round the coordinates of OpenType-PS fonts.
    """
    from foundrytools_cli_2.cli.otf.snippets.round_coordinates import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()
