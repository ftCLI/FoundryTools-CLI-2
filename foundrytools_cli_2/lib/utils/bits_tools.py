def is_nth_bit_set(x: int, n: int) -> bool:
    """
    If the nth bit of an integer x is set, return True, otherwise return False

    :param x: The number whose nth bit we want to check
    :type x: int
    :param n: The bit position to check
    :type n: int
    :return: True if the nth bit of x is set, False otherwise.
    """
    if x & (1 << n):
        return True
    return False


def set_nth_bit(x: int, n: int) -> int:
    """
    It takes an integer x and sets the nth bit of x to 1

    :param x: The number whose nth bit you want to set
    :type x: int
    :param n: the bit we want to set
    :type n: int
    :return: The number x with the nth bit set to 1.
    """
    return x | 1 << n


def unset_nth_bit(x: int, n: int) -> int:
    """
    It takes an integer x and clears the nth bit, setting its value to 0

    :param x: The number whose nth bit we want to clear
    :type x: int
    :param n: the nth bit to clear
    :type n: int
    :return: The number x with the nth bit set to 0.
    """
    return x & ~(1 << n)


def update_bit(num: int, value: bool, pos: int) -> int:
    """
    Handle a bitwise operation on an integer.

    Parameters:
        num (int): The integer to modify.
        pos (int): The position of the bit to update.
        value (bool): If True, the bit will be set, otherwise it will be cleared.
    """
    if value:
        return set_nth_bit(num, pos)
    return unset_nth_bit(num, pos)
