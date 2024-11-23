# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click
from foundrytools import Font
from foundrytools.app.otf_autohint import run as otf_autohint
from foundrytools.app.otf_check_outlines import run as otf_check_outlines
from foundrytools.app.otf_dehint import run as otf_dehint
from foundrytools.app.otf_desubroutinize import run as otf_desubroutinize
from foundrytools.app.otf_subroutinize import run as otf_subroutinize

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.otf.options import drop_hinting_data_flag, otf_autohint_options
from foundrytools_cli_2.cli.shared_options import base_options, subroutinize_flag
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing OpenType-PS fonts.")


@cli.command("autohint")
@otf_autohint_options()
@subroutinize_flag()
@base_options()
def autohint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Autohint OpenType-PS fonts with ``afdko.otfautohint``.
    """
    # from foundrytools_cli_2.cli.otf.tasks import autohint as task

    def _task(font: Font, subroutinize: bool = True, **kwargs: t.Dict[str, t.Any]) -> bool:
        logger.info("Autohinting...")
        otf_autohint(font, **kwargs)

        if subroutinize:
            font.reload()  # DO NOT REMOVE
            logger.info("Subroutinizing...")
            otf_subroutinize(font)

        return True

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("dehint")
@drop_hinting_data_flag()
@subroutinize_flag()
@base_options()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Dehint OpenType-PS fonts.
    """

    def _task(font: Font, drop_hinting_data: bool = False, subroutinize: bool = True) -> bool:
        logger.info("Dehinting font...")
        otf_dehint(font, drop_hinting_data=drop_hinting_data)
        if subroutinize:
            logger.info("Subroutinizing...")
            otf_subroutinize(font)

        return True

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("subr")
@base_options()
def subr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def _task(font: Font) -> bool:
        logger.info("Subroutinizing...")
        return otf_subroutinize(font)

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("desubr")
@base_options()
def desubr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def _task(font: Font) -> bool:
        logger.info("Desubroutinizing...")
        return otf_desubroutinize(font)

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("check-outlines")
@subroutinize_flag()
@base_options()
def check_outlines(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Check the outlines of OpenType-PS fonts with ``afdko.checkoutlinesufo``.
    """

    def _task(font: Font, subroutinize: bool = True) -> bool:
        logger.info("Checking outlines")
        otf_check_outlines(font)
        if subroutinize:
            logger.info("Subroutinizing")
            otf_subroutinize(font)

        return True

    runner = TaskRunner(input_path=input_path, task=_task, **options)
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

    def _task(font: Font, subroutinize: bool = True, drop_hinting_data: bool = False) -> bool:
        logger.info("Rounding coordinates")
        result = font.t_cff_.round_coordinates(drop_hinting_data=drop_hinting_data)
        if not result:
            return False

        logger.info(f"{len(result)} glyphs were modified")

        if subroutinize:
            logger.info("Subroutinizing")
            otf_subroutinize(font)

        return True

    runner = TaskRunner(input_path=input_path, task=_task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()
