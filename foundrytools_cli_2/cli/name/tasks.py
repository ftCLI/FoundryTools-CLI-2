import typing as t

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables import NameTable


def del_names(
    font: Font,
    name_ids_to_process: t.Tuple[int],
    platform_id: t.Optional[int] = None,
    language_string: t.Optional[str] = None,
) -> None:
    """
    Updates the name table of a font file by deleting NameRecords.

    Args:
        font (Font): The Font object representing the font file.
        name_ids_to_process (tuple[int]): A tuple of name IDs to delete.
        platform_id (Optional[int]): The platform ID of the name records to delete. Defaults to
            None.
        language_string (Optional[str]): The language of the name records to delete. Defaults to
            None.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.remove_names(
        name_ids=name_ids_to_process, platform_id=platform_id, language_string=language_string
    )
    font.is_modified = name_table.is_modified


def del_empty_names(font: Font) -> None:
    """
    Deletes empty names from the given font.

    Args:
        font (Font): The font object to delete the empty names from.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.remove_empty_names()
    font.is_modified = name_table.is_modified


def del_mac_names(
    font: Font,
    delete_all: bool = False,
) -> None:
    """
    Deletes Macintosh-specific font names from the given font. By default, the following names are
    kept: 1 (Font Family Name), 2 (Font Subfamily Name), 4 (Full Font Name), 5 (Version String),
    6 (PostScript Name).

    Args:
        font (Font): The font object to delete the Macintosh names from.
        delete_all (bool, optional): Whether to delete all Macintosh names. Defaults to False.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_ids_to_delete = {name.nameID for name in name_table.table.names if name.platformID == 1}
    if not delete_all:
        name_ids_to_delete.difference_update({1, 2, 4, 5, 6})
    name_table.remove_names(name_ids=name_ids_to_delete, platform_id=1)
    font.is_modified = name_table.is_modified


def del_unused_names(font: Font) -> None:
    """
    Removes unused NameRecords from the name table.

    Args:
        font (Font): The font object to remove the unused names from.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.table.removeUnusedNames(font.ttfont)
    font.is_modified = name_table.is_modified


def find_replace(
    font: Font,
    old_string: str,
    new_string: str,
    name_ids_to_process: t.Optional[t.Tuple[int]] = None,
    name_ids_to_skip: t.Optional[t.Tuple[int]] = None,
) -> None:
    """
    Updates the name table of a font file by replacing occurrences of one string with another.

    Args:
        font (Font): The Font object representing the font file.
        old_string (str): The string to be replaced.
        new_string (str): The string to replace the old_string with.
        name_ids_to_process (tuple[int], optional): A tuple of name IDs to process. Default is an
            empty tuple.
        name_ids_to_skip (tuple[int], optional): A tuple of name IDs to skip. Default is an empty
            tuple.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.find_replace(
        old_string=old_string,
        new_string=new_string,
        name_ids_to_process=name_ids_to_process,
        name_ids_to_skip=name_ids_to_skip,
    )
    font.is_modified = name_table.is_modified


def set_name(
    font: Font,
    name_id: int,
    name_string: str,
    platform_id: t.Optional[int] = None,
    language_string: str = "en",
) -> None:
    """
    Updates the name table of a font file by setting the string value of a NameRecord.

    Args:
        font (Font): The Font object representing the font file.
        name_id (int): The ID of the name to be set.
        name_string (str): The string value of the name to be set.
        platform_id (Optional[int]): The platform ID of the name record. Defaults to None.
        language_string (str): The language code of the name record. Defaults to "en".
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.set_name(
        name_id=name_id,
        name_string=name_string,
        platform_id=platform_id,
        language_string=language_string,
    )
    font.is_modified = name_table.is_modified


def strip_names(font: Font) -> None:
    """
    Removes leading and trailing whitespace from NameRecords in the name table.

    Args:
        font (Font): The Font object.
    """
    name_table = NameTable(ttfont=font.ttfont)
    name_table.strip_names()
    font.is_modified = name_table.is_modified


def build_unique_id(
    font: Font, platform_id: t.Optional[int] = None, alternate: bool = False
) -> None:
    """
    Builds a unique ID for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
        alternate (bool, optional): Whether to build an alternate unique ID. Defaults to False.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.build_unique_identifier(platform_id=platform_id, alternate=alternate)
    font.is_modified = name_table.is_modified


def build_full_font_name(font: Font, platform_id: t.Optional[int] = None) -> None:
    """
    Builds a full font name for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.build_full_font_name(platform_id=platform_id)
    font.is_modified = name_table.is_modified


def build_version_string(font: Font, platform_id: t.Optional[int] = None) -> None:
    """
    Builds a version string for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.build_version_string(platform_id=platform_id)
    font.is_modified = name_table.is_modified


def build_postscript_name(font: Font, platform_id: t.Optional[int] = None) -> None:
    """
    Builds a postscript name for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None, which
            will build the postscript name both platform 1 and 3.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.build_postscript_name(platform_id=platform_id)
    font.is_modified = name_table.is_modified


def build_mac_names(font: Font) -> None:
    """
    Builds Macintosh-specific font names for the given font.

    Args:
        font (Font): The font object to build the Macintosh names for.
    """

    name_table = NameTable(ttfont=font.ttfont)
    name_table.build_mac_names()
    font.is_modified = name_table.is_modified
