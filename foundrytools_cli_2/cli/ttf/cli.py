# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click
from foundrytools import Font

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.shared_options import base_options, target_upm_option
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing OpenType-TT fonts.")


@cli.command("autohint")
@base_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Auto-hints the given TrueType fonts using ttfautohint-py.
    """
    from foundrytools.app.ttf_autohint import run as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("dehint")
@base_options()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Removes hinting from the given TrueType fonts.
    """
    from foundrytools.app.ttf_dehint import run as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("decompose")
@base_options()
def decompose(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Decomposes the composite glyphs of the given TrueType fonts.
    """

    def task(font: Font) -> bool:
        result = font.t_glyf.decompose_all()
        if result:
            logger.opt(colors=True).info(f"Decomposed glyphs: <lc>{', '.join(list(result))}</lc>")
            return True
        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("scale-upm")
@target_upm_option(required=True)
@base_options()
def scale_upm(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Scales the given TrueType fonts to the specified UPM.
    """

    runner = TaskRunner(input_path=input_path, task=Font.scale_upm, **options)
    runner.filter.filter_out_ps = True
    runner.force_modified = True
    runner.run()
