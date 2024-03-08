import typing as t

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


def get_glyph_bounds(font: TTFont, glyph_name: str) -> t.Dict[str, float]:
    """
    Get the bounds of a glyph.

    :param font: The TTFont object.
    :param glyph_name: The name of the glyph.
    :return: The bounds of the glyph.
    """
    glyph_set = font.getGlyphSet()
    if glyph_name not in glyph_set:
        raise ValueError(f"Glyph '{glyph_name}' does not exist in the font.")

    bounds_pen = BoundsPen(glyphSet=glyph_set)

    glyph_set[glyph_name].draw(bounds_pen)
    bounds = {
        "xMin": bounds_pen.bounds[0],
        "yMin": bounds_pen.bounds[1],
        "xMax": bounds_pen.bounds[2],
        "yMax": bounds_pen.bounds[3],
    }

    return bounds
