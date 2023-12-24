import typing as t
from copy import deepcopy

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.name import TableName


def _compare_name_tables(font: Font, first: TableName, second: TableName) -> bool:
    """
    Compares two name tables.
    """
    return first.compile(font.ttfont) == second.compile(font.ttfont)


def find_replace(
    font: Font,
    old_string: str,
    new_string: str,
    name_ids_to_process: t.Optional[t.Tuple[int]] = None,
    name_ids_to_skip: t.Optional[t.Tuple[int]] = None,
) -> None:
    """
    Updates the name table of a font file by replacing occurrences of one string with another.

    Parameters:
        font (Font): The Font object representing the font file.
        old_string (str): The string to be replaced.
        new_string (str): The string to replace the old_string with.
        name_ids_to_process (tuple[int], optional): A tuple of name IDs to process. Default is an
            empty tuple.
        name_ids_to_skip (tuple[int], optional): A tuple of name IDs to skip. Default is an empty
            tuple.
    """
    name_table: TableName = font.ttfont["name"]
    name_copy = deepcopy(name_table)
    name_table.find_replace(
        old_string=old_string,
        new_string=new_string,
        name_ids_to_process=name_ids_to_process,
        name_ids_to_skip=name_ids_to_skip,
    )
    if not _compare_name_tables(font=font, first=name_table, second=name_copy):
        font.modified = True


def set_name(
    font: Font,
    name_id: int,
    name_string: str,
    platform_id: t.Optional[int] = None,
    language_string: str = "en",
) -> None:
    """
    Updates the name table of a font file by setting the string value of a NameRecord.

    Parameters:
        font (Font): The Font object representing the font file.
        name_id (int): The ID of the name to be set.
        name_string (str): The string value of the name to be set.
        platform_id (Optional[int]): The platform ID of the name record. Defaults to None.
        language_string (str): The language code of the name record. Defaults to "en".
    """
    name_table: TableName = font.ttfont["name"]
    name_copy = deepcopy(name_table)
    name_table.set_name(
        font=font.ttfont,
        name_id=name_id,
        name_string=name_string,
        platform_id=platform_id,
        language_string=language_string,
    )
    if not _compare_name_tables(font=font, first=name_table, second=name_copy):
        font.modified = True


def del_names(
    font: Font,
    name_ids_to_process: t.Tuple[int],
    platform_id: t.Optional[int] = None,
    language_string: t.Optional[str] = None,
) -> None:
    """
    Updates the name table of a font file by deleting NameRecords.

    Parameters:
        font (Font): The Font object representing the font file.
        name_ids_to_process (tuple[int]): A tuple of name IDs to delete.
        platform_id (Optional[int]): The platform ID of the name records to delete. Defaults to
            None.
        language_string (Optional[str]): The language of the name records to delete. Defaults to
            None.
    """
    name_table: TableName = font.ttfont["name"]
    name_copy = deepcopy(name_table)
    name_table.del_names(
        name_ids=name_ids_to_process, platform_id=platform_id, language_string=language_string
    )
    if not _compare_name_tables(font=font, first=name_table, second=name_copy):
        font.modified = True


def del_mac_names(
    font: Font,
    name_ids_to_process: t.Tuple[int],
    language_string: t.Optional[str] = None,
) -> None:
    """
    Updates the name table of a font file by deleting NameRecords.

    Parameters:
        font (Font): The Font object representing the font file.
        name_ids_to_process (tuple[int]): A tuple of name IDs to delete.
        platform_id (Optional[int]): The platform ID of the name records to delete. Defaults to
            None.
        language_string (Optional[str]): The language of the name records to delete. Defaults to
            None.
    """
    name_table: TableName = font.ttfont["name"]
    name_copy = deepcopy(name_table)
    name_table.del_mac_names(
        name_ids=name_ids_to_process, language_string=language_string
    )
    if not _compare_name_tables(font=font, first=name_table, second=name_copy):
        font.modified = True