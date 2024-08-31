import typing as t

import click

from foundrytools_cli_2.cli.shared_callbacks import choice_to_int_callback
from foundrytools_cli_2.cli.shared_options import add_options


def rename_source_option() -> t.Callable:
    """
    Returns a decorator that adds the --rename-source option to a click command. The option is a
    flag that can be used to rename the source of a font file.

    Returns:
        click.option: The decorator to add the option to a click command
    """
    _rename_source_option = [
        click.option(
            "-s",
            "--source",
            type=click.Choice(choices=["1", "2", "3", "4", "5"]),
            default="1",
            callback=choice_to_int_callback,
            help="""
        The source string(s) from which to extract the new file name. Default is 1
        (FamilyName-StyleName), used also as fallback name when 4 or 5 are passed but the font
        is TrueType

        \b
        1: FamilyName-StyleName
        2: PostScript Name
        3: Full Font Name
        4: CFF TopDict fontNames (CFF fonts only)
        5: CFF TopDict FullName (CFF fonts only)
        """,
        )
    ]
    return add_options(_rename_source_option)
