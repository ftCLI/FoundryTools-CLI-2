# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.click_options import (
    autohint_options,
    common_options,
    min_area_option,
    subroutinize_flag,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing OpenType-PS fonts.")


@cli.command("autohint")
@autohint_options()
@common_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Autohint OpenType-PS fonts with ``afdko.otfautohint``.
    """
    from foundrytools_cli_2.snippets.otf.autohint import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.auto_save = False
    runner.run()


@cli.command("recalc-stems")
@common_options()
def recalc_stems(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates hinting stems for the given font files.
    """
    from foundrytools_cli_2.snippets.otf.recalc_zones_and_stems import recalc_stems as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("recalc-zones")
@common_options()
def recalc_zones(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates hinting zones for the given font files.
    """
    from foundrytools_cli_2.snippets.otf.recalc_zones_and_stems import recalc_zones as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("subr")
@common_options()
def subr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(input_path=input_path, task=Font.ps_subroutinize, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("desubr")
@common_options()
def desubr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(input_path=input_path, task=Font.ps_desubroutinize, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("fix-contours")
@min_area_option()
@subroutinize_flag()
@common_options()
def fix_contours(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fix the contours of OpenType-PS fonts by removing overlaps, correcting contours direction, and
    removing tiny paths.
    """

    from foundrytools_cli_2.snippets.otf.fix_contours import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("check-outlines")
@common_options()
def check_outlines(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Check the outlines of OpenType-PS fonts with ``afdko.checkoutlinesufo``.
    """
    from foundrytools_cli_2.snippets.otf.check_outlines import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.auto_save = False
    runner.run()


@cli.command("add-extremes")
@common_options()
@subroutinize_flag()
def add_extremes(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Add missing extreme points to OpenType-PS fonts.
    """
    from foundrytools_cli_2.snippets.otf.add_extremes import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()
