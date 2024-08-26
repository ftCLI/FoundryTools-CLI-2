import typing as t

import click

from foundrytools_cli_2.cli.shared_callbacks import choice_to_int_callback
from foundrytools_cli_2.cli.shared_options import add_options


def name_id(required: bool = True) -> t.Callable:
    """
    Add the ``name_id`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``name_id`` option to a click command
    """
    _name_id_option = [
        click.option(
            "-n",
            "--name-id",
            type=click.IntRange(min=0, max=None),
            required=required,
            default=None,
            help="""
            Specify the name ID of the NameRecords to be modified.

            Example: ``-n 1`` will modify NameRecords with name ID 1.
            """,
        )
    ]
    return add_options(_name_id_option)


def name_ids(required: bool = True) -> t.Callable:
    """
    Add the ``name_ids`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``name_ids`` option to a click command
    """
    _name_ids_option = [
        click.option(
            "-n",
            "--name-ids",
            "name_ids_to_process",
            type=click.IntRange(min=0, max=None),
            required=required,
            multiple=True,
            default=None,
            help="""
            Specify the name IDs to be modified.

            Example: ``-n 1 -n 2`` will modify name IDs 1 and 2.
            """,
        )
    ]
    return add_options(_name_ids_option)


def skip_name_ids() -> t.Callable:
    """
    Add the ``exclude_name_ids`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``exclude_name_ids`` option to a click command
    """
    _exclude_name_ids_option = [
        click.option(
            "-x",
            "--exclude-name-ids",
            "name_ids_to_skip",
            type=click.IntRange(min=0, max=32767),
            multiple=True,
            default=None,
            help="""
            Specify the name IDs to be excluded.

            Example: ``-n 1 -n 2`` will modify all NameRecords except those with name IDs 1 and 2.
            """,
        )
    ]
    return add_options(_exclude_name_ids_option)


def platform_id() -> t.Callable:
    """
    Add the ``platform_id`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``platform_id`` option to a click command
    """
    _platform_id_option = [
        click.option(
            "-p",
            "--platform-id",
            type=click.IntRange(min=0, max=4),
            default=None,
            help="""
            Specify the platform ID of the NameRecords to be modified.

            \b
            0: Unicode 1.0 semantics (deprecated)
            1: Unicode 1.1 semantics (deprecated)
            2: ISO/IEC 10646 semantics (deprecated)
            3: Unicode 2.0 and onwards semantics, Unicode BMP only
            4: Unicode 2.0 and onwards semantics, Unicode full repertoire

            Example: ``-p 1`` will modify only NameRecords with platform ID 1.
            """,
        )
    ]
    return add_options(_platform_id_option)


def win_or_mac_platform_id() -> t.Callable:
    """
    Add the ``win_or_mac_platform_id`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``win_or_mac_platform_id`` option to a click command
    """
    _win_or_mac_platform_id_option = [
        click.option(
            "-p",
            "--platform-id",
            type=click.Choice(choices=["1", "3"]),
            callback=choice_to_int_callback,
            default=None,
            help="""
            Specify the platform ID of the NameRecords to be modified.

            \b
            1: Macintosh
            3: Windows

            Example: ``-p 1`` will modify only NameRecords with platform ID 1.
            """,
        )
    ]
    return add_options(_win_or_mac_platform_id_option)


def language_string() -> t.Callable:
    """
    Add the ``language_string`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``language_string`` option to a click command
    """
    _language_string_option = [
        click.option(
            "-l",
            "--language-string",
            type=str,
            default="en",
            help="""
            Specify the language of the NameRecords to be modified.

            Example: ``-l en`` will modify only NameRecords with language code "en".
            """,
        )
    ]
    return add_options(_language_string_option)


def name_string() -> t.Callable:
    """
    Add the ``name_string`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``name_string`` option to a click command
    """
    _string_option = [
        click.option(
            "-s",
            "--string",
            "name_string",
            type=str,
            required=True,
            help="""
            Specify the string to be added.
            """,
        )
    ]
    return add_options(_string_option)


def delete_all() -> t.Callable:
    """
    Add the ``delete_all`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the delete_all option to a click command
    """
    _delete_all_mac_names_flag = [
        click.option(
            "--del-all",
            "delete_all",
            is_flag=True,
            default=False,
            help="""
            Delete all Macintosh-specific NameRecords, including those with nameID 1, 2, 4, 5 and 6.
            """,
        )
    ]
    return add_options(_delete_all_mac_names_flag)


def alternate_unique_id() -> t.Callable:
    """
    Add the ``alternate_unique_id`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the alternate_unique_id option to a click command
    """
    _alternate_unique_id_option = [
        click.option(
            "-alt",
            "--alternate",
            is_flag=True,
            default=False,
            help="""
            Build the unique ID using the font's family name and subfamily name.
            """,
        )
    ]
    return add_options(_alternate_unique_id_option)
