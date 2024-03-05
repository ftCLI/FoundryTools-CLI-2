# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.options import common_options
from foundrytools_cli_2.lib.click.os_2_options import (
    set_attrs_options,
    set_fs_selection_options,
    set_fs_type_options,
)
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the OS/2 table.")


@cli.command("recalc-avg-width")
@common_options()
def recalc_avg_char_width(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the xAvgCharWidth value of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_avg_char_width as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-x-height")
@common_options()
def recalc_x_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sxHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_x_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-cap-height")
@common_options()
def recalc_cap_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sCapHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_cap_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-max-context")
@common_options()
def recalc_max_context(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the usMaxContext value of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_max_context as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("set-attrs")
@set_attrs_options()
@common_options()
def set_attrs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets miscellaneous attributes of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import set_attrs as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("set-fs-selection")
@set_fs_selection_options()
@common_options()
def set_fs_selection(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets flags in the fsSelection field of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import set_fs_selection as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("set-fs-type")
@set_fs_type_options()
@common_options()
def set_fs_type(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set font embedding licensing rights for the font, defined in the fsType field of the OS/2 table.
    """
    from foundrytools_cli_2.snippets.os_2 import set_fs_type as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
