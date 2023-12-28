# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib import Font
from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    in_format_choice,
    out_format_choice,
    subroutinize_flag,
    target_upm_option,
    tolerance_option,
    ttf2otf_mode_choice,
)
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group("converter", help="Font conversion utilities.")


@cli.command("otf2ttf")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@common_options()
def otf_to_ttf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    from foundrytools_cli_2.snippets.converter.otf_to_ttf import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("ttf2otf")
@ttf2otf_mode_choice()
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@subroutinize_flag()
@common_options()
def ttf_to_otf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """
    from foundrytools_cli_2.snippets.converter.ttf_to_otf import ttf2otf, ttf2otf_with_tx

    if options["mode"] == "tx":
        options.pop("tolerance")
        task = ttf2otf_with_tx
    else:
        task = ttf2otf  # type: ignore

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.auto_save = False
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("wf2ft")
@in_format_choice()
@common_options()
def web_to_sfnt(
    input_path: Path,
    in_format: t.Optional[t.Literal["woff", "woff2"]],
    **options: t.Dict[str, t.Any],
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
    runner.run()


@cli.command("ft2wf")
@out_format_choice()
@common_options()
def sfnt_to_web(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """
    from foundrytools_cli_2.snippets.converter.sfnt_to_web import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_woff = True
    runner.filter.filter_out_woff2 = True
    runner.auto_save = False
    runner.run()


@cli.command("var2static")
@common_options()
def variable_to_static(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert variable fonts to static fonts.
    """

    from foundrytools_cli_2.snippets.converter.variable_to_static import main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.filter.filter_out_static = True
    runner.filter.filter_out_ps = True
    runner.auto_save = False
    runner.run()
