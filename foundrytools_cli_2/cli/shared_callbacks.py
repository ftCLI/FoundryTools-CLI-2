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

    Args:
        ctx (click.Context): click Context
        _: click Parameter
        value (t.Optional[Path]): The value to convert

    Returns:
        t.Optional[Path]: The converted value
    """

    # if the value is None or the click context is resilient, return None
    if not value or ctx.resilient_parsing:
        return None
    # try to create the output directory if it doesn't exist
    try:
        value.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise click.BadParameter(f"Could not create output directory: {e}") from e
    # check if the output directory is writable
    if not os.access(value, os.W_OK):
        raise click.BadParameter(f"Output directory is not writable: {value}")
    return value


def choice_to_int_callback(
    ctx: click.Context, _: click.Parameter, value: t.Union[str, t.Tuple[str, ...]]
) -> t.Optional[t.Union[int, t.Tuple[int, ...]]]:
    """
    Callback for click options that accept a choice. Converts the choice to an integer or a tuple
    of integers.

    If the value is None or the click context is resilient, returns None. If the parameter is
    multiple, converts a click choice tuple of strings to a tuple of integers. Otherwise, converts
    a click choice string to an integer.

    Args:
        ctx (click.Context): click Context
        _: click Parameter
        value (t.Union[str, t.Tuple[str, ...]]): The value to convert

    Returns:
        t.Optional[t.Union[int, t.Tuple[int, ...]]]: The converted value
    """

    # we do not check if the values can be converted to integers here because the click.Choice
    # should be correctly built.

    def _to_int(val: str) -> int:
        return int(val)

    if not value or ctx.resilient_parsing:
        return None
    if isinstance(value, tuple):
        return tuple(_to_int(v) for v in value)
    return _to_int(value)


def tuple_to_set_callback(
    ctx: click.Context, _: click.Parameter, value: t.Tuple[t.Any, ...]
) -> t.Set[t.Any]:
    """
    Callback for click options that accept a tuple. Converts the tuple to a set.

    If the value is None or the click context is resilient, returns None. Otherwise, converts the
    tuple to a set.

    Args:
        ctx (click.Context): click Context
        _: click Parameter
        value (t.Tuple[t.Any, ...]): The value to convert

    Returns:
        t.Set[t.Any]: The converted value
    """

    if not value or ctx.resilient_parsing:
        return set()
    return set(value)


def ensure_at_least_one_param(ctx: click.Context) -> None:
    """
    Checks if any attributes are provided to set, except for the ignored ones.
    """
    ignored = ["input_path", "output_dir", "recursive", "recalc_timestamp", "overwrite"]

    if all(value is None for key, value in ctx.params.items() if key not in ignored):
        raise click.UsageError("No attributes provided to set.")
