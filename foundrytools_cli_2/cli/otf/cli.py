# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click
from foundrytools import Font
from foundrytools.app.otf_autohint import run as otf_autohint
from foundrytools.app.otf_check_outlines import run as otf_check_outlines
from foundrytools.app.otf_dehint import run as otf_dehint
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

    def task(font: Font, subroutinize: bool = True, **kwargs: t.Dict[str, t.Any]) -> bool:
        logger.info("Autohinting...")
        otf_autohint(font, **kwargs)

        if subroutinize:
            font.reload()  # DO NOT REMOVE
            logger.info("Subroutinizing...")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("dehint", cls=BaseCommand)
@drop_hinting_data_flag()
@subroutinize_flag()
def dehint(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Dehint OpenType-PS fonts.
    """

    def task(font: Font, drop_hinting_data: bool = False, subroutinize: bool = True) -> bool:
        logger.info("Dehinting font...")
        otf_dehint(font, drop_hinting_data=drop_hinting_data)
        if subroutinize:
            logger.info("Subroutinizing...")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("subr", cls=BaseCommand)
def subr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def task(font: Font) -> bool:
        logger.info("Subroutinizing...")
        return font.subroutinize()

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("desubr", cls=BaseCommand)
def desubr(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    def task(font: Font) -> bool:
        logger.info("Desubroutinizing...")
        return font.desubroutinize()

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.run()


@cli.command("check-outlines", cls=BaseCommand)
@subroutinize_flag()
def check_outlines(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Check the outlines of OpenType-PS fonts with ``afdko.checkoutlinesufo``.
    """

    def task(font: Font, subroutinize: bool = True) -> bool:
        logger.info("Checking outlines")
        otf_check_outlines(font)
        if subroutinize:
            logger.info("Subroutinizing")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("round-coordinates", cls=BaseCommand)
@subroutinize_flag()
def round_coordinates(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Round the coordinates of OpenType-PS fonts.
    """

    def task(font: Font, subroutinize: bool = True, drop_hinting_data: bool = False) -> bool:
        logger.info("Rounding coordinates")
        result = font.t_cff_.round_coordinates(drop_hinting_data=drop_hinting_data)
        if not result:
            return False

        logger.info(f"{len(result)} glyphs were modified")

        if subroutinize:
            logger.info("Subroutinizing")
            font.subroutinize()

        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("recalc-stems", cls=BaseCommand)
@click.option(
    "-all",
    "--report-all-stems",
    is_flag=True,
    help="""
    Include stems formed by curved line segments; by default, includes only stems formed by straight
    line segments.
    """,
)
@click.option(
    "--max-distance",
    type=click.IntRange(min=0),
    default=1,
    help="""
    The maximum distance between widths to consider as part of the same group.
    """,
)
@click.option(
    "--max-h-stems",
    type=click.IntRange(min=1, max=12),
    default=2,
    help="""
    The number of horizontal stem values to extract.
    """,
)
@click.option(
    "--max-v-stems",
    type=click.IntRange(min=1, max=12),
    default=2,
    help="""
    The number of vertical stem values to extract.
    """,
)
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

        report_all_stems = t.cast(bool, options["report_all_stems"])
        max_distance = t.cast(int, options["max_distance"])
        max_h_stems = t.cast(int, options["max_h_stems"])
        max_v_stems = t.cast(int, options["max_v_stems"])
        std_h_w, std_v_w, stem_snap_h, stem_snap_v = get_stems(
            input_file,
            report_all_stems=report_all_stems,
            max_distance=max_distance,
            max_h_stems=max_h_stems,
            max_v_stems=max_v_stems,
        )
        logger.info(f"StdHW: {current_std_h_w} -> {std_h_w}")
        logger.info(f"StdVW: {current_std_v_w} -> {std_v_w}")
        logger.info(f"StemSnapH: {current_stem_snap_h} -> {stem_snap_h}")
        logger.info(f"StemSnapV: {current_stem_snap_v} -> {stem_snap_v}")
        temp_file.unlink(missing_ok=True)

        if (current_std_h_w, current_std_v_w, current_stem_snap_h, current_stem_snap_v) == (
            std_h_w,
            std_v_w,
            stem_snap_h,
            stem_snap_v,
        ):
            return False

        font.t_cff_.set_hinting_data(
            **{
                "StdHW": std_h_w,
                "StdVW": std_v_w,
                "StemSnapH": stem_snap_h,
                "StemSnapV": stem_snap_v,
            }
        )
        font.ttfont.flavor = flavor
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("recalc-zones", cls=BaseCommand)
def recalc_zones(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculate the hinting zones of OpenType-PS fonts.
    """
    from foundrytools.app.otf_recalc_zones import run as get_zones

    def task(font: Font) -> bool:
        if not font.is_ps:
            logger.error("Font is not a PostScript font")
            return False
        current_other_blues, current_blues = (
            font.t_cff_.get_hinting_data().get("OtherBlues", None),
            font.t_cff_.get_hinting_data().get("BlueValues", None),
        )
        other_blues, blue_values = get_zones(font)
        logger.info(f"BlueValues: {current_blues} -> {blue_values}")
        logger.info(f"OtherBlues: {current_other_blues} -> {other_blues}")
        if (current_other_blues, current_blues) == (other_blues, blue_values):
            return False

        font.t_cff_.set_hinting_data(**{"BlueValues": blue_values, "OtherBlues": other_blues})
        return True

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_tt = True
    runner.filter.filter_out_variable = True
    runner.run()
