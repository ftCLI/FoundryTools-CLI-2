import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.callbacks import choice_to_int_callback, output_dir_callback


def add_options(options: t.List[t.Callable]) -> t.Callable:
    """
    Add options to a click command.

    :param options: a list of click options
    :return: a decorator that adds the options to a click command
    """

    def _add_options(func: t.Callable) -> t.Callable:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def common_options() -> t.Callable:
    """
    Add the common options to a click command.

    :return: a decorator that adds the common options to a click command
    """

    return add_options(
        [
            input_path_argument(),
            recursive_flag(),
            output_dir_option(),
            overwrite_flag(),
            recalc_timestamp_flag(),
        ]
    )


def input_path_argument(dir_okay: bool = True, file_okay: bool = True) -> t.Callable:
    """
    Add the ``input_path`` argument to a click command.

    The ``input_path`` argument is the path to a font file or to a directory containing font files.
    If ``input_path`` is a directory, all the font files stored in it, and matching the eventual
    criteria, will be processed. If ``input_path`` is a file, only that file will be processed.
    Users can specify whether the argument can be a directory or a file.

    :param dir_okay: if False, the argument can't be a file
    :param file_okay: if False, the argument can be a directory
    :return: a decorator that adds the input_path argument to a click command
    """
    _file_or_path_argument = [
        click.argument(
            "input_path",
            type=click.Path(
                exists=True,
                resolve_path=True,
                path_type=Path,
                dir_okay=dir_okay,
                file_okay=file_okay,
            ),
        )
    ]
    return add_options(_file_or_path_argument)


def recursive_flag() -> t.Callable:
    """
    Add the recursive option to a click command.

    :return: a decorator that adds the recursive flag to a click command
    """
    _recursive_flag = [
        click.option(
            "-r",
            "--recursive",
            is_flag=True,
            default=False,
            help="""
            When ``input_path`` is a directory, the font finder will search for fonts recursively in
            subdirectories.
            """,
        )
    ]
    return add_options(_recursive_flag)


def lazy_flag() -> t.Callable:
    """
    Add the lazy option to a click command.

    :return: a decorator that adds the lazy flag to a click command
    """
    _lazy_flag = [
        click.option(
            "--lazy/--no-lazy",
            default=None,
            help="""
            If lazy is set to True, many data structures are loaded lazily, upon access only. If it
            is set to False, many data structures are loaded immediately. The default is
            ``lazy=None`` which is somewhere in between.
            """,
        )
    ]
    return add_options(_lazy_flag)


def output_dir_option() -> t.Callable:
    """
    Add the output_dir option to a click command.

    :return: a decorator that adds the output_dir option to a click command
    """
    _output_dir_option = [
        click.option(
            "-out",
            "--output-dir",
            type=click.Path(path_type=Path, file_okay=False, resolve_path=True),
            default=None,
            callback=output_dir_callback,
            help="""
            Specify a directory where the output files are to be saved. If the output directory
            doesn't exist, it will be automatically created. If not specified, files will be saved
            to the source directory.
            """,
        )
    ]
    return add_options(_output_dir_option)


def overwrite_flag() -> t.Callable:
    """
    Add the overwrite option to a click command.

    :return: a decorator that adds the overwrite option to a click command
    """
    _overwrite_flag = [
        click.option(
            "--no-overwrite",
            "overwrite",
            is_flag=True,
            default=True,
            help="""
            Use this flag to avoid overwriting existing files, but save them to a new file by adding
            numbers at the end of file name. By default, files are overwritten.
            """,
        )
    ]
    return add_options(_overwrite_flag)


def recalc_timestamp_flag() -> t.Callable:
    """
    Add the recalc_timestamp option to a click command.

    :return: a decorator that adds the recalc_timestamp option to a click command
    """
    _recalc_timestamp_flag = [
        click.option(
            "--recalc-timestamp",
            is_flag=True,
            default=False,
            help="""
            Use this flag to recalculate the ``modified`` timestamp in the ``head`` table on save.
            By default, the ``modified`` timestamp is kept.
            """,
        )
    ]
    return add_options(_recalc_timestamp_flag)


def recalc_bboxes_flag() -> t.Callable:
    """
    Add the recalc_bboxes option to a click command.

    :return: a decorator that adds the recalc_bboxes option to a click command
    """
    _recalc_bboxes_flag = [
        click.option(
            "--no-recalc-bboxes",
            "recalc_bboxes",
            is_flag=True,
            default=True,
            help="""
            Use this flag to avoid recalculating the bounding boxes of all glyphs on save. By
            default, bounding boxes are recalculated.
            """,
        )
    ]
    return add_options(_recalc_bboxes_flag)


