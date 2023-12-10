from pathlib import Path
from typing import Optional

import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    subroutinize_flag,
    min_area_option,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.constants import FontInitOptions
from foundrytools_cli_2.lib.font_finder import FontFinder, FinderError
from foundrytools_cli_2.lib.font_runner import FontRunner
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.lib.otf.ps_correct_contours import correct_otf_contours


cli = click.Group()


@cli.command("recalc-sz")
@common_options()
@Timer(logger=logger.info)
def recalc_stems_and_zones(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    This method recalculates stems and zones for the given font files.

    Args:
        input_path (Path): The path of the input font file or directory.
        recursive (bool, optional): Recursively search for font files in subdirectories. Defaults to
            False.
        output_dir (Path, optional): The directory to save the recalculated font files. Defaults to
            None.
        overwrite (bool, optional): Overwrite existing files with the same name. Defaults to True.
        recalc_timestamp (bool, optional): Recalculate the timestamp of the font file. Defaults to
            False.

    Returns:
        None
    """
    filters = FontFinderFilter(filter_out_tt=True, filter_out_variable=True)
    options = FontInitOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, font_options=options, font_filter=filters
        )
        fonts = finder.find_fonts()

    except FinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        print()
        with font:
            try:
                logger.info(f"Current file {font.file}")
                logger.info("Getting stems...")
                std_h_w, std_v_w = font.recalc_stems()
                logger.info(f"StdHW: {std_h_w}")
                logger.info(f"StdVW: {std_v_w}")

                font.set_stems(std_h_w, std_v_w)

                logger.info("Getting zones...")
                other_blues, blue_values = font.recalc_zones()
                logger.info(f"OtherBlues: {other_blues}")
                logger.info(f"BlueValues: {blue_values}")

                font.set_zones(other_blues, blue_values)

                out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
                logger.success(f"File saved to {out_file}")

            except Exception as e:  # pylint: disable=broad-except
                logger.exception(e)


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

    runner = FontRunner(task=correct_otf_contours, task_name="Fixing contours of", **options)
    runner.font_filter.filter_out_tt = True
    runner.run()


def recalc_stems(font: Font) -> None:
    std_h_w, std_v_w = font.recalc_stems()
    logger.info(f"StdHW: {std_h_w}")
    logger.info(f"StdVW: {std_v_w}")

    font.set_stems(std_h_w, std_v_w)


