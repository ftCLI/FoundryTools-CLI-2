# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.name.options import (
    alternate_unique_id,
    delete_all,
    language_string,
    name_id,
    name_ids,
    name_string,
    new_string,
    old_string,
    platform_id,
    skip_name_ids,
    win_or_mac_platform_id,
)
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.lib.font import Font

cli = click.Group(help="Utilities for editing the ``name`` table.")


@cli.command("del-names")
@name_ids(required=True)
@platform_id()
@language_string()
@base_options()
def del_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete names from the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import del_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-empty-names")
@base_options()
def del_empty_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Deletes empty names from the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import del_empty_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-mac-names")
@delete_all()
@base_options()
def del_mac_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete Macintosh names from the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import del_mac_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("del-unused-names")
@base_options()
def del_unused_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Delete unused names from the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import del_unused_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("find-replace")
@old_string()
@new_string()
@name_ids(required=False)
@skip_name_ids()
@platform_id()
@base_options()
def find_replace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Find and replace text in the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import find_replace as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-name")
@name_string()
@name_id()
@win_or_mac_platform_id()
@base_options()
def set_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import set_name as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("strip-names")
@base_options()
def strip_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Strip the name table of the given font files.
    """
    from foundrytools_cli_2.cli.name.snippets import strip_names as task

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

    runner = TaskRunner(input_path=input_path, task=Font.build_unique_identifier, **options)
    runner.run()


@cli.command("build-full-font-name")
@win_or_mac_platform_id()
@base_options()
def build_full_font_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 4 (Full Font Name).
    """

    runner = TaskRunner(input_path=input_path, task=Font.build_full_font_name, **options)
    runner.run()


@cli.command("build-version-string")
@win_or_mac_platform_id()
@base_options()
def build_version_string(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 5 (Version String).
    """

    runner = TaskRunner(input_path=input_path, task=Font.build_version_string, **options)
    runner.run()


@cli.command("build-postscript-name")
@win_or_mac_platform_id()
@base_options()
def build_postscript_name(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Builds the NameID 6 (PostScript Name).
    """

    runner = TaskRunner(input_path=input_path, task=Font.build_postscript_name, **options)
    runner.run()
