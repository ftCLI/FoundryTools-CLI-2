# pylint: disable=import-outside-toplevel
from pathlib import Path
from typing import Optional

import click
from foundrytools import FontFinder

cli = click.Group(help="Prints various font's information.")


@cli.command("font-names")
@click.argument("input_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option(
    "-ml",
    "--max-lines",
    type=click.IntRange(min=1),
    help="Maximum number of lines to print for each NameRecord",
)
@click.option(
    "-min",
    "--minimal",
    is_flag=True,
    help="""
    Prints a minimal set of NameRecords, omitting the ones with nameID not in 1, 2, 3, 4, 5, 6, 16,
    17, 18, 21, 22, 25""",
)
def print_font_names(
    input_path: Path, max_lines: Optional[int] = None, minimal: bool = False
) -> None:
    """
    Prints the name table.
    """
    from foundrytools_cli_2.cli.commands.print.print_names import main as print_names

    finder = FontFinder(input_path)
    for font in finder.generate_fonts():
        print_names(font, max_lines=max_lines, minimal=minimal)
