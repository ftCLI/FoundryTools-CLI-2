import typing as t
from pathlib import Path

import click
from fontTools.misc.roundTools import otRound
from foundrytools import Font
from foundrytools.core.tables.os_2 import InvalidOS2VersionError

from foundrytools_cli_2.cli.base_command import BaseCommand
from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.os_2.options import (
    panose_options,
    set_attrs_options,
    set_fs_selection_options,
    set_fs_type_options,
)
from foundrytools_cli_2.cli.shared_callbacks import ensure_at_least_one_param
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``OS/2`` table.")


@cli.command("recalc-avg-width", cls=BaseCommand)
def recalc_avg_char_width(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the xAvgCharWidth value of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.table.recalcAvgCharWidth(font.ttfont)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-x-height")
@click.option(
    "-gn",
    "--glyph-name",
    default="x",
    help="The glyph name to use for calculating the x-height. Default is 'x'.",
)
def recalc_x_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sxHeight value of the OS/2 table.
    """

    def task(font: Font, glyph_name: str = "x") -> bool:
        font.t_os_2.x_height = otRound(font.get_glyph_bounds(glyph_name)["y_max"])
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-cap-height", cls=BaseCommand)
@click.option(
    "-gn",
    "--glyph-name",
    default="H",
    help="The glyph name to use for calculating the cap height. Default is 'H'.",
)
def recalc_cap_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sCapHeight value of the OS/2 table.
    """

    def task(font: Font, glyph_name: str = "H") -> bool:
        font.t_os_2.cap_height = otRound(font.get_glyph_bounds(glyph_name)["y_max"])
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-max-context", cls=BaseCommand)
def recalc_max_context(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the usMaxContext value of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.recalc_max_context()
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-codepage-ranges", cls=BaseCommand)
def recalc_codepage_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulCodePageRange values of the OS/2 table.
    """

    def task(font: Font) -> bool:
        font.t_os_2.recalc_code_page_ranges()
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-unicode-ranges", cls=BaseCommand)
@click.option(
    "-p",
    "--percentage",
    type=click.FloatRange(0.0001, 100),
    default=33.0,
    help="Minimum percentage of coverage required for a Unicode range to be enabled.",
)
def recalc_unicode_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulUnicodeRange values of the OS/2 table based on a minimum percentage of
    coverage.
    """

    def task(font: Font, percentage: float = 33) -> bool:
        result = font.t_os_2.recalc_unicode_ranges(percentage=percentage)
        if result:
            for block in result:
                logger.info(f"({block[0]}) {block[1]}: {block[2]}")
            return True
        return False

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-attrs", cls=BaseCommand)
@set_attrs_options()
def set_attrs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets miscellaneous attributes of the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, t.Optional[t.Union[int, float, str, bool]]]) -> bool:
        for attr, value in kwargs.items():
            if value is not None:
                try:
                    setattr(font.t_os_2, attr, value)
                except (ValueError, InvalidOS2VersionError) as e:
                    logger.warning(f"Error setting {attr} to {value}: {e}")
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fs-selection", cls=BaseCommand)
@set_fs_selection_options()
def set_fs_selection(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets flags in the fsSelection field of the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, t.Optional[bool]]) -> bool:
        for attr, value in kwargs.items():
            if value is not None:
                if hasattr(font.flags, attr):
                    setattr(font.flags, attr, value)
                elif hasattr(font.t_os_2.fs_selection, attr):
                    setattr(font.t_os_2.fs_selection, attr, value)
        # IMPORTANT: 'head' is a dependency of 'OS/2'. If 'font.t_head.is_modified' is evaluated
        # 'font.t_os_2.is_modified' to suppress fontTools warning about non-matching bits.
        return font.t_head.is_modified or font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fs-type", cls=BaseCommand)
@set_fs_type_options()
def set_fs_type(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set font embedding licensing rights for the font, defined in the fsType field of the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, t.Optional[bool]]) -> bool:
        for attr, value in kwargs.items():
            if hasattr(font.t_os_2, attr) and value is not None:
                setattr(font.t_os_2, attr, value)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("panose", cls=BaseCommand)
@panose_options()
def set_panose(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets the PANOSE classification in the OS/2 table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(font: Font, **kwargs: t.Dict[str, int]) -> bool:
        for attr, value in kwargs.items():
            if hasattr(font.t_os_2.table.panose, attr) and value is not None:
                setattr(font.t_os_2.table.panose, attr, value)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("upgrade", cls=BaseCommand)
@click.option(
    "-v",
    "--target-version",
    type=click.IntRange(1, 5),
    help="""
    The version of the OS/2 table to set.
    """,
)
def upgrade(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Upgrades the OS/2 table version.

    If the target version is less or equal to the current version, the table is not modified.
    """

    def task(font: Font, target_version: int) -> bool:
        font.t_os_2.upgrade(target_version)
        return font.t_os_2.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
