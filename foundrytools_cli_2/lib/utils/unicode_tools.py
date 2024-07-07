import json
import typing as t

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from ufo2ft.postProcessor import PostProcessor

from foundrytools_cli_2.lib.constants import NAMES_TO_UNICODES_FILE, UNICODES_TO_NAMES_FILE

_CharacterMap = t.Dict[int, str]


with open(NAMES_TO_UNICODES_FILE, encoding="utf-8") as f:
    NAMES_TO_UNICODES = json.load(f)

with open(UNICODES_TO_NAMES_FILE, encoding="utf-8") as f:
    UNICODES_TO_NAMES = json.load(f)


def calc_unicode_from_name(glyph_name: str) -> t.Optional[str]:
    """
    Guess the Unicode value of a glyph from its name.

    Args:
        glyph_name (str): The name of the glyph.

    Returns:
        str: The Unicode value of the glyph.
    """

    for prefix in ("uni", "u"):
        if glyph_name.startswith(prefix) and len(glyph_name) == 7:
            try:
                _ = int(glyph_name[len(prefix) :], 16)
                return glyph_name.replace(prefix, "0x")
            except ValueError:
                return None
    return None


def calc_name_from_unicode(unicode_value: str) -> t.Optional[str]:
    """
    Guess the name of a glyph from its Unicode value.

    Args:
        unicode_value (str): The Unicode value of the glyph.

    Returns:
        str: The name of the glyph.
    """

    try:
        codepoint = int(unicode_value, 16)
    except ValueError:
        return None

    if 0 <= codepoint <= 0xFFFF:
        return f"uni{unicode_value.replace('0x', '').upper()}"
    if 0x10000 <= codepoint <= 0x10FFFF:
        return f"u{unicode_value.replace('0x', '').upper()}"
    return None


def get_production_name(unicode_value: str) -> t.Optional[str]:
    """
    Get the production name of a glyph from its Unicode value.

    Args:
        unicode_value (str): The Unicode value of the glyph.

    Returns:
        str: The production name of the glyph.
    """
    return UNICODES_TO_NAMES.get(unicode_value, {}).get("production", None)


def get_friendly_name(unicode_value: str) -> t.Optional[str]:
    """
    Get the friendly name of a glyph from its Unicode value.

    Args:
        unicode_value (str): The Unicode value of the glyph.

    Returns:
        str: The first friendly name of the glyph.
    """
    return UNICODES_TO_NAMES.get(unicode_value, {}).get("friendly", [None])[0]


def cmap_from_glyph_names(glyphs_list: t.List[str]) -> _CharacterMap:
    """
    Get the Unicode values for the given list of glyph names.

    Args:
        glyphs_list (list): The list of glyph names.

    Returns:
        dict: A dictionary mapping Unicode values to glyph names.
    """
    new_mapping: _CharacterMap = {}
    for glyph_name in glyphs_list:
        if glyph_name.startswith("f_"):
            print(f"Skipping {glyph_name}")
        unicode_value = NAMES_TO_UNICODES.get(glyph_name)
        if not unicode_value:
            unicode_value = calc_unicode_from_name(glyph_name)
        if unicode_value:
            codepoint = int(unicode_value, 16)
            new_mapping.setdefault(codepoint, glyph_name)

    return new_mapping


def cmap_from_reversed_cmap(ttfont: TTFont) -> _CharacterMap:
    """
    Rebuild the cmap from the reversed cmap. Alternative to getBestCmap.

    Args:
        ttfont (TTFont): The TTFont object.

    Returns:
        dict: A dictionary mapping Unicode values to glyph names.
    """
    reversed_cmap: t.Dict[str, t.Set[int]] = ttfont["cmap"].buildReversed()
    cmap_dict: _CharacterMap = {}

    for glyph_name, codepoints in reversed_cmap.items():
        for codepoint in codepoints:
            cmap_dict[codepoint] = glyph_name

    # Sort the dictionary by codepoint
    cmap_dict = dict(sorted(cmap_dict.items(), key=lambda item: item[0]))

    return cmap_dict


def get_mapped_and_unmapped_glyphs(ttfont: TTFont) -> t.Tuple[t.List[str], t.List[str]]:
    """
    Collect the unmapped glyphs from the given TTFont object.

    Args:
        ttfont (TTFont): The TTFont object.

    Returns:
        list: A list of unmapped glyph names.
    """
    glyph_order = ttfont.getGlyphOrder()
    reversed_cmap: t.Dict[str, t.Set[int]] = ttfont["cmap"].buildReversed()

    mapped_glyphs = []
    unmapped_glyphs = []

    for glyph_name in glyph_order:
        if glyph_name in reversed_cmap:
            mapped_glyphs.append(glyph_name)
        else:
            unmapped_glyphs.append(glyph_name)
    return mapped_glyphs, unmapped_glyphs


def update_character_map(
    source_cmap: _CharacterMap, target_cmap: _CharacterMap
) -> t.Tuple[_CharacterMap, t.List[t.Tuple[int, str]], t.List[t.Tuple[int, str, str]]]:
    """
    Update the target character map with the source character map.

    Args:
        source_cmap (dict): The source character map.
        target_cmap (dict): The target character map.
    """
    updated_cmap = target_cmap.copy()
    duplicates: t.List[t.Tuple[int, str, str]] = []
    remapped: t.List[t.Tuple[int, str]] = []

    for codepoint, glyph_name in source_cmap.items():
        if codepoint in updated_cmap:
            duplicates.append((codepoint, glyph_name, updated_cmap[codepoint]))
        else:
            remapped.append((codepoint, glyph_name))
            updated_cmap[codepoint] = glyph_name

    return updated_cmap, remapped, duplicates


