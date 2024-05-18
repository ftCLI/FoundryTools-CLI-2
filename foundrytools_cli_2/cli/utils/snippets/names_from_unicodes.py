import json
from pathlib import Path
import typing as t

from fontTools.ttLib.tables._c_m_a_p import table__c_m_a_p

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.cli.logger import logger


NAMES_JSON = Path(__file__).parent / "names.json"
with open(NAMES_JSON, encoding="utf-8") as f:
    NAMES_CONTENT = json.load(f)


UNICODES_JSON = Path(__file__).parent / "unicodes.json"
with open(UNICODES_JSON, encoding="utf-8") as f:
    UNICODES_CONTENT = json.load(f)


def get_unicode_from_json(glyph_name: str) -> t.Optional[str]:
    """
    Get the Unicode value of a glyph.

    Args:
        glyph_name (str): The name of the glyph.

    Returns:
        str: The Unicode value of the glyph.
    """
    return NAMES_CONTENT.get(glyph_name)


def get_unicode_from_cmap(glyph_name: str, font: Font) -> t.Optional[str]:
    """
    Get the Unicode value of a glyph from the cmap table.

    Args:
        glyph_name (str): The name of the glyph.
        font (Font): The font object.

    Returns:
        str: The Unicode value of the glyph.
    """
    reversed_cmap: t.Dict[str, int] = {v: k for k, v in font.ttfont.getBestCmap().items()}
    if glyph_name in reversed_cmap:
        return "0x" + hex(reversed_cmap[glyph_name])[2:].upper().zfill(4)

    return None


def get_production_name(unicode_value: str) -> t.Optional[str]:
    """
    Get the name of a glyph from its Unicode value.

    Args:
        unicode_value (str): The Unicode value of the glyph.

    Returns:
        str: The name of the glyph.
    """
    if unicode_value not in UNICODES_CONTENT:
        return None
    return UNICODES_CONTENT.get(unicode_value)["production"][0]


def rename_glyphs(font: Font):
    """
    Rename glyphs in the font to their Unicode values.

    Args:
        font (Font): The font object.
    """

    glyph_order = font.ttfont.getGlyphOrder()
    new_glyph_order = []

    for glyph_name in glyph_order:
        unicode_from_cmap = get_unicode_from_cmap(glyph_name, font)
        unicode_from_json = get_unicode_from_json(glyph_name)
        if unicode_from_cmap != unicode_from_json:
            print(f"Glyph {glyph_name} {unicode_from_cmap} {unicode_from_json}")
        # continue
        if not unicode_from_cmap:
            new_glyph_order.append(glyph_name)
            continue

        production_name = get_production_name(unicode_from_cmap)
        if not production_name or production_name in glyph_order:
            new_glyph_order.append(glyph_name)
            continue

        new_glyph_order.append(production_name)

    name_map = dict(zip(glyph_order, new_glyph_order))

    from ufo2ft.postProcessor import PostProcessor
    PostProcessor.rename_glyphs(font.ttfont, name_map)

    font.modified = True
