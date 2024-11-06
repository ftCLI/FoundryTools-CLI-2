import typing as t
from pathlib import Path

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def rebuild_cmap(font: Font, remap_all: bool = False) -> None:
    """
    Rebuild the cmap table of a font.

    Args:
        font (Font): The font to rebuild the cmap table of.
        remap_all (bool, optional): Whether to remap all characters. Defaults to False.
    """
    result = font.rebuild_cmap(remap_all=remap_all)
    if result:
        font.is_modified = True
        logger.info("Remapped glyphs:")
        for r in result:
            logger.opt(colors=True).info(
                f"  {hex(r[0])[:2]}{hex(r[0])[2:].upper().zfill(6)} : <lc>{r[1]}</lc>"
            )


def remove_glyphs(
    font: Font,
    glyph_names_to_remove: t.Optional[t.Set[str]],
    glyph_ids_to_remove: t.Optional[t.Set[int]],
) -> None:
    """
    Remove a glyph from a font.

    Args:
        font (Font): The font to remove the glyphs from.
        glyph_names_to_remove (Tuple[str]): The names of the glyphs to remove.
        glyph_ids_to_remove (Tuple[int]): The glyph IDs to remove.

    """
    result = font.remove_glyphs(
        glyph_names_to_remove=glyph_names_to_remove, glyph_ids_to_remove=glyph_ids_to_remove
    )
    if result:
        font.is_modified = True
        logger.opt(colors=True).info(f"Removed glyphs: <lc>{', '.join(list(result))}</lc>")


def rename_glyph(font: Font, old_name: str, new_name: str) -> None:
    """
    Rename a single glyph in a font file.

    Args:
        font (Font): The font to rename the glyph in.
        old_name (str): The old name of the glyph.
        new_name (str): The new name of the glyph.
    """
    result = font.rename_glyph(old_name=old_name, new_name=new_name)
    if result:
        font.is_modified = True
        logger.opt(colors=True).info(f"Renamed glyph: <lc>{old_name}</lc> to <lc>{new_name}</lc>")


def rename_glyphs(font: Font, source_file: Path) -> None:
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
    except Exception as e:
        raise RuntimeError from e

    if old_glyph_order == new_glyph_order:
        logger.info("The glyph order of the source font is the same as the current font.")
        return

    result = font.rename_glyphs(new_glyph_order=new_glyph_order)
    if result:
        font.is_modified = True


def set_production_names(font: Font) -> None:
    """
    Set the production names of glyphs in a font.

    Args:
        font (Font): The font to set the production names of.
    """
    renamed_glyphs = font.set_production_names()

    if renamed_glyphs:
        font.is_modified = True
        logger.info("Renamed glyphs:")
        for old_name, new_name in renamed_glyphs:
            logger.opt(colors=True).info(f"  {old_name} -> <lc>{new_name}</lc>")


def sort_glyphs(
    font: Font,
    sort_by: t.Literal["unicode", "alphabetical", "cannedDesign"] = "unicode",
) -> None:
    """
    Reorders the glyphs based on the Unicode values, in alphabetical order, or based on the canned
    design order.
    """
    if font.sort_glyphs(sort_by=sort_by):
        font.is_modified = True
        logger.info("Glyphs sorted")
