from pathlib import Path

import click

from foundrytools_cli_2.lib.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
)
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderError,
    FontFinderFilters,
    FontLoadOptions,
)
from foundrytools_cli_2.lib.timer import Timer

cli = click.Group()


@cli.command("print")
@input_path_argument()
@recursive_flag()
@recalc_timestamp_flag()
@Timer()
def print_font_name(
        input_path: Path, recursive: bool = False, recalc_timestamp: bool = False
) -> None:
    """
    Print the name of the font file.

    \f
    :param input_path: A path to a font file or a directory containing font files.
    :param recursive: A boolean indicating whether to search for fonts recursively in
        subdirectories.
    :param recalc_timestamp: A boolean indicating whether to recalculate the font's
        modified timestamp on save.
    :return: None
    """
    filters = FontFinderFilters(filter_out_tt=True)
    options = FontLoadOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.find_fonts()
        for font in fonts:
            with font:
                print(font.reader.file.name)
    except FontFinderError as e:
        print(e)
