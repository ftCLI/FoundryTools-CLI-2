# pylint: disable=import-outside-toplevel
from pathlib import Path
from typing import Any, Literal, Optional

import click
from foundrytools import Font

from foundrytools_cli_2.cli import BaseCommand, choice_to_int_callback
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group("converter", help="Font conversion utilities.")


@cli.command("otf2ttf", cls=BaseCommand)
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(min=0.0, max=3.0),
    default=1.0,
    help="""
    Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps shapes.
    High tolerance adds few points but may change shape.
    """,
)
@click.option(
    "-upm",
    "--target-upm",
    type=click.IntRange(min=16, max=16384),
    help="""
    Set the target UPM value for the converted font.

    Scaling is applied to the font after conversion to TrueType, to avoid scaling a PostScript font
    (which in some cases can lead to corrupted outlines).
    """,
)
def otf_to_ttf(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.otf_to_ttf import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("ttf2otf", cls=BaseCommand)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["qu2cu", "tx"]),
    default="qu2cu",
    show_default=True,
    help="""
    Conversion mode. By default, the script uses the ``qu2cu`` mode. Quadratic curves are
    converted to cubic curves using the Qu2CuPen. Use the ``tx`` mode to use the tx tool
    from AFDKO to generate the CFF table instead of the Qu2CuPen.
    """,
)
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(min=0.0, max=3.0),
    default=1.0,
    help="""
    Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps shapes.
    High tolerance adds few points but may change shape.

    This option is only used in the ``qu2cu`` mode.
    """,
)
@click.option(
    "-upm",
    "--target-upm",
    type=click.IntRange(min=16, max=16384),
    default=None,
    help="""
    Set the target UPM value for the converted font.

    Scaling is applied to the TrueType font before conversion, to avoid scaling a PostScript font
    (which in some cases can lead to corrupted outlines).
    """,
)
@click.option(
    "-cc/--no-cc",
    "--correct-contours/--no-correct-contours",
    is_flag=True,
    default=True,
    show_default=True,
    help="""
    Correct contours with pathops during conversion (removes overlaps and tiny contours, corrects
    direction).
    """,
)
@click.option(
    "-co/--no-co",
    "--check-outlines/--no-check-outlines",
    is_flag=True,
    default=False,
    show_default=True,
    help="Perform a further check with ``afdko.checkoutlinesufo`` after conversion.",
)
@click.option(
    "-s/--no-s",
    "--subroutinize/--no-subroutinize",
    is_flag=True,
    default=True,
    show_default=True,
    help="Subroutinize the font with ``cffsubr`` after conversion.",
)
def ttf_to_otf(input_path: Path, **options: dict[str, Any]) -> None:
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


@cli.command("wf2ft", cls=BaseCommand)
@click.option(
    "-f",
    "--format",
    "in_format",
    type=click.Choice(["woff", "woff2"]),
    default=None,
    help="""
    By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts
    (TrueType or OpenType). Use this option to convert only woff or woff2 flavored web
    fonts.
    """,
)
def web_to_sfnt(
    input_path: Path,
    in_format: Optional[Literal["woff", "woff2"]],
    **options: dict[str, Any],
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


@cli.command("ft2wf", cls=BaseCommand)
@click.option(
    "-f",
    "--format",
    "out_format",
    type=click.Choice(["woff", "woff2"]),
    default=None,
    help="""
    By default, the script converts SFNT fonts to both woff and woff2 flavored web fonts.
    Use this option to convert only to woff or woff2 flavored web fonts.
    """,
)
def sfnt_to_web(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.sfnt_to_web import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_woff = True
    runner.filter.filter_out_woff2 = True
    runner.save_if_modified = False
    runner.run()


@cli.command("var2static", cls=BaseCommand)
@click.option(
    "-ol",
    "--overlap-mode",
    "overlap",
    type=click.Choice(["0", "1", "2", "3"]),
    default="1",
    show_default=True,
    callback=choice_to_int_callback,
    help="""
    The overlap mode to use when converting variable fonts to static fonts.

    See https://fonttools.readthedocs.io/en/latest/varLib/instancer.html#fontTools.varLib.instancer.instantiateVariableFont

    \b
    0: KEEP_AND_DONT_SET_FLAGS
    1: KEEP_AND_SET_FLAGS
    2: REMOVE
    3: REMOVE_AND_IGNORE_ERRORS
    """,
)
@click.option(
    "-s",
    "--select-instance",
    is_flag=True,
    help="Select a single instance with custom axis values.",
)
def variable_to_static(input_path: Path, **options: dict[str, Any]) -> None:
    """
    Convert variable fonts to static fonts.
    """
    from foundrytools_cli_2.cli.converter.tasks.variable_to_static import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_static = True
    runner.filter.filter_out_ps = True
    runner.save_if_modified = False
    runner.run()