def reorder_tables_flag() -> t.Callable:
    """
    Add the reorder_tables option to a click command.

    :return: a decorator that adds the reorder_tables option to a click command
    """
    _reorder_tables_flag = [
        click.option(
            "--reorder-tables/--no-reorder-tables",
            default=True,
            help="""
            Reorder the font's tables on save. If true (the default), reorder the tables, sorting
            them by tag (recommended by the OpenType specification). If False, retain the original
            font order. If None, reorder by table dependency (fastest).
            """,
        )
    ]
    return add_options(_reorder_tables_flag)


def debug_flag() -> t.Callable:
    """
    Add the debug option to a click command.

    :return: a decorator that adds the debug option to a click command
    """
    _debug_flag = [
        click.option(
            "--debug/--no-debug",
            default=False,
            help="""
            Use this flag to enable debug mode. By default, debug mode is disabled.
            """,
        )
    ]
    return add_options(_debug_flag)


def tolerance_option() -> t.Callable:
    """
    Add the tolerance option to a click command.

    :return: a decorator that adds the tolerance option to a click command
    """
    _tolerance_option = [
        click.option(
            "-t",
            "--tolerance",
            type=click.FloatRange(min=0.0, max=3.0),
            default=1.0,
            help="""
            Conversion tolerance (0.0-3.0, default 1.0). Low tolerance adds more points but keeps
            shapes. High tolerance adds  few points but may change shape.
            """,
        )
    ]
    return add_options(_tolerance_option)


def target_upm_option(
    required: bool = False,
    help_msg: str = "Scale the font to the specified UPM.",
) -> t.Callable:
    """
    Add the scale_upm option to a click command.

    :return: a decorator that adds the scale_upm option to a click command
    """
    _target_upm_option = [
        click.option(
            "-upm",
            "--target-upm",
            type=click.IntRange(min=16, max=16384),
            default=None,
            required=required,
            help=help_msg,
        )
    ]
    return add_options(_target_upm_option)


def subroutinize_flag() -> t.Callable:
    """
    Add the subroutinize option to a click command.

    :return: a decorator that adds the subroutinize option to a click command
    """
    _subroutinize_flag = [
        click.option(
            "--subroutinize/--no-subroutinize",
            default=True,
            help="Subroutinize the font.",
        )
    ]
    return add_options(_subroutinize_flag)


def min_area_option() -> t.Callable:
    """
    Add the min_area option to a click command.

    :return: a decorator that adds the min_area option to a click command
    """
    _min_area_option = [
        click.option(
            "-ma",
            "--min-area",
            type=click.IntRange(min=0),
            default=25,
            help="Remove tiny paths with area less than the specified value.",
        )
    ]
    return add_options(_min_area_option)


def in_format_choice() -> t.Callable:
    """
    Add the flavor option to a click command.

    :return: a decorator that adds the flavor option to a click command
    """
    _in_format_choice = [
        click.option(
            "-f",
            "--format",
            "in_format",
            type=click.Choice(["woff", "woff2"]),
            default=None,
            help="""
            By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts
            (TrueType or OpenType). Use this option to convert only woff or woff2 flavored web
            fonts.
    """,
        )
    ]
    return add_options(_in_format_choice)


def out_format_choice() -> t.Callable:
    """
    Add the flavor option to a click command.

    :return: a decorator that adds the flavor option to a click command
    """
    _out_format_choice = [
        click.option(
            "-f",
            "--format",
            "out_format",
            type=click.Choice(["woff", "woff2"]),
            default=None,
            help="""
            By default, the script converts SFNT fonts to both woff and woff2 flavored web fonts.
            Use this option to convert only to woff or woff2 flavored web fonts.
    """,
        )
    ]
    return add_options(_out_format_choice)


def ttf2otf_mode_choice() -> t.Callable:
    """
    Add the ttf2otf_mode option to a click command.

    :return: a decorator that adds the ttf2otf_mode option to a click command
    """
    _ttf2otf_mode_choice = [
        click.option(
            "-m",
            "--mode",
            type=click.Choice(["qu2cu", "tx"]),
            default="qu2cu",
            show_default=True,
            help="""
            Conversion mode. By default, the script uses the ``qu2cu`` mode. Quadratic curves are
            converted to cubic curves using the Qu2CuPen. Use the ``tx`` mode to use the tx tool
            from AFDKO to generate the CFF table instead of the Qu2CuPen.
            """,
        )
    ]
    return add_options(_ttf2otf_mode_choice)


