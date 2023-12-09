from typing import Any

import click

from foundrytools_cli_2.lib import Font
from foundrytools_cli_2.lib.font_runner import FontRunner
from foundrytools_cli_2.lib.click.click_options import (
    target_upm_option,
    tolerance_option,
    subroutinize_flag,
    common_options,
)


cli = click.Group()


@cli.command("ps2tt")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@common_options()
def ps_to_tt(**options: Any) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    from foundrytools_cli_2.snippets.ps_to_tt import otf2ttf
    runner = FontRunner(task=otf2ttf, task_name="Converting", **options)
    runner.finder_options.filter_out_tt = True
    runner.finder_options.filter_out_variable = True
    runner.run()


@cli.command("tt2ps")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@subroutinize_flag()
@common_options()
def ttf2otf(**options: Any) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """
    from foundrytools_cli_2.snippets.tt_to_ps import ttf2otf as tt_to_ps
    runner = FontRunner(task=tt_to_ps, task_name="Converting", **options)
    runner.font_filter.filter_out_ps = True
    runner.font_filter.filter_out_variable = True
    runner.run()


@cli.command("to-woff")
@common_options()
def sfnt_to_woff(**options: Any) -> None:
    """
    Convert SFNT fonts to WOFF flavored fonts.
    """
    runner = FontRunner(task=Font.to_woff, task_name="Converting", **options)
    runner.finder_options.filter_out_woff = True
    runner.finder_options.filter_out_woff2 = True
    runner.run()


@cli.command("to-woff2")
@common_options()
def sfnt_to_woff2(**options: Any) -> None:
    """
    Convert SFNT fonts to WOFF2 flavored fonts.
    """
    runner = FontRunner(task=Font.to_woff2, task_name="Converting", **options)
    runner.finder_options.filter_out_woff2 = True
    runner.run()


@cli.command("from-woff")
@common_options()
def woff_to_sfnt(**options: Any) -> None:
    """
    Convert WOFF flavored fonts to SFNT fonts.
    """
    runner = FontRunner(task=Font.to_sfnt, task_name="Converting", **options)
    runner.finder_options.filter_out_sfnt = True
    runner.finder_options.filter_out_woff = True
    runner.run()


@cli.command("from-woff2")
@common_options()
def woff2_to_sfnt(**options: Any) -> None:
    """
    Convert WOFF2 flavored fonts to SFNT fonts.
    """
    runner = FontRunner(task=Font.to_sfnt, task_name="Converting", **options)
    runner.finder_options.filter_out_sfnt = True
    runner.finder_options.filter_out_woff2 = True
    runner.run()
