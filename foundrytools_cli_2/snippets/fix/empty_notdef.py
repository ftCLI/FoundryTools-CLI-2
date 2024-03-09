import typing as t

from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.ttGlyphSet import _TTGlyphSetCFF, _TTGlyphSetGlyf

from foundrytools_cli_2.lib.constants import (
    CFF_TABLE_TAG,
    GLYF_TABLE_TAG,
    HEAD_TABLE_TAG,
    HMTX_TABLE_TAG,
    OS_2_TABLE_TAG,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.pathops.skia_tools import is_empty_glyph

NOTDEF = ".notdef"


def draw_empty_notdef_cff(
    glyph_set: _TTGlyphSetCFF, width: int, height: int, thickness: int
) -> T2CharString:
    """
    Draws an empty .notdef glyph in a CFF font.

    Parameters:
        glyph_set (_TTGlyphSetCFF): The glyph set to which the .notdef glyph belongs.
        width (int): The width of the .notdef glyph.
        height (int): The height of the .notdef glyph.
        thickness (int): The thickness of the .notdef glyph.

    Returns:
        None
    """

    pen = T2CharStringPen(width=width, glyphSet=glyph_set)
    notdef_glyph = glyph_set[NOTDEF]

    # Draw the outer contour (clockwise)
    pen.moveTo((0, 0))
    pen.lineTo((width, 0))
    pen.lineTo((width, height))
    pen.lineTo((0, height))
    pen.closePath()

    # Draw the inner contour (counterclockwise)
    pen.moveTo((thickness, thickness))
    pen.lineTo((thickness, height - thickness))
    pen.lineTo((width - thickness, height - thickness))
    pen.lineTo((width - thickness, thickness))
    pen.closePath()

    notdef_glyph.draw(pen)
    charstring = pen.getCharString()
    charstring.compile()
    return charstring


def draw_empty_notdef_glyf(
    glyph_set: t.Union[t.Dict[str, t.Any], _TTGlyphSetGlyf], width: int, height: int, thickness: int
) -> Glyph:
    """
    Draws an empty .notdef glyph in a glyf font.

    Parameters:
        glyph_set (_TTGlyphSetGlyf): The glyph set to which the .notdef glyph belongs.
        width (int): The width of the .notdef glyph.
        height (int): The height of the .notdef glyph.
        thickness (int): The thickness of the .notdef glyph.

    Returns:
        None
    """
    pen = TTGlyphPen(glyphSet=glyph_set)
    notdef_glyph = glyph_set[NOTDEF]

    # Draw the outer contour (clockwise)
    pen.moveTo((0, 0))
    pen.lineTo((0, height))
    pen.lineTo((width, height))
    pen.lineTo((width, 0))
    pen.closePath()

    # Draw the inner contour (clockwise)
    pen.moveTo((thickness, thickness))
    pen.lineTo((width - thickness, thickness))
    pen.lineTo((width - thickness, height - thickness))
    pen.lineTo((thickness, height - thickness))
    pen.closePath()

    notdef_glyph.draw(pen)
    return pen.glyph()


def fix_empty_notdef(font: Font) -> None:
    """
    Fixes the empty .notdef glyph by adding a simple rectangle.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    glyph_set = font.ttfont.getGlyphSet()

    if NOTDEF not in glyph_set:
        raise ValueError("Font does not contain a .notdef glyph")

    if not is_empty_glyph(glyph_set=glyph_set, glyph_name=NOTDEF):
        return

    width = round(font.ttfont[HEAD_TABLE_TAG].unitsPerEm / 1000 * 600)
    height = font.ttfont[OS_2_TABLE_TAG].sCapHeight or round(width * 1.25)
    thickness = round(width / 10)

    if isinstance(glyph_set, _TTGlyphSetCFF):
        charstring = draw_empty_notdef_cff(
            glyph_set=glyph_set, width=width, height=height, thickness=thickness
        )
        charstrings = font.ttfont[CFF_TABLE_TAG].cff.topDictIndex[0].CharStrings
        charstrings[NOTDEF].bytecode = charstring.bytecode

    if isinstance(glyph_set, _TTGlyphSetGlyf):
        draw_empty_notdef_glyf(glyph_set=glyph_set, width=width, height=height, thickness=thickness)
        font.ttfont[GLYF_TABLE_TAG][NOTDEF] = draw_empty_notdef_glyf(
            glyph_set=glyph_set, width=width, height=height, thickness=thickness
        )

    font.ttfont[HMTX_TABLE_TAG][NOTDEF] = (width, 0)
    font.modified = True
