import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.options import add_options
from foundrytools_cli_2.cli.options.callbacks import output_dir_callback


def base_options() -> t.Callable:
    """
    Add the common options to a click command.

    :return: a decorator that adds the common options to a click command
    """

    return add_options(
        [
            input_path_argument(),
            recursive_flag(),
            output_dir_option(),
            overwrite_flag(),
            recalc_timestamp_flag(),
        ]
    )


def input_path_argument(dir_okay: bool = True, file_okay: bool = True) -> t.Callable:
    """
    Add the ``input_path`` argument to a click command.

    The ``input_path`` argument is the path to a font file or to a directory containing font files.
    If ``input_path`` is a directory, all the font files stored in it, and matching the eventual
    criteria, will be processed. If ``input_path`` is a file, only that file will be processed.
    Users can specify whether the argument can be a directory or a file.

    :param dir_okay: if False, the argument can't be a file
    :param file_okay: if False, the argument can be a directory
    :return: a decorator that adds the input_path argument to a click command
    """
    _file_or_path_argument = [
        click.argument(
            "input_path",
            type=click.Path(
                exists=True,
                resolve_path=True,
                path_type=Path,
                dir_okay=dir_okay,
                file_okay=file_okay,
            ),
        )
    ]
    return add_options(_file_or_path_argument)


def recursive_flag() -> t.Callable:
    """
    Add the recursive option to a click command.

    :return: a decorator that adds the recursive flag to a click command
    """
    _recursive_flag = [
        click.option(
            "-r",
            "--recursive",
            is_flag=True,
            default=False,
            help="""
            When ``input_path`` is a directory, the font finder will search for fonts recursively in
            subdirectories.
            """,
        )
    ]
    return add_options(_recursive_flag)


def lazy_flag() -> t.Callable:
    """
    Add the lazy option to a click command.

    :return: a decorator that adds the lazy flag to a click command
    """
    _lazy_flag = [
        click.option(
            "--lazy/--no-lazy",
            default=None,
            help="""
            If lazy is set to True, many data structures are loaded lazily, upon access only. If it
            is set to False, many data structures are loaded immediately. The default is
            ``lazy=None`` which is somewhere in between.
            """,
        )
    ]
    return add_options(_lazy_flag)


def output_dir_option() -> t.Callable:
    """
    Add the output_dir option to a click command.

    :return: a decorator that adds the output_dir option to a click command
    """
    _output_dir_option = [
        click.option(
            "-out",
            "--output-dir",
            type=click.Path(path_type=Path, file_okay=False, resolve_path=True),
            default=None,
            callback=output_dir_callback,
            help="""
            Specify a directory where the output files are to be saved. If the output directory
            doesn't exist, it will be automatically created. If not specified, files will be saved
            to the source directory.
            """,
        )
    ]
    return add_options(_output_dir_option)


def overwrite_flag() -> t.Callable:
    """
    Add the overwrite option to a click command.

    :return: a decorator that adds the overwrite option to a click command
    """
    _overwrite_flag = [
        click.option(
            "--no-overwrite",
            "overwrite",
            is_flag=True,
            default=True,
            help="""
            Use this flag to avoid overwriting existing files, but save them to a new file by adding
            numbers at the end of file name. By default, files are overwritten.
            """,
        )
    ]
    return add_options(_overwrite_flag)


def recalc_timestamp_flag() -> t.Callable:
    """
    Add the recalc_timestamp option to a click command.

    :return: a decorator that adds the recalc_timestamp option to a click command
    """
    _recalc_timestamp_flag = [
        click.option(
            "--recalc-timestamp",
            is_flag=True,
            default=False,
            help="""
            Use this flag to recalculate the ``modified`` timestamp in the ``head`` table on save.
            By default, the ``modified`` timestamp is kept.
            """,
        )
    ]
    return add_options(_recalc_timestamp_flag)


def recalc_bboxes_flag() -> t.Callable:
    """
    Add the recalc_bboxes option to a click command.

    :return: a decorator that adds the recalc_bboxes option to a click command
    """
    _recalc_bboxes_flag = [
        click.option(
            "--no-recalc-bboxes",
            "recalc_bboxes",
            is_flag=True,
            default=True,
            help="""
            Use this flag to avoid recalculating the bounding boxes of all glyphs on save. By
            default, bounding boxes are recalculated.
            """,
        )
    ]
    return add_options(_recalc_bboxes_flag)


def reorder_tables_flag() -> t.Callable:
    """
    Add the reorder_tables option to a click command.

    :return: a decorator that adds the reorder_tables option to a click command
    """
    _reorder_tables_flag = [
        click.option(
            "--reorder-tables/--no-reorder-tables",
            default=True,
            help="""
            Reorder the font's tables on save. If true (the default), reorder the tables, sorting
            them by tag (recommended by the OpenType specification). If False, retain the original
            font order. If None, reorder by table dependency (fastest).
            """,
        )
    ]
    return add_options(_reorder_tables_flag)


def debug_flag() -> t.Callable:
    """
    Add the debug option to a click command.

    :return: a decorator that adds the debug option to a click command
    """
    _debug_flag = [
        click.option(
            "--debug/--no-debug",
            default=False,
            help="""
            Use this flag to enable debug mode. By default, debug mode is disabled.
            """,
        )
    ]
    return add_options(_debug_flag)


def target_upm_option(
    required: bool = False,
    help_msg: str = "Scale the font to the specified UPM.",
) -> t.Callable:
    """
    Add the scale_upm option to a click command.

    :return: a decorator that adds the scale_upm option to a click command
    """
    _target_upm_option = [
        click.option(
            "-upm",
            "--target-upm",
            type=click.IntRange(min=16, max=16384),
            default=None,
            required=required,
            help=help_msg,
        )
    ]
    return add_options(_target_upm_option)
