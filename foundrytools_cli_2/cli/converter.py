# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib import Font
from foundrytools_cli_2.lib.font_runner import FontRunner
from foundrytools_cli_2.lib.click.click_options import (
    target_upm_option,
    tolerance_option,
    subroutinize_flag,
    common_options,
    in_format_choice,
    out_format_choice,
)


cli = click.Group("converter", help="Font conversion utilities.")


@cli.command("otf2ttf")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@common_options()
def otf2ttf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    from foundrytools_cli_2.snippets.converter.ps_to_tt import otf2ttf

    runner = FontRunner(input_path=input_path, task=otf2ttf, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("ttf2otf")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@subroutinize_flag()
@common_options()
def ttf2otf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """
    from foundrytools_cli_2.snippets.converter.tt_to_ps import ttf2otf as tt_to_ps

    runner = FontRunner(input_path=input_path, task=tt_to_ps, **options)
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("wf2ft")
@in_format_choice()
@common_options()
def wf2ft(
    input_path: Path,
    in_format: t.Optional[t.Literal["woff", "woff2"]],
    **options: t.Dict[str, t.Any]
) -> None:
    """
    Convert WOFF and WOFF2 fonts to SFNT fonts.
    """
    runner = FontRunner(input_path=input_path, task=Font.to_sfnt, **options)
    runner.filter.filter_out_sfnt = True
    if in_format == "woff":
        runner.filter.filter_out_woff2 = True
    elif in_format == "woff2":
        runner.filter.filter_out_woff = True
    else:
        runner.filter.filter_out_woff = False
        runner.filter.filter_out_woff2 = False
    runner.run()


@cli.command("ft2wf")
@out_format_choice()
@common_options()
def ft2wf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """
    from foundrytools_cli_2.snippets.converter.ft2wf import sfnt_to_wf

    runner = FontRunner(input_path=input_path, task=sfnt_to_wf, **options)
    runner.filter.filter_out_woff = True
    runner.filter.filter_out_woff2 = True
    runner.auto_save = False
    runner.run()
