import os
import typing as t
from pathlib import Path

import click


def output_dir_callback(
    ctx: click.Context, _: click.Parameter, value: t.Optional[Path]
) -> t.Optional[Path]:
    """
    Callback for ``--output-dir option``.

    Tries to create the output directory if it doesn't exist. Checks if the output directory is
    writable. Returns a Path object. If the callback fails, raises a click.BadParameter exception.

    :param ctx: click Context
    :param _: click Parameter. Not used
    :param value: a Path object or None
    :return: a Path object representing the output directory
    """

    # if the value is None or the click context is resilient, return None
    if not value or ctx.resilient_parsing:
        return None
    # try to create the output directory if it doesn't exist
    try:
        value.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise click.BadParameter(f"Could not create output directory: {e}")
    # check if the output directory is writable
    if not os.access(value, os.W_OK):
        raise click.BadParameter(f"Output directory is not writable: {value}")
    return value


# def choice_to_int_callback(
#     ctx: click.Context, param: click.Parameter, value: t.Union[str, t.Tuple[str]]
# ) -> t.Optional[t.Union[int, t.Tuple[int, ...]]]:
#     """
#     Callback for click options that accept a choice. Converts the choice to an integer or a tuple
#     of integers.
#
#     If the value is None or the click context is resilient, returns None. If the parameter is
#     multiple, converts a click choice tuple of strings to a tuple of integers. Otherwise, converts
#     a click choice string to an integer.
#     :param ctx: click Context
#     :param param: click Parameter
#     :param value: string or tuple of strings to convert
#     :return: an integer or a tuple of integers
#     """
#
#     # we do not check if the values can be converted to integers here because the click.Choice
#     # should be correctly built.
#     if not value or ctx.resilient_parsing:
#         return None
#     if param.multiple:
#         return tuple(sorted(set(int(v) for v in value)))
#     return int(value)
#
#
# def str_to_tuple_callback(
#     ctx: click.Context, _: click.Parameter, value: t.Optional[str]
# ) -> t.Optional[t.Tuple[str, ...]]:
#     """
#     Callback for click options that accept a tuple of strings. Converts a string to a tuple of
#     strings.
#
#     If the value is None or the click context is resilient, returns None. Otherwise, converts a
#     string to a tuple of strings.
#
#     :param ctx: click Context
#     :param _: click Parameter. Not used
#     :param value: string to convert
#     :return: a tuple of strings
#     """
#
#     if not value or ctx.resilient_parsing:
#         return None
#     return tuple(value.split(","))