def autohint_options() -> t.Callable:
    """
    Add the autohint options to a click command.

    :return: a decorator that adds the autohint options to a click command
    """
    _autohint_options = [
        allow_changes_flag(),
        allow_no_blues_flag(),
        decimal_flag(),
        no_flex_flag(),
        no_hint_sub_flag(),
    ]
    return add_options(_autohint_options)


def allow_changes_flag() -> t.Callable:
    """
    Add the allow_changes option to a click command.

    :return: a decorator that adds the allow_changes option to a click command
    """
    _allow_changes_flag = [
        click.option(
            "--allow-changes",
            is_flag=True,
            default=False,
            help="""
            Allow changes to the glyphs outlines.
            """,
        )
    ]
    return add_options(_allow_changes_flag)


def allow_no_blues_flag() -> t.Callable:
    """
    Add the allow_no_blues option to a click command.

    :return: a decorator that adds the allow_no_blues option to a click command
    """
    _allow_no_blues_flag = [
        click.option(
            "--allow-no-blues",
            is_flag=True,
            default=False,
            help="""
            Allow the font to have no alignment zones nor stem widths.
            """,
        )
    ]
    return add_options(_allow_no_blues_flag)


def decimal_flag() -> t.Callable:
    """
    Add the decimal option to a click command.

    :return: a decorator that adds the decimal option to a click command
    """
    _decimal_flag = [
        click.option(
            "--decimal",
            is_flag=True,
            default=False,
            help="""
            Use decimal coordinates.
            """,
        )
    ]
    return add_options(_decimal_flag)


def no_flex_flag() -> t.Callable:
    """
    Add the no_flex option to a click command.

    :return: a decorator that adds the no_flex option to a click command
    """
    _no_flex_flag = [
        click.option(
            "--no-flex",
            is_flag=True,
            default=False,
            help="""
            Suppress generation of flex commands.
            """,
        )
    ]
    return add_options(_no_flex_flag)


def no_hint_sub_flag() -> t.Callable:
    """
    Add the no_hint_sub option to a click command.

    :return: a decorator that adds the no_hint_sub option to a click command
    """
    _no_hint_sub_flag = [
        click.option(
            "--no-hint-sub",
            is_flag=True,
            default=False,
            help="""
            Suppress hint substitution.
            """,
        )
    ]
    return add_options(_no_hint_sub_flag)


def name_id(required: bool = True) -> t.Callable:
    """
    Add the name_id option to a click command.

    :return: a decorator that adds the name_id option to a click command
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
    Add the name_ids option to a click command.

    :return: a decorator that adds the name_ids option to a click command
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
    Add the exclude_name_ids option to a click command.

    :return: a decorator that adds the exclude_name_ids option to a click command
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

            Example: ``-n 1 -n 2`` will modify name IDs 1 and 2.
            """,
        )
    ]
    return add_options(_exclude_name_ids_option)


def platform_id() -> t.Callable:
    """
    Add the platform_id option to a click command.

    :return: a decorator that adds the platform_id option to a click command
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
    Add the win_or_mac_platform_id option to a click command.

    :return: a decorator that adds the win_or_mac_platform_id option to a click command
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
    Add the language_string option to a click command.

    :return: a decorator that adds the language_string option to a click command
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
    Add the string option to a click command.

    :return: a decorator that adds the string option to a click command
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


def old_string() -> t.Callable:
    """
    Add the old_string option to a click command.

    :return: a decorator that adds the old_string option to a click command
    """
    _old_string_option = [
        click.option(
            "-os",
            "--old-string",
            type=str,
            required=True,
            help="""
            Specify the string to be replaced.
            """,
        )
    ]
    return add_options(_old_string_option)


def new_string() -> t.Callable:
    """
    Add the new_string option to a click command.

    :return: a decorator that adds the new_string option to a click command
    """
    _new_string_option = [
        click.option(
            "-ns",
            "--new-string",
            type=str,
            required=True,
            help="""
            Specify the string to replace the old string with.
            """,
        )
    ]
    return add_options(_new_string_option)


def delete_all() -> t.Callable:
    """
    Add the delete_all_mac_names option to a click command.

    :return: a decorator that adds the delete_all_mac_names option to a click command
    """
    _delete_all_mac_names_flag = [
        click.option(
            "--delete-all",
            is_flag=True,
            default=False,
            help="""
            Delete all Macintosh NameRecords.
            """,
        )
    ]
    return add_options(_delete_all_mac_names_flag)
