import json
import typing as t

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from ufo2ft.postProcessor import PostProcessor

from foundrytools_cli_2.lib.constants import NAMES_TO_UNICODES_FILE, T_CMAP, UNICODES_TO_NAMES_FILE

_CharacterMap = t.Dict[int, str]
_ReversedCmap = t.Dict[str, t.Set[int]]

with open(NAMES_TO_UNICODES_FILE, encoding="utf-8") as f:
    NAMES_TO_UNICODES = json.load(f)

with open(UNICODES_TO_NAMES_FILE, encoding="utf-8") as f:
    UNICODES_TO_NAMES = json.load(f)


def _uni_str_from_int(codepoint: int) -> t.Optional[str]:
    """
    Get a Unicode string from an integer.

    Args:
        codepoint (int): The codepoint of the glyph.

    Returns:
        str: The Unicode string (e.g. "0x0041").
    """
    if codepoint < 0 or codepoint > 0x10FFFF:
        return None

    if codepoint > 0xFFFF:
        return f"0x{codepoint:06x}"

    return f"0x{codepoint:04x}"


def _uni_str_from_glyph_name(glyph_name: str) -> t.Optional[str]:
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
                _ = int(glyph_name[len(prefix):], 16)
                return glyph_name.replace(prefix, "0x")
            except ValueError:
                return None
    return None


def _uni_str_from_reversed_cmap(glyph_name: str, reversed_cmap: _ReversedCmap) -> t.Optional[str]:
    """
    Get the Unicode value of a glyph from the reversed cmap.

    Args:
        glyph_name (str): The name of the glyph.
        reversed_cmap (dict): The reversed character map.

    Returns:
        str: The Unicode value of the glyph.
    """
    codepoints = reversed_cmap.get(glyph_name)
    if not codepoints:
        return None
    return _uni_str_from_int(list(codepoints)[0])


def _glyph_name_from_uni_str(uni_str: str) -> t.Optional[str]:
    """
    Guess the name of a glyph from its Unicode value.

    Args:
        uni_str (str): The Unicode value of the glyph.

    Returns:
        str: The name of the glyph.
    """

    try:
        codepoint = int(uni_str, 16)
    except ValueError:
        return None

    if 0 <= codepoint <= 0xFFFF:
        return f"uni{uni_str.replace('0x', '').upper()}"
    if 0x10000 <= codepoint <= 0x10FFFF:
        return f"u{uni_str.replace('0x', '').upper()}"
    return None


def _prod_name_from_uni_str(uni_str: str) -> t.Optional[str]:
    """
    Get the production name of a glyph from its Unicode value.

    Args:
        uni_str (str): The Unicode value of the glyph.

    Returns:
        str: The production name of the glyph.
    """
    return UNICODES_TO_NAMES.get(uni_str, {}).get("production", None)


def _prod_name_from_glyph_name(glyph_name: str) -> t.Optional[str]:
    """
    Get the production name of a glyph from its name.

    Args:
        glyph_name (str): The name of the glyph.

    Returns:
        str: The production name of the glyph.
    """
    uni_str = NAMES_TO_UNICODES.get(glyph_name)
    if not uni_str:
        uni_str = _uni_str_from_glyph_name(glyph_name)
    if not uni_str:
        return None
    return _prod_name_from_uni_str(uni_str)


def _friendly_name_from_uni_str(uni_str: str) -> t.Optional[str]:
    """
    Get the friendly name of a glyph from its Unicode value.

    Args:
        uni_str (str): The Unicode value of the glyph.

    Returns:
        str: The first friendly name of the glyph.
    """
    return UNICODES_TO_NAMES.get(uni_str, {}).get("friendly", [None])[0]


def _cmap_from_glyph_names(glyphs_list: t.List[str]) -> _CharacterMap:
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
            unicode_value = _uni_str_from_glyph_name(glyph_name)
        if unicode_value:
            codepoint = int(unicode_value, 16)
            new_mapping.setdefault(codepoint, glyph_name)

    return new_mapping


def _cmap_from_reversed_cmap(reversed_cmap: t.Dict[str, t.Set[int]]) -> _CharacterMap:
    """
    Rebuild the cmap from the reversed cmap. Alternative to getBestCmap.

    Args:
        reversed_cmap (dict): The reversed character map.

    Returns:
        dict: A dictionary mapping Unicode values to glyph names.
    """
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
    reversed_cmap: t.Dict[str, t.Set[int]] = ttfont[T_CMAP].buildReversed()

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

    cmap_table = newTable(T_CMAP)
    cmap_table.tableVersion = 0
    cmap_table.tables = out_tables

    ttfont[T_CMAP] = cmap_table


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
        source_cmap = _cmap_from_glyph_names(glyphs_list=unmapped)
    else:
        target_cmap = {}
        source_cmap = _cmap_from_glyph_names(glyphs_list=glyph_order)

    updated_cmap, remapped, duplicates = update_character_map(
        source_cmap=source_cmap, target_cmap=target_cmap
    )
    setup_character_map(ttfont=font, mapping=updated_cmap)

    return remapped, duplicates


def _get_multi_mapped_glyphs(reversed_cmap: t.Dict[str, t.Set[int]]) -> t.List[
    t.Tuple[str, t.List[int]]]:
    """
    Get the glyphs that are mapped to multiple Unicode values.

    Args:
        reversed_cmap (dict): The reversed character map.

    Returns:
        list: A list of glyphs that are mapped to multiple Unicode values.
    """
    multi_mapped = []
    for glyph_name, codepoints in reversed_cmap.items():
        if len(codepoints) > 1:
            multi_mapped.append((glyph_name, list(codepoints)))
    return multi_mapped


def set_production_names(ttfont: TTFont) -> t.List[t.Tuple[str, str]]:
    """
    Set the production names for the glyphs in the given TTFont object.

    Args:
        ttfont (TTFont): The TTFont object.
    """
    old_glyph_order = ttfont.getGlyphOrder()
    new_glyph_order = []
    renamed_glyphs: t.List[t.Tuple[str, str]] = []
    reversed_cmap: _ReversedCmap = ttfont[T_CMAP].buildReversed()

    for glyph_name in old_glyph_order:

        # Check if the glyph is present in the reversed cmap
        uni_str = _uni_str_from_reversed_cmap(glyph_name, reversed_cmap)

        # If not, check if the Unicode value is present in the JSON file
        if not uni_str:
            uni_str = NAMES_TO_UNICODES.get(glyph_name)

        # If not, calculate the Unicode value from the glyph name
        if not uni_str:
            uni_str = _uni_str_from_glyph_name(glyph_name)

        # If not, skip the glyph
        if not uni_str:
            new_glyph_order.append(glyph_name)
            continue

        production_name = _prod_name_from_uni_str(uni_str)

        if production_name == glyph_name:
            new_glyph_order.append(glyph_name)
            continue

        if not production_name or production_name in new_glyph_order:
            new_glyph_order.append(glyph_name)
            continue

        new_glyph_order.append(production_name)
        renamed_glyphs.append((glyph_name, production_name))
        print(f"Renamed {glyph_name} to {production_name}")

    if not renamed_glyphs:
        return []

    rename_map = dict(zip(old_glyph_order, new_glyph_order))
    PostProcessor.rename_glyphs(otf=ttfont, rename_map=rename_map)
    rebuild_character_map(font=ttfont, remap_all=True)

    return renamed_glyphs
