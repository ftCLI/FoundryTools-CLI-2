import typing as t
from textwrap import TextWrapper


def adjust_string_length(string: str, length: int, pad_char: str = " ") -> str:
    """
    Adjust the string to a specified length by padding or truncating it.

    Args:
        string (str): The string to adjust.
        length (int): The target length.
        pad_char (str): The character to pad with.

    Returns:
        str: The adjusted string.
    """
    return string.ljust(length, pad_char) if len(string) < length else string[:length]


def wrap_string(
    string: str, width: int, initial_indent: int, indent: int, max_lines: t.Optional[int] = None
) -> str:
    """
    Wraps a string to a given width, with a given indentation

    Args:
        string (str): The string to wrap
        width (int): The maximum width of the wrapped lines
        initial_indent (int): The number of spaces to add to the beginning of each line
        indent (int): The number of spaces to add to the left margin of subsequent lines
        max_lines (Optional[int]): The maximum number of lines to return. If the string is longer
        than this, it will be truncated
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
