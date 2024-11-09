from fontTools.misc.psCharStrings import T2CharString
from fontTools.misc.roundTools import otRound
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph

from foundrytools_cli_2.lib.constants import T_CFF, T_GLYF, T_HEAD, T_HMTX
from foundrytools_cli_2.lib.font import Font

NOTDEF = ".notdef"
WIDTH_CONSTANT = 600
HEIGHT_CONSTANT = 1.25
THICKNESS_CONSTANT = 10


def draw_notdef_cff(font: Font, width: int, height: int, thickness: int) -> T2CharString:
    """
    Draws a '.notdef' glyph in a CFF font.

    Args:
        font (Font): The Font object.
        width (int): The width of the '.notdef' glyph.
        height (int): The height of the '.notdef' glyph.
        thickness (int): The thickness of the '.notdef' glyph.

    Returns:
        T2CharString: The '.notdef' glyph charstring.
    """
    pen = T2CharStringPen(width=0, glyphSet=font.ttfont.getGlyphSet())
    glyph_set = font.ttfont.getGlyphSet()

    # Draw the outer contour (counterclockwise)
    pen.moveTo((0, 0))
    pen.lineTo((width, 0))
    pen.lineTo((width, height))
    pen.lineTo((0, height))
    pen.closePath()

    # Draw the inner contour (clockwise)
    pen.moveTo((thickness, thickness))
    pen.lineTo((thickness, height - thickness))
    pen.lineTo((width - thickness, height - thickness))
    pen.lineTo((width - thickness, thickness))
    pen.closePath()

    glyph_set[NOTDEF].draw(pen)
    charstring = pen.getCharString()
    return charstring


def draw_notdef_glyf(font: Font, width: int, height: int, thickness: int) -> Glyph:
    """
    Draws a '.notdef' glyph in a TTF font.

    Args:
        font (Font): The Font object.
        width (int): The width of the '.notdef' glyph.
        height (int): The height of the '.notdef' glyph.
        thickness (int): The thickness of the '.notdef' glyph.

    Returns:
        Glyph: The '.notdef' glyph object.
    """

    # Do not use font.glyph_set property here, as TTGlyphPen expects a dict[str, Any] object, not a
    # _TTGlyphSet object
    pen = TTGlyphPen(glyphSet=font.ttfont.getGlyphSet())
    glyph_set = font.ttfont.getGlyphSet()

    # Draw the outer contour (clockwise)
    pen.moveTo((0, 0))
    pen.lineTo((0, height))
    pen.lineTo((width, height))
    pen.lineTo((width, 0))
    pen.closePath()

    # Draw the inner contour (counterclockwise)
    pen.moveTo((thickness, thickness))
    pen.lineTo((width - thickness, thickness))
    pen.lineTo((width - thickness, height - thickness))
    pen.lineTo((thickness, height - thickness))
    pen.closePath()

    glyph_set[NOTDEF].draw(pen)
    return pen.glyph()


def fix_empty_notdef(font: Font) -> None:
    """
    If the '.notdef' glyph is empty, draw a simple rectangle in it.

    Args:
        font (Font): The Font object.
    """
    glyph_set = font.ttfont.getGlyphSet()

    if NOTDEF not in glyph_set:
        raise KeyError("Font does not contain a '.notdef' glyph")

    rec_pen = RecordingPen()
    glyph_set[NOTDEF].draw(rec_pen)
    if rec_pen.value:
        raise ValueError("The '.notdef' glyph is not empty")

    head_table = font.ttfont[T_HEAD]
    width = otRound(head_table.unitsPerEm / 1000 * WIDTH_CONSTANT)
    height = width * HEIGHT_CONSTANT
    thickness = otRound(width / THICKNESS_CONSTANT)

    if font.is_ps:
        cff_table = font.ttfont[T_CFF]
        top_dict = cff_table.cff.topDictIndex[0]
        width = top_dict.Private.nominalWidthX
        charstring = draw_notdef_cff(font=font, width=width, height=height, thickness=thickness)
        charstring.compile()
        top_dict.CharStrings[NOTDEF].setBytecode(charstring.bytecode)

    if font.is_tt:
        glyf_table = font.ttfont[T_GLYF]
        glyph = draw_notdef_glyf(font=font, width=width, height=height, thickness=thickness)
        glyf_table[NOTDEF] = glyph

    font.ttfont[T_HMTX][NOTDEF] = (width, 0)
    font.is_modified = True
