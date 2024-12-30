from foundrytools import Font


def main(font: Font) -> bool:
    """
    Fix the regular flag of a font. If the font is not bold or italic, it will be set to regular. If
    the font is bold or italic, it will be set to not regular.

    Args:
        font (Font): The font to fix.
    """

    # If the font is not bold or italic, set it to regular
    if not (font.flags.is_bold or font.flags.is_italic or font.flags.is_regular):
        font.flags.set_regular()
        return True

    # If the font is bold or italic, set it to not regular
    if (font.flags.is_bold or font.flags.is_italic) and font.flags.is_regular:
        font.t_os_2.fs_selection.regular = False
        return True

    return False