def create_cmap_tables(
    subtable_format: int, platform_id: int, plat_enc_id: int, cmap: _CharacterMap
) -> CmapSubtable:
    """
    Create a cmap subtable with the given parameters.
    """
    cmap_table = CmapSubtable.newSubtable(subtable_format)
    cmap_table.platformID = platform_id
    cmap_table.platEncID = plat_enc_id
    cmap_table.language = 0
    cmap_table.cmap = cmap
    return cmap_table


def setup_character_map(ttfont: TTFont, mapping: _CharacterMap) -> None:
    """
    Set up the character map for the given TTFont object.

    Args:
        ttfont (TTFont): The TTFont object.
        mapping (dict): The character map dictionary.
    """
    out_tables: t.List[CmapSubtable] = []

    max_unicode = max(mapping, default=0)  # Avoid max() error on empty dict
    if max_unicode > 0xFFFF:
        cmap_3_1 = {k: v for k, v in mapping.items() if k <= 0xFFFF}
        cmap_3_10 = mapping
    else:
        cmap_3_1 = mapping
        cmap_3_10 = None

    if cmap_3_1:
        out_tables.append(create_cmap_tables(4, 3, 1, cmap_3_1))
        out_tables.append(create_cmap_tables(4, 0, 3, cmap_3_1))

    if cmap_3_10:
        out_tables.append(create_cmap_tables(12, 3, 10, cmap_3_10))
        out_tables.append(create_cmap_tables(12, 0, 4, cmap_3_10))

    cmap_table = newTable("cmap")
    cmap_table.tableVersion = 0
    cmap_table.tables = out_tables

    ttfont["cmap"] = cmap_table


def rebuild_character_map(
    font: TTFont, remap_all: bool = False
) -> t.Tuple[t.List[t.Tuple[int, str]], t.List[t.Tuple[int, str, str]]]:
    """
    Rebuild the character map for the given TTFont object.

    Args:
        font (TTFont): The TTFont object.
        remap_all (bool): Whether to remap all glyphs.

    Returns:
        tuple: A tuple containing the remapped and duplicate glyphs.
    """

    glyph_order = font.getGlyphOrder()
    _, unmapped = get_mapped_and_unmapped_glyphs(font)

    if not remap_all:
        target_cmap = font.getBestCmap()  # We can also use cmap_from_reversed_cmap
        source_cmap = cmap_from_glyph_names(glyphs_list=unmapped)
    else:
        target_cmap = {}
        source_cmap = cmap_from_glyph_names(glyphs_list=glyph_order)

    updated_cmap, remapped, duplicates = update_character_map(
        source_cmap=source_cmap, target_cmap=target_cmap
    )
    setup_character_map(ttfont=font, mapping=updated_cmap)

    return remapped, duplicates


def set_production_names(font: TTFont) -> t.List[t.Tuple[str, str]]:
    """
    Set the production names for the glyphs in the given TTFont object.

    Args:
        font (TTFont): The TTFont object.
    """
    old_glyph_order = font.getGlyphOrder()
    new_glyph_order = []
    renamed_glyphs: t.List[t.Tuple[str, str]] = []

    print(calc_unicode_from_name("uniFB00"))
    print(calc_name_from_unicode("0xFB00"))
    print(get_production_name("0xFB00"))
    print("f_f" in old_glyph_order)

    for glyph_name in old_glyph_order:
        # Check if the glyph name is in the NAMES_TO_UNICODES dictionary
        unicode_value = NAMES_TO_UNICODES.get(glyph_name)
        # If not, calculate the Unicode value from the glyph name
        if not unicode_value:
            unicode_value = calc_unicode_from_name(glyph_name)

        if not unicode_value:
            new_glyph_order.append(glyph_name)
            continue

        production_name = get_production_name(unicode_value)
        if not production_name or production_name in old_glyph_order:
            new_glyph_order.append(glyph_name)
            continue

        new_glyph_order.append(production_name)
        renamed_glyphs.append((glyph_name, production_name))

    if not renamed_glyphs:
        return []

    rename_map = dict(zip(old_glyph_order, new_glyph_order))
    PostProcessor.rename_glyphs(otf=font, rename_map=rename_map)

    return renamed_glyphs


def rename_glyph(font: TTFont, old_name: str, new_name: str) -> bool:
    """
    Rename a glyph in the given TTFont object.

    Args:
        font (TTFont): The TTFont object.
        old_name (str): The old name of the glyph.
        new_name (str): The new name of the glyph.
    """
    old_glyph_order = font.getGlyphOrder()
    new_glyph_order = []

    if old_name not in old_glyph_order:
        raise ValueError(f"Glyph '{old_name}' not found in the font.")

    if new_name in old_glyph_order:
        raise ValueError(f"Glyph '{new_name}' already exists in the font.")

    for glyph_name in old_glyph_order:
        if glyph_name == old_name:
            print(f"Renaming {old_name} to {new_name}.")
            new_glyph_order.append(new_name)
        else:
            new_glyph_order.append(glyph_name)

    rename_map = dict(zip(old_glyph_order, new_glyph_order))
    PostProcessor.rename_glyphs(otf=font, rename_map=rename_map)

    return new_glyph_order != old_glyph_order
