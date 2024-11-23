import typing as t

from foundrytools import Font


def set_names(font: Font, **kwargs: t.Dict[str, str]) -> bool:
    """
    Set the provided values in the CFF table of a font.

    Args:
        font (Font): The font to set the values in.
        kwargs (Dict[str, str]): The values to set in the CFF table.
    """
    font.t_cff_.set_names(**kwargs)
    return True


def del_names(font: Font, **kwargs: t.Dict[str, str]) -> bool:
    """
    Delete the provided names from the CFF table of a font.

    Args:
        font (Font): The font to delete the names from.
        kwargs (Dict[str, str]): The names to delete from the CFF table TopDict.
    """

    font.t_cff_.del_names(**kwargs)
    return True


def find_replace(font: Font, old_string: str, new_string: str) -> bool:
    """
    Replace the provided string in the CFF table of a font.

    Args:
        font (Font): The font to replace the string in.
        old_string (str): The string to replace.
        new_string (str): The string to replace the old string with.
    """

    font.t_cff_.find_replace(old_string, new_string)
    return True
