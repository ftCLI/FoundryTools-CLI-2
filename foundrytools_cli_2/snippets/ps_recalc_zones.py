import typing as t
from collections import Counter

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.ttFont import TTFont

__all__ = ["recalc_zones"]


class GlyphBounds(t.TypedDict):
    """
    A type representing the bounds of a glyph.
    """

    xMin: float
    yMin: float
    xMax: float
    yMax: float


def get_glyph_bounds(font: TTFont, glyph_name: str) -> GlyphBounds:
    """
    Get the bounds of a glyph.

    Parameters:
        font (TTFont): The TTFont object.
        glyph_name (str): The name of the glyph.

    Returns:
        GlyphBounds: The bounds of the glyph.

    Raises:
        ValueError: If the glyph does not exist in the font.
    """
    glyph_set = font.getGlyphSet()
    if glyph_name not in glyph_set:
        raise ValueError(f"Glyph '{glyph_name}' does not exist in the font.")

    bounds_pen = BoundsPen(glyphSet=glyph_set)

    glyph_set[glyph_name].draw(bounds_pen)
    bounds = GlyphBounds(
        xMin=bounds_pen.bounds[0],
        yMin=bounds_pen.bounds[1],
        xMax=bounds_pen.bounds[2],
        yMax=bounds_pen.bounds[3],
    )

    return bounds


def get_glyph_bounds_many(font: TTFont, glyph_names: t.List[str]) -> t.Dict[str, GlyphBounds]:
    """
    Get the bounds of multiple glyphs in a given font.

    Parameters:
        font (TTFont): The TTFont object.
        glyph_names (List[str]): A list of glyph names.

    Returns:
        dict: A dictionary containing glyph names as keys and GlyphBounds objects as values.
    """
    glyphs_bounds = {}
    for glyph_name in glyph_names:
        try:
            bounds = get_glyph_bounds(font=font, glyph_name=glyph_name)
            glyphs_bounds[glyph_name] = bounds
        except ValueError:
            pass

    return glyphs_bounds


def get_pair(counter: Counter) -> t.List[float]:
    """
    Get the two most common elements from the given counter.

    Parameters:
        counter (Counter): The counter object containing elements and their counts.

    Returns:
        List[float]: List containing the pair of most common elements.
    """
    most_common = counter.most_common(2)
    if len(counter) == 1:
        return [most_common[0][0], most_common[0][0]]
    return sorted([most_common[0][0], most_common[1][0]])


def lists_overlaps(lists: t.List[t.List[float]]) -> bool:
    """
    Check if there are overlapping intervals in a list of lists.

    Args:
        lists (List[List[float]]): A list of lists, where each inner list represents an interval.

    Returns:
        bool: True if there are overlapping intervals, False otherwise.
    """
    for i in range(len(lists) - 1):
        if lists[i][1] > lists[i + 1][0]:
            return True
    return False


def fix_lists_overlaps(lists: t.List[t.List[float]]) -> t.List[t.List[float]]:
    """
    Fixes overlaps in a list of lists of floats.

    Args:
        lists (List[List[float]]): A list of lists of floats.

    Returns:
        List[List[float]]: The input list with any overlaps fixed.
    """
    for i in range(len(lists) - 1):
        if lists[i][1] > lists[i + 1][0]:
            lists[i + 1][0] = lists[i][1]
            lists[i + 1] = sorted(lists[i + 1])
    return lists


def calculate_zone(
    font: TTFont, glyph_names: t.List[str], min_or_max: t.Literal["yMin", "yMax"]
) -> t.List[float]:
    """
    Calculates the minimum and maximum vertical values for a given zone.

    Parameters:
        font: TTFont object representing the font.
        glyph_names: List of glyph names to process.
        min_or_max: Literal specifying whether to process the minimum ('yMin') or maximum ('yMax')
            values.

    Returns:
        List of float values representing the minimum or maximum vertical values for each glyph.

    """
    data = get_glyph_bounds_many(font=font, glyph_names=glyph_names)
    counter = Counter([v[min_or_max] for v in data.values()])
    return get_pair(counter)


def recalc_zones(font: TTFont) -> t.Tuple[t.List[int], t.List[int]]:
    """
    Recalc Zones

    Recalculates the zones for a given TTFont object.

    Parameters:
        font (TTFont): The TTFont object.

    Returns:
        Tuple[List[int], List[int]]: A tuple containing two lists. The first list contains the
            values for the OtherBlues zones, and the second list contains the values for the
            BlueValues zones.
    """

    uppercase_letters = [chr(i) for i in range(65, 91)]
    lowercase_letters = [chr(i) for i in range(97, 123)]

    uppercase_descenders = ["J", "Q"]
    lowercase_descenders = ["f", "g", "j", "p", "q", "y"]
    lowercase_ascenders = ["b", "d", "f", "h", "k", "l", "t"]

    # Get descender zone
    descender_glyphs = list(set(lowercase_descenders) - {'f', 'j'})
    descender_zone = calculate_zone(font=font, glyph_names=descender_glyphs, min_or_max="yMin")

    # Get baseline zone
    baseline_glyphs = list(
        set(uppercase_letters + lowercase_letters)
        - set(lowercase_descenders)
        - set(uppercase_descenders)
    )
    baseline_zone = calculate_zone(font=font, glyph_names=baseline_glyphs, min_or_max="yMin")

    # Get x-height zone
    x_height_glyphs = list(set(lowercase_letters) - set(lowercase_ascenders + ['i', 'j']))
    x_height_zone = calculate_zone(font=font, glyph_names=x_height_glyphs, min_or_max="yMax")

    # Get cap-height zone
    uppercase_zone = calculate_zone(font=font, glyph_names=uppercase_letters, min_or_max="yMax")

    # Get ascender zone
    ascender_glyphs = list(set(lowercase_ascenders) - {'t'})
    ascender_zone = calculate_zone(font=font, glyph_names=ascender_glyphs, min_or_max="yMax")

    zones = sorted([descender_zone, baseline_zone, x_height_zone, uppercase_zone, ascender_zone])
    if lists_overlaps(zones):
        zones = fix_lists_overlaps(zones)

    other_blues = [int(v) for v in zones[0]]
    blue_values = [int(v) for v in zones[1] + zones[2] + zones[3] + zones[4]]

    return other_blues, blue_values
