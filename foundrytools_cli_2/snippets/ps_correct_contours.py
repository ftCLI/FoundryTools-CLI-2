from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.tables import C_F_F_

from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.skia_tools import (
    skia_path_from_glyph,
    simplify_path,
    remove_tiny_paths,
    same_path,
    t2_charstring_from_skia_path,
)


def correct_otf_contours(font: Font, min_area: int = 25) -> None:
    """
    Corrects the contours of an OTF font.

    :param font: the font
    :param min_area: the minimum area of a path
    :return: None
    """

    if not font.is_ps:
        raise NotImplementedError("Not an OTF font")

    cff_table: C_F_F_.table_C_F_F_ = font["CFF "]
    glyph_set = font.getGlyphSet()
    charstrings = {}
    modified = []

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(width=v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstrings[k] = t2_pen.getCharString()

        path_1 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = skia_path_from_glyph(glyph_name=k, glyph_set=glyph_set)
        path_2 = simplify_path(path=path_2, glyph_name=k, clockwise=False)

        if min_area > 0:
            path_2 = remove_tiny_paths(path=path_2, glyph_name=k, min_area=min_area)

        if not same_path(path_1=path_1, path_2=path_2):
            cs = t2_charstring_from_skia_path(path=path_2, width=v.width)
            logger.debug(f"Corrected contours for glyph '{k}'")
            charstrings[k] = cs
            modified.append(k)

    if not modified:
        logger.info("No glyphs modified")
        return

    ps_name = cff_table.cff.fontNames[0]
    font_info = {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }
    private_dict = {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].Private.rawDict.items()
        if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
    }
    fb = FontBuilder(font=font)
    fb.setupCFF(
        psName=ps_name, fontInfo=font_info, privateDict=private_dict, charStringsDict=charstrings
    )