from copy import deepcopy

from dehinter.font import dehint

from foundrytools_cli_2.lib.font import Font

def tt_remove_hints(font: Font) -> None:
    """
    Remove hints from a TrueType font.
    """

    if not font.is_tt:
        raise NotImplementedError("Only TrueType fonts are supported.")

    font_copy = deepcopy(font)
    dehint(font_copy)

    return font_copy
