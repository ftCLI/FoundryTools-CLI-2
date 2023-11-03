from pathlib import Path

import click

from foundrytools_cli_2.lib.click_options import (
    input_path_argument,
    recursive_flag,
    recalc_timestamp_flag,
    overwrite_flag,
    output_dir_option,
)
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderError,
    FontFinderFilters,
    FontLoadOptions,
)
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.snippets.otf_to_ttf import otf_to_ttf

cli = click.Group()


@cli.command("ttf2otf")
@input_path_argument()
@recursive_flag()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
@Timer()
def ttf2otf(
    input_path: Path,
    recursive: bool = False,
    output_dir: Path = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
):
    """
    Convert TrueType fonts to OpenType fonts.
    """
    filters = FontFinderFilters(filter_out_tt=True, filter_out_variable=True)
    options = FontLoadOptions(recalc_timestamp=recalc_timestamp)
    try:
        finder = FontFinder(
            input_path=input_path, recursive=recursive, options=options, filters=filters
        )
        fonts = finder.generate_fonts()
        for font in fonts:
            with font:
                try:
                    print(font.reader.file.name)
                    otf_to_ttf(font=font)
                    out_file = font.get_output_file(output_dir=output_dir, overwrite=overwrite)
                    font.save(out_file)
                except Exception as e:
                    print(e)
    except FontFinderError as e:
        print(e)
