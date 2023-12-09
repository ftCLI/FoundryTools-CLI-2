from pathlib import Path
from typing import Optional

import click

from foundrytools_cli_2.lib.click.click_options import (
    common_options,
    subroutinize_flag,
    min_area_option,
)
from foundrytools_cli_2.lib.constants import FontInitOptions
from foundrytools_cli_2.lib.font_finder import FontFinder, FinderError, FinderFilter
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.snippets.ps_correct_contours import correct_otf_contours


cli = click.Group()


@cli.command("fix-contours")
@min_area_option()
@subroutinize_flag()
@common_options()
def fix_contours(
    input_path: Path,
    recursive: bool = False,
    min_area: int = 25,
    subroutinize: bool = True,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Fix the contours of OpenType-PS fonts by removing overlaps, correcting contours direction, and
    removing tiny paths.
    """

    filters = FinderFilter()
    filters.filter_out_tt = True
    filters.filter_out_variable = True
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
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Correcting contours...")
                correct_otf_contours(font, min_area=min_area)
                if subroutinize:
                    logger.info("Subroutinizing...")
                    font.ps_subroutinize()
                output_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)
                font.ttfont.save(output_file)
                logger.success(f"File saved to {output_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(e)


@cli.command("subr")
@common_options()
def subr(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Subroutinize OpenType-PS fonts with ``cffsubr``.
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
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Subroutinizing...")
                font.ps_subroutinize()
                out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
                logger.success(f"File saved to {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("desubr")
@common_options()
@Timer(logger=logger.info)
def desubr(
    input_path: Path,
    recursive: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Desubroutinize OpenType-PS fonts with ``cffsubr``.
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
        with font:
            try:
                print()
                logger.info(f"Checking file {font.file}")
                logger.info("Desubroutinizing...")
                font.ps_desubroutinize()
                out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
                logger.success(f"File saved to {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


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
