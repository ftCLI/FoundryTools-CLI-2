import typing as t

import click

from foundrytools_cli_2.cli import choice_to_int_callback, make_options


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
        4: CFF fontNames (CFF fonts only)
        5: CFF TopDict FullName (CFF fonts only)
        """,
        )
    ]
    return make_options(_rename_source_option)


def sort_by_manufacturer_flag() -> t.Callable:
    """
    Returns a decorator that adds the --sort-by-manufacturer option to a click command. The
    option is a flag that can be used to sort the font files by manufacturer.

    Returns:
        click.option: The decorator to add the option to a click command
    """
    _sort_by_manufacturer_option = [
        click.option(
            "-m",
            "--sort-by-manufacturer",
            is_flag=True,
            help="Sort the font files by manufacturer.",
        )
    ]
    return make_options(_sort_by_manufacturer_option)


def sort_by_font_revision_flag() -> t.Callable:
    """
    Returns a decorator that adds the --sort-by-font-revision option to a click command. The
    option is a flag that can be used to sort the font files by font revision.

    Returns:
        click.option: The decorator to add the option to a click command
    """
    _sort_by_font_revision_option = [
        click.option(
            "-v",
            "--sort-by-font-revision",
            is_flag=True,
            help="Sort the font files by font revision.",
        )
    ]
    return make_options(_sort_by_font_revision_option)


def sort_by_extension_flag() -> t.Callable:
    """
    Returns a decorator that adds the --sort-by-extension option to a click command. The option is a
    flag that can be used to sort the font files by extension.

    Returns:
        click.option: The decorator to add the option to a click command
    """
    _sort_by_extension_option = [
        click.option(
            "-e",
            "--sort-by-extension",
            is_flag=True,
            help="Sort the font files by extension.",
        )
    ]
    return make_options(_sort_by_extension_option)


def delete_empty_directories_flag() -> t.Callable:
    """
    Returns a decorator that adds the --delete-empty-directories option to a click command. The
    option is a flag that can be used to delete empty directories.

    Returns:
        click.option: The decorator to add the option to a click command
    """
    _delete_empty_directories_option = [
        click.option(
            "-d",
            "--delete-empty-directories",
            is_flag=True,
            help="Delete empty directories after moving the font files.",
        )
    ]
    return make_options(_delete_empty_directories_option)


def font_organizer_options() -> t.Callable:
    """
    Returns a decorator that adds the options to a click command.

    Returns:
        click.option: The decorator to add the options to a click command
    """
    return make_options(
        [
            rename_source_option(),
            sort_by_manufacturer_flag(),
            sort_by_font_revision_flag(),
            sort_by_extension_flag(),
            delete_empty_directories_flag(),
        ]
    )
