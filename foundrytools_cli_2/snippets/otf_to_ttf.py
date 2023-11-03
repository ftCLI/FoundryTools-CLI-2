import copy
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTLibError, newTable

from foundrytools_cli_2.lib.font import Font


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
    if font.sfntVersion != "OTTO":
        raise TTLibError("Not a OpenType font (bad sfntVersion)")

    font_copy = copy.deepcopy(font)

    glyph_order = font_copy.getGlyphOrder()

    font_copy["loca"] = newTable("loca")
    font_copy["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = glyph_order
    glyf.glyphs = glyphs_to_quadratic(
        glyphs=font_copy.getGlyphSet(), max_err=max_err, reverse_direction=reverse_direction
    )
    del font_copy["CFF "]
    if "VORG" in font_copy:
        del font_copy["VORG"]
    glyf.compile(font_copy)
    update_hmtx(font=font_copy, glyf=glyf)

    MAXP_TABLE_VERSION = 0x00010000
    font_copy["maxp"] = maxp = newTable("maxp")
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
    maxp.compile(font_copy)

    post = font_copy["post"]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    try:
        post.compile(font_copy)
    except OverflowError:
        post.formatType = 3

    font_copy.sfntVersion = "\000\001\000\000"
    return font_copy


def update_hmtx(font: Font, glyf):
    """
    Update the 'hmtx' table of a font.

    Args:

        font (Font): The font to update.
        glyf: The 'glyf' table.
    """

    hmtx = font["hmtx"]
    for glyph_name, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyph_name] = (hmtx[glyph_name][0], glyph.xMin)


def glyphs_to_quadratic(glyphs, max_err=1.0, reverse_direction=False) -> dict:
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
