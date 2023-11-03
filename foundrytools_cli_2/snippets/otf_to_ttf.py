from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTLibError, newTable

from foundrytools_cli_2.lib.font import Font


def otf_to_ttf(
        font: Font, max_err: float = 1.0, reverse_direction: bool = True, post_format=2.0
) -> None:
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

    glyphOrder = font.getGlyphOrder()

    font["loca"] = newTable("loca")
    font["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = glyphOrder
    glyf.glyphs = glyphs_to_quadratic(
        glyphs=font.getGlyphSet(), max_err=max_err, reverse_direction=reverse_direction
    )
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    glyf.compile(font)
    update_hmtx(font=font, glyf=glyf)

    font["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
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

    post = font["post"]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyphOrder
    try:
        post.compile(font)
    except OverflowError:
        post.formatType = 3

    font.sfntVersion = "\000\001\000\000"


def update_hmtx(font: Font, glyf):
    """
    Update the 'hmtx' table of a font.

    Args:

        font (Font): The font to update.
        glyf: The 'glyf' table.
    """

    hmtx = font["hmtx"]
    for glyphName, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyphName] = (hmtx[glyphName][0], glyph.xMin)


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

    quadGlyphs = {}
    for gname in glyphs.keys():
        glyph = glyphs[gname]
        ttPen = TTGlyphPen(glyphs)
        cu2quPen = Cu2QuPen(ttPen, max_err=max_err, reverse_direction=reverse_direction)
        glyph.draw(cu2quPen)
        quadGlyphs[gname] = ttPen.glyph()
    return quadGlyphs
