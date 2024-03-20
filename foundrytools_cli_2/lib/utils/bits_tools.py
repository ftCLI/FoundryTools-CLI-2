def is_nth_bit_set(x: int, n: int) -> bool:
    """
    If the nth bit of an integer x is set, return True, otherwise return False

    Args:
        x (int): The number to check
        n (int): The bit to check

    Returns:
        bool: ``True`` if the nth bit is set, ``False`` otherwise
    """
    if x & (1 << n):
        return True
    return False


def set_nth_bit(x: int, n: int) -> int:
    """
    It takes an integer x and sets the nth bit of x to 1

    Args:
        x (int): The number to modify
        n (int): The bit to set

    Returns:
        int: The number x with the nth bit set to 1
    """
    return x | 1 << n


def unset_nth_bit(x: int, n: int) -> int:
    """
    It takes an integer x and clears the nth bit, setting its value to 0

    Args:
        x (int): The number to modify
        n (int): The bit to clear

    Returns:
        int: The number x with the nth bit set to 0
    """
    return x & ~(1 << n)


def update_bit(num: int, pos: int, value: bool) -> int:
    """
    Handle a bitwise operation on an integer.

    Args:
        num (int): The integer to modify.
        pos (int): The position of the bit to update.
        value (bool): If True, the bit will be set, otherwise it will be cleared.

    Returns:
        int: The modified integer.
    """
    if value:
        return set_nth_bit(num, pos)
    return unset_nth_bit(num, pos)
