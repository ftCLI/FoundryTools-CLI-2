from textwrap import TextWrapper
from typing import Optional


def wrap_string(
    string: str, width: int, initial_indent: int, indent: int, max_lines: Optional[int] = None
) -> str:
    """
    Wraps a string to a given width, with a given indentation.

    :param string: The string to wrap.
    :type string: str
    :param width: The width to wrap the string to.
    :type width: int
    :param initial_indent: The initial indentation.
    :type initial_indent: int
    :param indent: The subsequent indentation.
    :type indent: int
    :param max_lines: The maximum number of lines to wrap the string to.
    :type max_lines: Optional[int]
    :return: The wrapped string.
    :rtype: str
    """
    wrapped_string = TextWrapper(
        width=width,
        initial_indent=" " * initial_indent,
        subsequent_indent=" " * indent,
        max_lines=max_lines,
        break_on_hyphens=False,
        break_long_words=True,
    ).fill(string)
    return wrapped_string
