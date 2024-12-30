import typing as t

from foundrytools import Font


def del_names(
    font: Font,
    name_ids_to_process: t.Tuple[int],
    platform_id: t.Optional[int] = None,
    language_string: t.Optional[str] = None,
) -> bool:
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

    font.t_name.remove_names(
        name_ids=name_ids_to_process, platform_id=platform_id, language_string=language_string
    )
    return font.t_name.is_modified


def del_empty_names(font: Font) -> bool:
    """
    Deletes empty names from the given font.

    Args:
        font (Font): The font object to delete the empty names from.
    """

    font.t_name.remove_empty_names()
    return font.t_name.is_modified


def del_mac_names(font: Font) -> bool:
    """
    Deletes Macintosh-specific font names from the given font.

    Args:
        font (Font): The font object to delete the Macintosh names from.
    """
    font.t_name.remove_mac_names()
    return font.t_name.is_modified


def del_unused_names(font: Font) -> bool:
    """
    Removes unused NameRecords from the name table.

    Args:
        font (Font): The font object to remove the unused names from.
    """

    font.t_name.table.removeUnusedNames(font.ttfont)
    return font.t_name.is_modified


def find_replace(
    font: Font,
    old_string: str,
    new_string: str,
    name_ids_to_process: t.Optional[t.Tuple[int]] = None,
    name_ids_to_skip: t.Optional[t.Tuple[int]] = None,
) -> bool:
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

    font.t_name.find_replace(
        old_string=old_string,
        new_string=new_string,
        name_ids_to_process=name_ids_to_process,
        name_ids_to_skip=name_ids_to_skip,
    )
    return font.t_name.is_modified


def set_name(
    font: Font,
    name_id: int,
    name_string: str,
    platform_id: t.Optional[int] = None,
    language_string: str = "en",
) -> bool:
    """
    Updates the name table of a font file by setting the string value of a NameRecord.

    Args:
        font (Font): The Font object representing the font file.
        name_id (int): The ID of the name to be set.
        name_string (str): The string value of the name to be set.
        platform_id (Optional[int]): The platform ID of the name record. Defaults to None.
        language_string (str): The language code of the name record. Defaults to "en".
    """

    font.t_name.set_name(
        name_id=name_id,
        name_string=name_string,
        platform_id=platform_id,
        language_string=language_string,
    )
    return font.t_name.is_modified


def strip_names(font: Font) -> bool:
    """
    Removes leading and trailing whitespace from NameRecords in the name table.

    Args:
        font (Font): The Font object.
    """
    font.t_name.strip_names()
    return font.t_name.is_modified


def build_unique_id(
    font: Font, platform_id: t.Optional[int] = None, alternate: bool = False
) -> bool:
    """
    Builds a unique ID for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
        alternate (bool, optional): Whether to build an alternate unique ID. Defaults to False.
    """

    font.t_name.build_unique_identifier(platform_id=platform_id, alternate=alternate)
    return font.t_name.is_modified


def build_full_font_name(font: Font, platform_id: t.Optional[int] = None) -> bool:
    """
    Builds a full font name for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
    """

    font.t_name.build_full_font_name(platform_id=platform_id)
    return font.t_name.is_modified


def build_version_string(font: Font, platform_id: t.Optional[int] = None) -> bool:
    """
    Builds a version string for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None.
    """

    font.t_name.build_version_string(platform_id=platform_id)
    return font.t_name.is_modified


def build_postscript_name(font: Font, platform_id: t.Optional[int] = None) -> bool:
    """
    Builds a postscript name for the font file.

    Args:
        font (Font): The Font object representing the font file.
        platform_id (int, optional): The platform ID of the name record. Defaults to None, which
            will build the postscript name both platform 1 and 3.
    """

    font.t_name.build_postscript_name(platform_id=platform_id)
    return font.t_name.is_modified


def build_mac_names(font: Font) -> bool:
    """
    Builds Macintosh-specific font names for the given font.

    Args:
        font (Font): The font object to build the Macintosh names for.
    """

    font.t_name.build_mac_names()
    return font.t_name.is_modified
