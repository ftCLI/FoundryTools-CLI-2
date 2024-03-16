# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.os_2.options import (
    set_attrs_options,
    set_fs_selection_options,
    set_fs_type_options,
)
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Utilities for editing the OS/2 table.")


@cli.command("recalc-avg-width")
@base_options()
def recalc_avg_char_width(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the xAvgCharWidth value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_avg_char_width as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-x-height")
@base_options()
def recalc_x_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sxHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_x_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-cap-height")
@base_options()
def recalc_cap_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sCapHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_cap_height as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-max-context")
@base_options()
def recalc_max_context(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the usMaxContext value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_max_context as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-unicode-ranges")
@base_options()
def recalc_unicode_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulUnicodeRange values of the OS/2 table.

    The ulUnicodeRanges values are calculated using the fontTools library.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_unicode_ranges as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-codepage-ranges")
@base_options()
def recalc_codepage_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulCodePageRange values of the OS/2 table.

    The ulCodePageRanges values are calculated using the fontTools library.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_codepage_ranges as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("recalc-ranges-afdko")
@base_options()
def recalc_ranges_afdko(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulUnicodeRange and ulCodePageRange values of the OS/2 table using AFDKO.

    The font is first converted to T1, then to OTF. The ulUnicodeRange and ulCodePageRange values
    are then retrieved from the OS/2 table of the OTF font and written to the original font.
    """
    from foundrytools_cli_2.cli.os_2.snippets import recalc_ranges_afdko as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("set-attrs")
@set_attrs_options()
@base_options()
def set_attrs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets miscellaneous attributes of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import set_attrs as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("fs-selection")
@set_fs_selection_options()
@base_options()
def set_fs_selection(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets flags in the fsSelection field of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import set_fs_selection as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()


@cli.command("fs-type")
@set_fs_type_options()
@base_options()
def set_fs_type(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set font embedding licensing rights for the font, defined in the fsType field of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.snippets import set_fs_type as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
