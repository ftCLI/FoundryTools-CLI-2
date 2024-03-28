from dehinter.font import dehint

from foundrytools_cli_2.lib.font import Font


def ttf_dehint(font: Font) -> None:
    """
    De-hints the given TrueType font.

    Args:
        font (Font): The Font object.
    """

    if not font.is_tt:
        raise ValueError("TTF de-hinting is only supported for TrueType fonts.")

    dehint(font.ttfont, verbose=False)
    font.modified = True
