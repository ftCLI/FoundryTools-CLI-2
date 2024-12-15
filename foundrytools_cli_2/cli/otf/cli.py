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
from foundrytools.utils.path_tools import get_temp_file_path

from foundrytools_cli_2.cli.base_command import BaseCommand
from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.otf.options import drop_hinting_data_flag, otf_autohint_options
from foundrytools_cli_2.cli.shared_options import subroutinize_flag
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing OpenType-PS fonts.")


@cli.command("autohint", cls=BaseCommand)
@otf_autohint_options()
@subroutinize_flag()
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


@cli.command("dehint", cls=BaseCommand)
@drop_hinting_data_flag()
@subroutinize_flag()
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


@cli.command("subr", cls=BaseCommand)
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


@cli.command("desubr", cls=BaseCommand)
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


@cli.command("check-outlines", cls=BaseCommand)
@subroutinize_flag()
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


@cli.command("round-coordinates", cls=BaseCommand)
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


@cli.command("recalc-stems", cls=BaseCommand)
def recalc_stems(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculate the hinting stems of OpenType-PS fonts.
    """
    from foundrytools.app.otf_recalc_stems import run as get_stems
    def task(font: Font) -> bool:
        if not font.is_ps:
            logger.error("Font is not a PostScript font")
            return False

        if font.file is None:
            logger.error("Font has no file path")
            return False

        flavor = font.ttfont.flavor
        temp_file = get_temp_file_path()
        if flavor is not None:
            font.ttfont.flavor = None
            font.save(font.temp_file)
            input_file = font.temp_file
        else:
            input_file = font.file

        logger.info("Getting stems...")

        current_std_h_w = font.t_cff_.get_hinting_data().get("StdHW", None)
        current_std_v_w = font.t_cff_.get_hinting_data().get("StdVW", None)
        current_stem_snap_h = font.t_cff_.get_hinting_data().get("StemSnapH", None)
        current_stem_snap_v = font.t_cff_.get_hinting_data().get("StemSnapV", None)

        std_h_w, std_v_w, stem_snap_h, stem_snap_v = get_stems(input_file)
        logger.info(f"StdHW: {current_std_h_w} -> {std_h_w}")
        logger.info(f"StdVW: {current_std_v_w} -> {std_v_w}")
        logger.info(f"StemSnapH: {current_stem_snap_h} -> {stem_snap_h}")
        logger.info(f"StemSnapV: {current_stem_snap_v} -> {stem_snap_v}")
        temp_file.unlink(missing_ok=True)

        if (current_std_h_w, current_std_v_w, current_stem_snap_h, current_stem_snap_v) == (std_h_w, std_v_w, stem_snap_h, stem_snap_v):
            logger.info("No changes were made")
            return False

        font.t_cff_.set_hinting_data(**{"StdHW": std_h_w, "StdVW": std_v_w, "StemSnapH": stem_snap_h, "StemSnapV": stem_snap_v})
        font.ttfont.flavor = flavor
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()