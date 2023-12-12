import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    subroutinize_flag,
    min_area_option,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_runner import FontRunner
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer

cli = click.Group()


@cli.command("recalc-sz")
@common_options()
@Timer(logger=logger.info)
def recalc_zs(**options) -> None:
    """
    Recalculates hinting stems and zones for the given font files.
    """
    from foundrytools_cli_2.snippets.otf.recalc_zones_and_stems import recalc_zones_and_stems

    runner = FontRunner(
        task=recalc_zones_and_stems, task_name="Recalculating zones and stems of", **options
    )
    runner.font_filter.filter_out_tt = True
    runner.run()


@cli.command("subr")
@common_options()
def subr(**options) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(task=Font.ps_subroutinize, task_name="Subroutinizing", **options)
    runner.font_filter.filter_out_tt = True
    runner.run()


@cli.command("desubr")
@common_options()
def desubr(**options) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
    """

    runner = FontRunner(task=Font.ps_desubroutinize, task_name="Desubroutinizing", **options)
    runner.font_filter.filter_out_tt = True
    runner.run()


@cli.command("fix-contours")
@min_area_option()
@subroutinize_flag()
@common_options()
def fix_contours(**options) -> None:
    """
    Fix the contours of OpenType-PS fonts by removing overlaps, correcting contours direction, and
    removing tiny paths.
    """
    from foundrytools_cli_2.lib.otf.ps_correct_contours import correct_otf_contours

    runner = FontRunner(task=correct_otf_contours, task_name="Fixing contours of", **options)
    runner.font_filter.filter_out_tt = True
    runner.run()
