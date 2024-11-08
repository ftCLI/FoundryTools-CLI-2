# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.os_2.options import (
    panose_options,
    set_attrs_options,
    set_fs_selection_options,
    set_fs_type_options,
    target_version,
)
from foundrytools_cli_2.cli.shared_callbacks import validate_params
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.lib.cli_tools.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``OS/2`` table.")


@cli.command("recalc-avg-width")
@base_options()
def recalc_avg_char_width(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the xAvgCharWidth value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_avg_char_width as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-x-height")
@base_options()
def recalc_x_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sxHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_x_height as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-cap-height")
@base_options()
def recalc_cap_height(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the sCapHeight value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_cap_height as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-max-context")
@base_options()
def recalc_max_context(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the usMaxContext value of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_max_context as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-codepage-ranges")
@base_options()
def recalc_codepage_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulCodePageRange values of the OS/2 table.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_codepage_ranges as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("recalc-unicode-ranges")
@click.option(
    "-p",
    "--percentage",
    type=click.FloatRange(0.0001, 100),
    default=33.0,
    help="Minimum percentage of coverage required for a Unicode range to be enabled.",
)
@base_options()
def recalc_unicode_ranges(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Recalculates the ulUnicodeRange values of the OS/2 table based on a minimum percentage of
    coverage.
    """
    from foundrytools_cli_2.cli.os_2.tasks import recalc_unicode_ranges as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-attrs", no_args_is_help=True)
@set_attrs_options()
@base_options()
def set_attrs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets miscellaneous attributes of the OS/2 table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.os_2.tasks import set_attrs as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fs-selection", no_args_is_help=True)
@set_fs_selection_options()
@base_options()
def set_fs_selection(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets flags in the fsSelection field of the OS/2 table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.os_2.tasks import set_fs_selection as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fs-type", no_args_is_help=True)
@set_fs_type_options()
@base_options()
def set_fs_type(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set font embedding licensing rights for the font, defined in the fsType field of the OS/2 table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.os_2.tasks import set_fs_type as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("panose", no_args_is_help=True)
@panose_options()
@base_options()
def set_panose(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sets the PANOSE classification in the OS/2 table.
    """
    validate_params(click.get_current_context())

    from foundrytools_cli_2.cli.os_2.tasks import set_panose as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("upgrade", no_args_is_help=True)
@target_version()
@base_options()
def upgrade(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Upgrades the OS/2 table version.

    If the target version is less or equal to the current version, the table is not modified.
    """
    from foundrytools_cli_2.cli.os_2.tasks import upgrade_version as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
