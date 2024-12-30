from foundrytools import Font


def main(font: Font) -> bool:
    """
    Fixes the width of the non-breaking space glyph to be the same as the space glyph.
    """
    return font.t_hmtx.fix_non_breaking_space_width()
