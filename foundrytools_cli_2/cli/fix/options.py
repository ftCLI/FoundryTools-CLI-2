import typing as t

import click

from foundrytools_cli_2.cli.shared_options import add_options


def keep_hinting_flag() -> t.Callable:
    """
    Returns a decorator that adds the --no-remove-hinting option to a click command. The option is
    a flag that can be used to keep the hinting of a TrueType font when the contours are modified.

    Returns:
        t.Callable: The decorator to add the option to a click command
    """
    _keep_hinting_flag = [
        click.option(
            "--keep-hinting",
            "remove_hinting",
            is_flag=True,
            default=True,
            help="Keep hinting for unmodified glyphs, default is to drop hinting",
        )
    ]
    return add_options(_keep_hinting_flag)


def ignore_errors_flag() -> t.Callable:
    """
    Returns a decorator that adds the --ignore-errors option to a click command. The option is a
    flag that can be used to ignore errors when processing the font files.

    Returns:
        t.Callable: The decorator to add the option to a click command
    """
    _ignore_errors_flag = [
        click.option(
            "--ignore-errors",
            is_flag=True,
            help="""
            Ignore errors while correcting contours, thus keeping the tricky glyphs unchanged.
            """,
        )
    ]
    return add_options(_ignore_errors_flag)


def keep_unused_subroutines_flag() -> t.Callable:
    """
    Returns a decorator that adds the --remove-unused-subroutines option to a click command. The
    option is a flag that can be used to remove unused subroutines from a PostScript font.

    Returns:
        t.Callable: The decorator to add the option to a click command
    """
    _keep_unused_subroutines_flag = [
        click.option(
            "--keep-unused-subroutines",
            "remove_unused_subroutines",
            is_flag=True,
            default=True,
            help="""
            Keep unused subroutines in CFF table after removing overlaps, default is to remove them
            if any glyphs are modified.
            """,
        )
    ]
    return add_options(_keep_unused_subroutines_flag)


def min_area_option() -> t.Callable:
    """
    Returns a decorator that adds the --min-area option to a click command. The option is used to
    remove tiny paths with area less than the specified value.

    Returns:
        t.Callable: A decorator that adds the ``min_area`` option to a click command
    """
    _min_area_option = [
        click.option(
            "-ma",
            "--min-area",
            type=click.IntRange(min=0),
            default=25,
            help="Remove tiny paths with area less than the specified value.",
        )
    ]
    return add_options(_min_area_option)
