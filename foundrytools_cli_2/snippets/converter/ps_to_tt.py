import typing as t

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._g_l_y_f import (
    table__g_l_y_f,
    Glyph,
)  # pylint: disable=protected-access

from foundrytools_cli_2.lib import logger
from foundrytools_cli_2.lib.font import Font

T_CFF = "CFF "
T_LOCA = "loca"
T_GLYF = "glyf"
T_MAXP = "maxp"
T_POST = "post"
T_HMTX = "hmtx"
T_VORG = "VORG"
MAXP_TABLE_VERSION = 0x00010000


def build_ttf(
    font: Font, max_err: float = 1.0, reverse_direction: bool = True, post_format: float = 2.0
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

    glyph_order = font.ttfont.getGlyphOrder()

    font.ttfont[T_LOCA] = newTable(T_LOCA)
    font.ttfont[T_GLYF] = glyf = newTable(T_GLYF)
    glyf.glyphOrder = glyph_order
    glyf.glyphs = glyphs_to_quadratic(
        glyphs=font.ttfont.getGlyphSet(), max_err=max_err, reverse_direction=reverse_direction
    )
    del font.ttfont[T_CFF]
    if T_VORG in font.ttfont:
        del font.ttfont[T_VORG]
    glyf.compile(font.ttfont)
    update_hmtx(font=font, glyf=glyf)

    font.ttfont[T_MAXP] = maxp = newTable(T_MAXP)
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
    maxp.compile(font.ttfont)

    post = font.ttfont[T_POST]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    try:
        post.compile(font.ttfont)
    except OverflowError:
        post.formatType = 3

    font.ttfont.sfntVersion = "\000\001\000\000"
    return font


def update_hmtx(font: Font, glyf: table__g_l_y_f) -> None:
    """
    Update the 'hmtx' table of a font.

    Args:

        font (Font): The font to update.
        glyf: The 'glyf' table.
    """

    hmtx = font.ttfont[T_HMTX]
    for glyph_name, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyph_name] = (hmtx[glyph_name][0], glyph.xMin)


def glyphs_to_quadratic(
    glyphs: t.Dict, max_err: float = 1.0, reverse_direction: bool = False
) -> t.Dict[str, Glyph]:
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


def otf2ttf(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    tt = build_ttf(font=font, max_err=tolerance, reverse_direction=True)
    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}")
        tt.tt_scale_upem(new_upem=target_upm)

    out_file = font.make_out_file_name(overwrite=True)
    tt.save(out_file)
    logger.success(f"File saved to {out_file}")
