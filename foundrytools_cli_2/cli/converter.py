from pathlib import Path
from typing import Optional

from cffsubr import subroutinize
import click

from foundrytools_cli_2.lib.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
    overwrite_flag,
    output_dir_option,
    target_upm_option,
    tolerance_option,
    subroutinize_flag,
    debug_flag,
)
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderError,
    FontFinderFilters,
    FontLoadOptions,
)
from foundrytools_cli_2.lib.logger import logger, logger_filter
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.snippets.otf_to_ttf import otf_to_ttf
from foundrytools_cli_2.snippets.ttf_to_otf import ttf_to_otf, get_charstrings

cli = click.Group()


@cli.command("otf2ttf")
@input_path_argument()
@recursive_flag()
@tolerance_option()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@Timer(logger=logger.info)
def ps2tt(
    input_path: Path,
    recursive: bool = False,
    tolerance: float = 1.0,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """

    filters = FontFinderFilters(filter_out_tt=True, filter_out_variable=True)
    options = FontLoadOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.generate_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        with font:
            try:
                logger.info(f"Converting {font.reader.file.name}")
                tt = otf_to_ttf(font=font, max_err=tolerance, reverse_direction=True)
                out_file = tt.get_output_file(output_dir=output_dir, overwrite=overwrite)
                font.save(out_file)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("ttf2otf")
@input_path_argument()
@recursive_flag()
@tolerance_option()
@target_upm_option()
@subroutinize_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def tt2ps(
    input_path: Path,
    recursive: bool = False,
    tolerance: float = 1.0,
    subr: bool = True,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    target_upm: Optional[int] = None,
    recalc_timestamp: bool = False,
    debug: bool = False,
) -> None:
    """
    Convert TrueType flavored fonts to PostScript flavored fonts.
    """

    if debug:
        logger_filter.level = "DEBUG"

    filters = FontFinderFilters(filter_out_ps=True, filter_out_variable=True)
    options = FontLoadOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort()

    for font in fonts:
        with font, Timer(logger=logger.success, text="Font converted in {:0.3f} seconds"):
            try:
                logger.info(f"Converting {font.reader.file.name}")

                logger.info("Decomponentizing source font...")
                font.tt_decomponentize()

                if target_upm:
                    logger.info(f"Scaling UPM to {target_upm}")
                    font.tt_scale_upm(units_per_em=target_upm)

                logger.info("Getting charstrings...")
                charstrings = get_charstrings(font=font, tolerance=tolerance)

                logger.info("Converting to OTF...")
                otf = ttf_to_otf(font=font, charstrings=charstrings)
                out_file = otf.get_output_file(output_dir=output_dir, overwrite=overwrite)

                if subr:
                    logger.info("Subroutinizing...")
                    # Save the flavor and set it to None to avoid cffsubr to fail
                    if otf.flavor is not None:
                        flavor = otf.flavor
                    otf.flavor = None
                    subroutinize(otf)
                    if locals().get("flavor"):
                        otf.flavor = flavor

                    # Using compreffor requires to save the font to a buffer first
                    # from io import BytesIO
                    # with BytesIO() as buf:
                    #     buf = BytesIO()
                    #     otf.save(buf)
                    #     buf.seek(0)
                    #     otf = Font(buf)
                    #     compress(otf)

                otf.save(out_file)

                logger.success(f"Saved {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)
