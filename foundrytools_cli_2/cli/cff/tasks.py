import typing as t

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.cff_ import CFFTable


def set_names(font: Font, **kwargs: t.Dict[str, str]) -> None:
    """
    Set the provided values in the CFF table of a font.

    Args:
        font (Font): The font to set the values in.
        kwargs (Dict[str, str]): The values to set in the CFF table.
    """

    cff_table = CFFTable(font.ttfont)
    cff_table.set_names(**kwargs)
    font.is_modified = cff_table.is_modified


def del_names(font: Font, **kwargs: t.Dict[str, str]) -> None:
    """
    Delete the provided names from the CFF table of a font.

    Args:
        font (Font): The font to delete the names from.
        kwargs (Dict[str, str]): The names to delete from the CFF table TopDict.
    """

    cff_table = CFFTable(font.ttfont)
    cff_table.del_names(**kwargs)
    font.is_modified = cff_table.is_modified


def find_replace(font: Font, old_string: str, new_string: str) -> None:
    """
    Replace the provided string in the CFF table of a font.

    Args:
        font (Font): The font to replace the string in.
        old_string (str): The string to replace.
        new_string (str): The string to replace the old string with.
    """

    cff_table = CFFTable(font.ttfont)
    cff_table.find_replace(old_string, new_string)
    font.is_modified = cff_table.is_modified
