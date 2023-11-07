from pathlib import Path
from typing import Optional

import click

from foundrytools_cli_2.lib.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
    overwrite_flag,
    output_dir_option,
    debug_flag,
    subroutinize_flag,
)
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderError,
    FontFinderFilters,
    FontLoadOptions,
)
from foundrytools_cli_2.lib.logger import logger, logger_filter
from foundrytools_cli_2.lib.skia_tools import correct_otf_contours
from foundrytools_cli_2.lib.timer import Timer

cli = click.Group()


@cli.command("fix-contours")
@input_path_argument()
@recursive_flag()
@subroutinize_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@debug_flag()
@Timer(logger=logger.info)
def fix_contours(
    input_path: Path,
    recursive: bool = False,
    subroutinize: bool = True,
    debug: bool = False,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
) -> None:
    """
    Fix the contours of an OTF font.
    """

    if debug:
        logger_filter.level = "DEBUG"

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
                logger.info(f"Checking file {font.file.name}")
                correct_otf_contours(font)
                if subroutinize:
                    logger.info(f"Subroutinizing...")
                    font.ps_subroutinize()
                output_file = font.get_output_file(output_dir=output_dir, overwrite=overwrite)
                font.save(output_file)
                logger.success(f"File saved to {output_file}")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(e)
