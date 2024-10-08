from foundrytools_cli_2.lib.font import Font


def main(font: Font, old_name: str, new_name: str) -> None:
    """
    Rename a single glyph in a font file.

    Args:
        font (Font): The font to rename the glyph in.
        old_name (str): The old name of the glyph.
        new_name (str): The new name of the glyph.
    """
    result = font.rename_glyph(old_name=old_name, new_name=new_name)
    if result:
        font.modified = True
