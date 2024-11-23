from foundrytools import Font


def main(font: Font) -> bool:
    """
    Fixes the missing non-breaking space glyph by double mapping the space glyph.
    """
    font.t_cmap.add_missing_nbsp()
    return font.t_cmap.is_modified
