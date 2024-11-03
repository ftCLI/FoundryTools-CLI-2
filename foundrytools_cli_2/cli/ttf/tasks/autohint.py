from io import BytesIO

from fontTools.ttLib import TTFont
from ttfautohint import ttfautohint

from foundrytools_cli_2.lib.constants import T_HEAD
from foundrytools_cli_2.lib.font import Font


def ttf_autohint(font: Font) -> None:
    """
    Auto-hints the given TrueType font.

    Args:
        font (Font): The Font object.
    """

    if not font.is_tt:
        raise NotImplementedError("TTF auto-hinting is only supported for TrueType fonts.")

    with BytesIO() as buffer:
        flavor = font.ttfont.flavor
        font.ttfont.flavor = None
        font.save(buffer, reorder_tables=None)
        data = ttfautohint(in_buffer=buffer.getvalue(), no_info=True)
        hinted_font = TTFont(BytesIO(data), recalcTimestamp=False)
        hinted_font.flavor = flavor
        hinted_font[T_HEAD].modified = font.ttfont[T_HEAD].modified
        font.ttfont = hinted_font
        font.is_modified = True
