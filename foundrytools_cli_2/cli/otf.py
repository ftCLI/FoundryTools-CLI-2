# pylint: disable=import-outside-toplevel
import typing as t

import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    subroutinize_flag,
    min_area_option,
    zones_flag,
    stems_flag,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_runner import FontRunner
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer

cli = click.Group()


@cli.command("recalc-zs")
@zones_flag()
@stems_flag()
@common_options()
@Timer(logger=logger.info)
def recalc_zs(**options: dict) -> None:
    """
    Recalculates hinting stems and zones for the given font files.
    """
    from foundrytools_cli_2.snippets.otf.recalc_zones_and_stems import recalc_zones_and_stems

    runner = FontRunner(
        task=recalc_zones_and_stems, **options
    )
    runner.finder.filter.filter_out_tt = True
    runner.run()


@cli.command("subr")
@common_options()
def subr(**options: t.Dict[str, t.Any]) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(task=Font.ps_subroutinize, **options)
    runner.finder.filter.filter_out_tt = True
    runner.run()


@cli.command("desubr")
@common_options()
def desubr(**options: t.Dict[str, t.Any]) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(task=Font.ps_desubroutinize, **options)
    runner.finder.filter.filter_out_tt = True
    runner.run()


@cli.command("fix-contours")
@min_area_option()
@subroutinize_flag()
@common_options()
def fix_contours(**options: t.Dict[str, t.Any]) -> None:
    """
    Fix the contours of OpenType-PS fonts by removing overlaps, correcting contours direction, and
    removing tiny paths.
    """
    from foundrytools_cli_2.lib.otf.ps_correct_contours import correct_otf_contours

    runner = FontRunner(task=correct_otf_contours, **options)
    runner.finder.filter.filter_out_tt = True
    runner.run()
