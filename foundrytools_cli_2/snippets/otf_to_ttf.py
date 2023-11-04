from typing import Dict

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._g_l_y_f import Glyph  # pylint: disable=protected-access

from foundrytools_cli_2.lib.font import Font

T_CFF = "CFF "
T_LOCA = "loca"
T_GLYF = "glyf"
T_MAXP = "maxp"
T_POST = "post"
T_HMTX = "hmtx"
T_VORG = "VORG"
MAXP_TABLE_VERSION = 0x00010000


def otf_to_ttf(
        font: Font, max_err: float = 1.0, reverse_direction: bool = True, post_format=2.0
) -> Font:
    """
    Convert a OpenType font to a TrueType font.

    Args:
        font (Font): The OpenType font to convert.
        max_err (float, optional): The maximum approximation error, measured in UPEM. Defaults to
            1.0.
        reverse_direction (bool, optional): Whether to reverse the direction of the contours.
            Defaults to True.
        post_format (float, optional): The 'post' table format. Defaults to 2.0.
    """
    if font.is_tt:
        raise ValueError("The font is not an OpenType-PS font.")
    if font.is_variable:
        raise NotImplementedError("Variable fonts are not supported.")

    glyph_order = font.getGlyphOrder()

    font[T_LOCA] = newTable(T_LOCA)
    font[T_GLYF] = glyf = newTable(T_GLYF)
    glyf.glyphOrder = glyph_order
    glyf.glyphs = glyphs_to_quadratic(
        glyphs=font.getGlyphSet(), max_err=max_err, reverse_direction=reverse_direction
    )
    del font[T_CFF]
    if T_VORG in font:
        del font[T_VORG]
    glyf.compile(font)
    update_hmtx(font=font, glyf=glyf)

    font[T_MAXP] = maxp = newTable(T_MAXP)
    maxp.tableVersion = MAXP_TABLE_VERSION
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = max(
        len(g.components if hasattr(g, "components") else []) for g in glyf.glyphs.values()
    )
    maxp.compile(font)

    post = font[T_POST]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    try:
        post.compile(font)
    except OverflowError:
        post.formatType = 3

    font.sfntVersion = "\000\001\000\000"
    return font


def update_hmtx(font: Font, glyf):
    """
    Update the 'hmtx' table of a font.

    Args:

        font (Font): The font to update.
        glyf: The 'glyf' table.
    """

    hmtx = font[T_HMTX]
    for glyph_name, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyph_name] = (hmtx[glyph_name][0], glyph.xMin)


def glyphs_to_quadratic(glyphs, max_err=1.0, reverse_direction=False) -> Dict[str, Glyph]:
    """
    Convert the glyphs of a font to quadratic.

    Args:

        glyphs: The glyphs to convert.
        max_err (float, optional): The maximum approximation error, measured in UPEM. Defaults to
            1.0.
        reverse_direction (bool, optional): Whether to reverse the direction of the contours.

    Returns:
        The converted glyphs.
    """

    quad_glyphs = {}
    for gname in glyphs.keys():
        glyph = glyphs[gname]
        tt_pen = TTGlyphPen(glyphs)
        cu2qu_pen = Cu2QuPen(tt_pen, max_err=max_err, reverse_direction=reverse_direction)
        glyph.draw(cu2qu_pen)
        quad_glyphs[gname] = tt_pen.glyph()
    return quad_glyphs
