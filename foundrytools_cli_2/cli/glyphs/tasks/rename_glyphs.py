from pathlib import Path

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(font: Font, source_file: Path) -> None:
    """
    Set the production names of glyphs in a font.

    Args:
        font (Font): The font to rename the glyph in.
        source_file (Path): The source font file to get the glyph order from.
    """
    old_glyph_order = font.ttfont.getGlyphOrder()
    try:
        source_font = Font(source_file)
        new_glyph_order = source_font.ttfont.getGlyphOrder()
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Failed to get the glyph order from the source font: {e}")
        return
    if old_glyph_order == new_glyph_order:
        logger.info("The glyph order of the source font is the same as the current font.")
        return
    result = font.rename_glyphs(new_glyph_order=new_glyph_order)
    if result:
        font.rebuild_cmap(remap_all=True)
        font.is_modified = True
