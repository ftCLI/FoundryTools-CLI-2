from foundrytools_cli_2.lib.font import Font


def main(font: Font) -> None:
    """
    Fix the regular flag of a font. If the font is not bold or italic, it will be set to regular. If
    the font is bold or italic, it will be set to not regular.

    Args:
        font (Font): The font to fix.
    """

    # If the font is not bold or italic, set it to regular
    if not (font.is_bold or font.is_italic or font.is_regular):
        font.is_regular = True
        font.is_modified = True

    # If the font is bold or italic, set it to not regular
    elif (font.is_bold or font.is_italic) and font.is_regular:
        font.is_regular = False
        font.is_modified = True
