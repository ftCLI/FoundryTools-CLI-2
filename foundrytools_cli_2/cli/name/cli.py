# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.name.options import (
    alternate_unique_id,
    language_string,
    name_id,
    name_ids,
    name_string,
    platform_id,
    skip_name_ids,
    win_or_mac_platform_id,
)
from foundrytools_cli_2.cli.shared_options import base_options, new_string_option, old_string_option
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Utilities for editing the ``name`` table.")


@cli.command("del-names")
@name_ids(required=True)
@platform_id()
@language_string()
@base_options()
def del_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete the specified NameRecords from the ``name`` table.
    """
    from foundrytools_cli_2.cli.name.tasks import del_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-empty-names")
@base_options()
def del_empty_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Deletes empty NameRecords from the ``name`` table.
    """
    from foundrytools_cli_2.cli.name.tasks import del_empty_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-mac-names")
@base_options()
def del_mac_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete Macintosh-specific NameRecords from the ``name`` table, excluding those with nameID 1, 2,
    4, 5 and 6. If the ``--del-all`` flag is set, all Macintosh-specific NameRecords are deleted.
    """
    from foundrytools_cli_2.cli.name.tasks import del_mac_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-unused-names")
@base_options()
def del_unused_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete unused NameRecords from the ``name`` table.
    """
    from foundrytools_cli_2.cli.name.tasks import del_unused_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("find-replace")
@old_string_option()
@new_string_option()
@name_ids(required=False)
@skip_name_ids()
@platform_id()
@base_options()
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Find and replace text in the specified NameRecords.
    """
    from foundrytools_cli_2.cli.name.tasks import find_replace as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-name")
@name_string()
@name_id()
@win_or_mac_platform_id()
@base_options()
def set_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the string of the specified NameRecord in the ``name`` table.
    """
    from foundrytools_cli_2.cli.name.tasks import set_name as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("strip-names")
@base_options()
def strip_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Remove leading and trailing whitespace from the NameRecords.
    """
    from foundrytools_cli_2.cli.name.tasks import strip_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-unique-id")
@alternate_unique_id()
@win_or_mac_platform_id()
@base_options()
def build_unique_id(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 3 (Unique ID).

    If the ``--alternate`` flag is set, the unique ID is built using the following fields:

    ``Manufacturer Name: Family Name - Subfamily Name: Creation Year``

    Otherwise, the unique ID is built using the following fields (Default):

    ``Font Revision;Vendor ID;PostScript Name``
    """
    from foundrytools_cli_2.cli.name.tasks import build_unique_id as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-full-font-name")
@win_or_mac_platform_id()
@base_options()
def build_full_font_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 4 (Full Font Name).
    """
    from foundrytools_cli_2.cli.name.tasks import build_full_font_name as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-version-string")
@win_or_mac_platform_id()
@base_options()
def build_version_string(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 5 (Version String).
    """
    from foundrytools_cli_2.cli.name.tasks import build_version_string as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-postscript-name")
@win_or_mac_platform_id()
@base_options()
def build_postscript_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 6 (PostScript Name).
    """
    from foundrytools_cli_2.cli.name.tasks import build_postscript_name as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("build-mac-names")
@base_options()
def build_mac_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the Macintosh-specific names.

    The following names are built: 1 (Font Family Name), 2 (Font Subfamily Name), 4
    (Full Font Name), 5 (Version String), 6 (PostScript Name).
    """
    from foundrytools_cli_2.cli.name.tasks import build_mac_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
