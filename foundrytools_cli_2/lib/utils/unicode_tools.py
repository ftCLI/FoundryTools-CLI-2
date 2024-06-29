import json
import typing as t

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

from foundrytools_cli_2.lib.constants import NAMES_TO_UNICODES_FILE

CharacterMapping = t.TypeVar("CharacterMapping", t.Dict[int, str], t.Dict[str, int])


def guess_unicode_from_name(glyph_name: str) -> t.Optional[int]:
    """
    Guess the Unicode value of a glyph from its name.

    Args:
        glyph_name (str): The name of the glyph.

    Returns:
        str: The Unicode value of the glyph.
    """

    for prefix in ("uni", "u"):
        if glyph_name.startswith(prefix):
            try:
                return int(glyph_name[len(prefix):], 16)
            except ValueError:
                return None


def build_cmap_from_glyph_names(glyphs_list: t.List[str]) -> CharacterMapping:
    """
    Get the Unicode values for the given list of glyph names.

    Args:
        glyphs_list (list): The list of glyph names.

    Returns:
        dict: A dictionary mapping Unicode values to glyph names.
    """
    with open(NAMES_TO_UNICODES_FILE, encoding="utf-8") as f:
        glyphs_to_codepoints = json.load(f)

    new_mapping: t.Dict[int, str] = {}
    for glyph_name in glyphs_list:
        unicode_value = glyphs_to_codepoints.get(glyph_name)
        if unicode_value:
            codepoint = int(unicode_value, 16)
            new_mapping.setdefault(codepoint, glyph_name)

    return new_mapping


def cmap_from_reversed_cmap(ttfont: TTFont) -> t.Dict[int, str]:
    """
    Rebuild the cmap from the reversed cmap. Alternative to getBestCmap.

    Args:
        ttfont (TTFont): The TTFont object.

    Returns:
        dict: A dictionary mapping Unicode values to glyph names.
    """
    reversed_cmap: t.Dict[str, t.Set[int]] = ttfont["cmap"].buildReversed()
    cmap_dict: t.Dict[int, str] = {}

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
    source_cmap: t.Dict[int, str], target_cmap: t.Dict[int, str]
) -> t.Tuple[t.Dict[int, str], t.List[t.Tuple[int, str]], t.List[t.Tuple[int, str, str]]]:
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
    subtable_format: int, platform_id: int, plat_enc_id: int, cmap: t.Dict[int, str]
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


def setup_character_map(ttfont: TTFont, mapping: t.Dict[int, str]) -> None:
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


def main(font: TTFont, remap_all: bool = False) -> None:
    """
    :param remap_all: A boolean indicating whether to remap all glyphs or only the unmapped ones.
    :param font: A TTFont object.
    :return: None

    The `main` method is used to perform glyph remapping on a TrueType font. It takes an optional
    boolean parameter `remap_all` which determines whether to remap all glyphs or only the unmapped
    ones. The method does not return any value.

    The method first creates a `TTFont` object using the `TEST_FONT_FILE` file. It then retrieves
    the glyph order of the font using the `getGlyphOrder` method. Next, it calls the
    `get_mapped_and_unmapped_glyphs` function to obtain the mapped and unmapped glyphs in the font.

    If the `remap_all` parameter is `False`, the method updates the existing character map.
    Otherwise, it creates a new mapping for all glyphs. The initial character map is obtained using
    the `getBestCmap` method. The additional character map is created using the
    `build_cmap_from_glyph_names` function with the `unmapped` list as the parameter.

    Next, the method calls the `update_character_map` function with `additional_cmap` as the
    source and `initial_cmap` as the target. It assigns the returned values of `updated_cmap`,
    `remapped`, and `duplicates` to their respective variables.

    The method then calls the `setup_character_map` function with the `ttfont` parameter set to
    `font` and the `mapping` parameter set to `updated_cmap`. It saves the modified font using
    `font.save` to a file named "remapped.ttf".

    Finally, the method calls the `print_results` function with various parameters including
    `remap_all`, `glyph_order`, `initial_cmap`, `additional_cmap`, `unmapped`, `remapped`,
    and `duplicates`.
    """

    glyph_order = font.getGlyphOrder()
    _, unmapped = get_mapped_and_unmapped_glyphs(font)

    if not remap_all:
        initial_cmap = font.getBestCmap()  # We can also use cmap_from_reversed_cmap
        additional_cmap = build_cmap_from_glyph_names(glyphs_list=unmapped)
    else:
        initial_cmap = {}
        additional_cmap = build_cmap_from_glyph_names(glyphs_list=glyph_order)

    updated_cmap, remapped, duplicates = update_character_map(
        source_cmap=additional_cmap, target_cmap=initial_cmap
    )
    setup_character_map(ttfont=font, mapping=updated_cmap)
