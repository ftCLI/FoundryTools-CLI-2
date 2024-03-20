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
