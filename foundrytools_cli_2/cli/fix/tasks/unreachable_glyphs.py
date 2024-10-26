from fontTools.subset import Options, Subsetter

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.constants import T_CMAP
from foundrytools_cli_2.lib.font import Font


def main(font: Font, recalc_timestamp: bool = False) -> None:
    """
    Removes unreachable glyphs from the font.
    Args:
        font: The font to remove the unreachable glyphs from.
        recalc_timestamp: Whether to recalculate the font's timestamp.

    Returns:
        None
    """
    options = Options()
    options.drop_tables = []
    options.passthrough_tables = True
    options.hinting_tables = ["*"]
    options.layout_features = ["*"]
    options.legacy_kern = True
    options.layout_closure = True
    options.layout_scripts = ["*"]
    options.ignore_missing_unicodes = True
    options.hinting = True
    options.glyph_names = True
    options.legacy_cmap = True
    options.symbol_cmap = True
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.retain_gids = False
    options.notdef_glyph = True
    options.notdef_outline = True
    options.recalc_bounds = True
    options.recalc_timestamp = recalc_timestamp
    options.prune_unicode_ranges = True
    options.prune_codepage_ranges = True
    options.recalc_average_width = True
    options.recalc_max_context = True
    options.canonical_order = False

    old_glyph_order = font.ttfont.getGlyphOrder()
    unicodes = []
    for t in font.ttfont[T_CMAP].tables:
        if t.isUnicode():
            unicodes.extend(t.cmap.keys())
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font=font.ttfont)
    new_glyph_order = font.ttfont.getGlyphOrder()

    font.modified = new_glyph_order != old_glyph_order
    removed_glyphs = set(old_glyph_order) - set(new_glyph_order)
    if removed_glyphs:
        logger.opt(colors=True).info(
            f"{len(removed_glyphs)} glyphs has been removed: \n" f"{', '.join(removed_glyphs)}"
        )
