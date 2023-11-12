from pathlib import Path
from typing import Literal, Optional

import click

from foundrytools_cli_2.lib.constants import (
    TTFontOptions,
    WOFF_FLAVOR,
    WOFF2_FLAVOR,
    OTF_EXTENSION,
    TTF_EXTENSION,
)

from foundrytools_cli_2.lib.click.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
    overwrite_flag,
    output_dir_option,
    target_upm_option,
    tolerance_option,
    subroutinize_flag,
    debug_flag,
    in_flavor_choice,
    out_flavor_choice,
)
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderError,
    FontFinderFilter,
)
from foundrytools_cli_2.lib.logger import logger, logger_filter
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.snippets.ps2tt import otf_to_ttf
from foundrytools_cli_2.snippets.tt2ps import ttf_to_otf, get_charstrings

timer = Timer(
    logger=logger.opt(colors=True).info,
    text="Font converted in <cyan>{:0.3f} seconds</>",
)

cli = click.Group()


@cli.command("otf2ttf")
@input_path_argument()
@recursive_flag()
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@Timer(logger=logger.info)
def otf2ttf(
    input_path: Path,
    recursive: bool = False,
    tolerance: float = 1.0,
    target_upm: Optional[int] = None,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """

    filters = FontFinderFilter(filter_out_tt=True, filter_out_variable=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.generate_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort(e)

    for font in fonts:
        print()
        with font:
            try:
                timer.start()
                logger.info(f"Converting {font.file}")
                tt = otf_to_ttf(font=font, max_err=tolerance, reverse_direction=True)
                if target_upm:
                    logger.info(f"Scaling UPM to {target_upm}")
                    tt.tt_scale_upem(new_upem=target_upm)
                if font.ttfont.flavor is not None:
                    suffix = TTF_EXTENSION
                else:
                    suffix = ""
                out_file = tt.get_output_file(
                    output_dir=output_dir,
                    overwrite=overwrite,
                    suffix=suffix,
                )
                font.save(out_file)
                timer.stop()
                logger.success(f"Saved {out_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("ttf2otf")
@input_path_argument()
@recursive_flag()
@tolerance_option()
@target_upm_option(help_msg="Scale the converted fonts to the specified UPM.")
@subroutinize_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def ttf2otf(
    input_path: Path,
    recursive: bool = False,
    tolerance: float = 1.0,
    subroutinize: bool = True,
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

    filters = FontFinderFilter(filter_out_ps=True, filter_out_variable=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort()

    for font in fonts:
        print()
        with font:
            try:
                timer.start()
                logger.info(f"Converting {font.file}")

                logger.info("Decomponentizing source font...")
                font.tt_decomponentize()

                if target_upm:
                    logger.info(f"Scaling UPM to {target_upm}")
                    font.tt_scale_upem(new_upem=target_upm)

                logger.info("Getting charstrings...")
                charstrings = get_charstrings(font=font, tolerance=tolerance)

                logger.info("Converting to OTF...")
                otf = ttf_to_otf(font=font, charstrings=charstrings)

                if subroutinize:
                    logger.info("Subroutinizing...")
                    otf.ps_subroutinize()

                if font.ttfont.flavor is not None:
                    suffix = OTF_EXTENSION
                else:
                    suffix = ""
                out_file = otf.get_output_file(
                    output_dir=output_dir, overwrite=overwrite, suffix=suffix
                )
                otf.save(out_file)
                timer.stop()
                logger.success(f"Saved {out_file}")

            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)

    print()  # Add a newline after the last font before the timer message


@cli.command("wf2ft")
@input_path_argument()
@recursive_flag()
@in_flavor_choice()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@Timer(logger=logger.info)
def wf2sfnt(
    input_path: Path,
    recursive: bool = False,
    in_flavor: Optional[Literal["woff", "woff2"]] = None,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Convert WOFF/WOFF2 flavored fonts to SFNT fonts.
    """

    filters = FontFinderFilter(filter_out_sfnt=True)
    if in_flavor == "woff":
        filters.filter_out_woff2 = True
    if in_flavor == "woff2":
        filters.filter_out_woff = True

    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort()

    for font in fonts:
        print()
        with font:
            try:
                timer.start()
                logger.info(f"Converting {font.file}")
                suffix = font.real_extension  # See note below
                font.ttfont.flavor = None

                # What happens if we convert a WOFF and a WOFF2 with the same stem and the same
                # sfntVersion? The file converted first will be overwritten by the second one.
                # We need to add the suffix retrieved few lines above to avoid this.
                out_file = font.get_output_file(
                    output_dir=output_dir, overwrite=overwrite, suffix=suffix
                )
                font.save(out_file, reorder_tables=False)
                timer.stop()
                logger.success(f"Saved {out_file}")

            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)


@cli.command("ft2wf")
@input_path_argument()
@recursive_flag()
@out_flavor_choice()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@Timer(logger=logger.info)
def sfnt2wf(
    input_path: Path,
    recursive: bool = False,
    out_flavor: Optional[Literal["woff", "woff2"]] = None,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Convert SFNT fonts to WOFF/WOFF2 flavored fonts.
    """

    filters = FontFinderFilter(filter_out_woff=True, filter_out_woff2=True)
    options = TTFontOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()

    except FontFinderError as e:
        logger.error(e)
        raise click.Abort()

    for font in fonts:
        print()
        with font:
            try:
                logger.info(f"Converting {font.file}")

                suffix = font.real_extension
                out_flavors = [WOFF_FLAVOR, WOFF2_FLAVOR]
                if out_flavor:
                    out_flavors = [out_flavor]

                if WOFF_FLAVOR in out_flavors:
                    timer.start()
                    logger.info("Converting to WOFF...")
                    font.ttfont.flavor = WOFF_FLAVOR
                    out_file = font.get_output_file(
                        output_dir=output_dir, overwrite=overwrite, suffix=suffix
                    )
                    font.save(out_file, reorder_tables=False)
                    timer.stop()
                    logger.success(f"Saved {out_file}")

                if WOFF2_FLAVOR in out_flavors:
                    timer.start()
                    logger.info("Converting to WOFF2...")
                    font.ttfont.flavor = WOFF2_FLAVOR
                    out_file = font.get_output_file(
                        output_dir=output_dir, overwrite=overwrite, suffix=suffix
                    )
                    font.save(out_file, reorder_tables=False)
                    timer.stop()
                    logger.success(f"Saved {out_file}")

            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)
