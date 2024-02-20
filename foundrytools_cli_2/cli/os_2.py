# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.callbacks import choice_to_int_callback
from foundrytools_cli_2.lib.click.options import common_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the OS/2 table.", chain=True)


@cli.command("set-fs-type")
@click.option(
    "-el",
    "--embed-level",
    type=click.Choice(["0", "2", "4", "8"]),
    callback=choice_to_int_callback,
    help="The new fsType value.",
)
@click.option("--bmp-only/--no-bmp-only", default=None, help="Set the fsType value to 0.")
@click.option("--no-subsetting/--allow-subsetting", default=None, help="Set the fsType value to 2.")
@common_options()
def set_fs_type(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the fsType value of the OS/2 table of the given font files.
    """
    from foundrytools_cli_2.snippets.os_2 import set_permissions as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-x-height")
@common_options()
def recalc_x_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculate the xHeight value of the OS/2 table of the given font files.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_x_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-cap-height")
@common_options()
def recalc_cap_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculate the capHeight value of the OS/2 table of the given font files.
    """
    from foundrytools_cli_2.snippets.os_2 import recalc_cap_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
