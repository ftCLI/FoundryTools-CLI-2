from pathlib import Path
from typing import Callable

import click


def add_options(options: list[Callable]) -> Callable:
    """
    Add options to a click command.

    Args:
        options (t.List[t.Callable]): The options to add

    Returns:
        t.Callable: A decorator that adds the options to a click command
    """

    def _add_options(func: Callable) -> Callable:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def input_path_argument(dir_okay: bool = True, file_okay: bool = True) -> Callable:
    """
    Add the ``input_path`` argument to a click command.

    The ``input_path`` argument is the path to a font file or to a directory containing font files.
    If ``input_path`` is a directory, all the font files stored in it, and matching the eventual
    criteria, will be processed. If ``input_path`` is a file, only that file will be processed.
    Users can specify whether the argument can be a directory or a file.

    Args:
        dir_okay (bool, optional): Whether the argument can be a directory. Defaults to ``True``.
        file_okay (bool, optional): Whether the argument can be a file. Defaults to ``True``.

    Returns:
        t.Callable: A decorator that adds the ``input_path argument`` to a click command
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


def recursive_flag() -> Callable:
    """
    Add the ``recursive`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``recursive`` option to a click command
    """
    _recursive_flag = [
        click.option(
            "-r",
            "--recursive",
            is_flag=True,
            default=False,
            help="""
            If ``input_path`` is a directory, the font finder will search for fonts recursively in
            subdirectories.
            """,
        )
    ]
    return add_options(_recursive_flag)
