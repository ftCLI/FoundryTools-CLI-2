# pylint: disable=import-outside-toplevel

import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.converter.options import (
    in_format_choice,
    out_format_choice,
    tolerance_option,
    ttf2otf_mode_choice,
)
from foundrytools_cli_2.cli.shared_options import (
    base_options,
    correct_contours_flag,
    reorder_tables_flag,
    subroutinize_flag,
    target_upm_option,
)
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.lib.font import Font

cli = click.Group("converter", help="Font conversion utilities.")


@cli.command("otf2ttf")
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@base_options()
def otf_to_ttf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.otf_to_ttf import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("ttf2otf")
@ttf2otf_mode_choice()
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@correct_contours_flag()
@subroutinize_flag()
@base_options()
def ttf_to_otf(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.ttf_to_otf import ttf2otf, ttf2otf_with_tx

    if options["mode"] == "tx":
        options.pop("tolerance")
        task = ttf2otf_with_tx
    else:
        task = ttf2otf  # type: ignore

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("wf2ft")
@in_format_choice()
@reorder_tables_flag()
@base_options()
def web_to_sfnt(
    input_path: Path,
    in_format: t.Optional[t.Literal["woff", "woff2"]],
    **options: t.Dict[str, t.Any],
) -> None:
    """
    Convert WOFF and WOFF2 fonts to SFNT fonts.
    """
    runner = TaskRunner(input_path=input_path, task=Font.to_sfnt, **options)
    runner.filter.filter_out_sfnt = True
    runner.force_modified = True
    if in_format == "woff":
        runner.filter.filter_out_woff2 = True
    elif in_format == "woff2":
        runner.filter.filter_out_woff = True
    runner.run()


@cli.command("ft2wf")
@out_format_choice()
@reorder_tables_flag()
@base_options()
def sfnt_to_web(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.sfnt_to_web import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_woff = True
    runner.filter.filter_out_woff2 = True
    runner.save_if_modified = False
    runner.run()


@cli.command("var2static")
@base_options()
def variable_to_static(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Convert variable fonts to static fonts.
    """

    from foundrytools_cli_2.cli.converter.tasks.variable_to_static import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_static = True
    runner.filter.filter_out_ps = True
    runner.save_if_modified = False
    runner.run()
