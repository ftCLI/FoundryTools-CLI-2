import typing as t

import click

from foundrytools_cli_2.cli.shared_options import add_options


def tolerance_option() -> t.Callable:
    """
    Add the ``tolerance`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``tolerance`` option to a click command
    """
    _tolerance_option = [
        click.option(
            "-t",
            "--tolerance",
            type=click.FloatRange(min=0.0, max=3.0),
            default=1.0,
            help="""
            Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps
            shapes. High tolerance adds  few points but may change shape.
            """,
        )
    ]
    return add_options(_tolerance_option)


def check_outlines_flag() -> t.Callable:
    """
    Add the ``check_outlines`` flag to a click command.

    Returns:
        t.Callable: A decorator that adds the ``check_outlines`` flag to a click command
    """
    _check_outlines_flag = [
        click.option(
            "-co/--no-co",
            "--check-outlines/--no-check-outlines",
            is_flag=True,
            default=False,
            show_default=True,
            help="""
            Check outlines for correctness. If set to False, the outlines will not be checked.
            """,
        )
    ]
    return add_options(_check_outlines_flag)


def in_format_choice() -> t.Callable:
    """
    Add the ``flavor`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``flavor`` option to a click command
    """
    _in_format_choice = [
        click.option(
            "-f",
            "--format",
            "in_format",
            type=click.Choice(["woff", "woff2"]),
            default=None,
            help="""
            By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts
            (TrueType or OpenType). Use this option to convert only woff or woff2 flavored web
            fonts.
    """,
        )
    ]
    return add_options(_in_format_choice)


def out_format_choice() -> t.Callable:
    """
    Add the ``format`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``format`` option to a click command
    """
    _out_format_choice = [
        click.option(
            "-f",
            "--format",
            "out_format",
            type=click.Choice(["woff", "woff2"]),
            default=None,
            help="""
            By default, the script converts SFNT fonts to both woff and woff2 flavored web fonts.
            Use this option to convert only to woff or woff2 flavored web fonts.
    """,
        )
    ]
    return add_options(_out_format_choice)


def ttf2otf_mode_choice() -> t.Callable:
    """
    Add the ``mode`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``mode`` option to a click command
    """
    _ttf2otf_mode_choice = [
        click.option(
            "-m",
            "--mode",
            type=click.Choice(["qu2cu", "tx"]),
            default="qu2cu",
            show_default=True,
            help="""
            Conversion mode. By default, the script uses the ``qu2cu`` mode. Quadratic curves are
            converted to cubic curves using the Qu2CuPen. Use the ``tx`` mode to use the tx tool
            from AFDKO to generate the CFF table instead of the Qu2CuPen.
            """,
        )
    ]
    return add_options(_ttf2otf_mode_choice)
