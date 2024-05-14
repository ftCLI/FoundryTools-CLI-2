import json
from pathlib import Path
import typing as t

from fontTools.ttLib.tables._c_m_a_p import table__c_m_a_p

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.cli.logger import logger


NAMES_UNICODES_FILE = Path(__file__).parent / "names_unicodes.json"
with open(NAMES_UNICODES_FILE, encoding="utf-8") as f:
    NAMES_UNICODES = json.load(f)


def collect_unmapped_glyphs(font: Font, reversed_cmap: t.Dict[str, int]) -> t.List[str]:
    """
    Collects the unmapped glyphs from the font.

    Args:
        font (Font): The font object.
        reversed_cmap (dict): The reversed cmap table.
    """
    unmapped_glyphs = []
    for glyph_name in font.ttfont.getGlyphOrder():
        if glyph_name not in reversed_cmap:
            unmapped_glyphs.append(glyph_name)
    return unmapped_glyphs


def remap_glyphs(unmapped_glyphs: t.List[str], cmap: table__c_m_a_p) -> t.List[str]:
    """
    Remaps the glyphs to their Unicode values.

    Args:
        unmapped_glyphs (list): The list of unmapped glyphs.
        cmap (table__c_m_a_p): The cmap table.
    """
    remapped_glyphs = []
    for glyph_name in unmapped_glyphs:
        unicode_value = NAMES_UNICODES.get(glyph_name)
        if unicode_value:
            logger.info(f"Remapping {glyph_name} to {hex(unicode_value)}")
            for subtable in cmap.tables:
                if subtable.isUnicode() and unicode_value in subtable.cmap:
                    continue
                subtable.cmap[unicode_value] = glyph_name
                remapped_glyphs.append(glyph_name)
    return remapped_glyphs


def main(font: Font) -> None:
    """
    Rename glyphs based on a mapping file.
    Args:
        font (Font): The font object to rename the glyphs from.
    """
    cmap = font.ttfont["cmap"]
    reversed_cmap = cmap.buildReversed()
    unmapped_glyphs = collect_unmapped_glyphs(font, reversed_cmap)
    remapped_glyphs = remap_glyphs(unmapped_glyphs, cmap)
    font.modified = bool(remapped_glyphs)
