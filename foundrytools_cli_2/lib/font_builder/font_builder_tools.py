import typing as t

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.psCharStrings import T2CharString
from fontTools.ttLib import TTFont


def build_otf(
    font: TTFont,
    charstrings_dict: t.Dict[str, T2CharString],
    ps_name: t.Optional[str] = None,
    font_info: t.Optional[t.Dict[str, t.Any]] = None,
    private_dict: t.Optional[t.Dict[str, t.Any]] = None,
) -> None:
    """
    Builds an OpenType font with FontBuilder.

    Args:
        font (TTFont): The TTFont object.
        ps_name (str): The PostScript name of the font.
        charstrings_dict (dict): The charstrings dictionary.
        font_info (dict): The font info.
        private_dict (dict): The private dict.
    """

    if not ps_name:
        ps_name = get_ps_name(font=font)
    if not font_info:
        font_info = get_font_info_dict(font=font)
    if not private_dict:
        private_dict = get_private_dict(font=font)

    fb = FontBuilder(font=font)
    fb.isTTF = False
    delete_ttf_tables(font=fb.font)
    fb.setupGlyphOrder(font.getGlyphOrder())
    fb.setupCFF(
        psName=ps_name,
        charStringsDict=charstrings_dict,
        fontInfo=font_info,
        privateDict=private_dict,
    )
    metrics = get_hmtx_values(font=fb.font, charstrings=charstrings_dict)
    fb.setupHorizontalMetrics(metrics)
    fb.setupDummyDSIG()
    fb.setupMaxp()
    post_values = get_post_values(font=fb.font)
    fb.setupPost(**post_values)


def delete_ttf_tables(font: TTFont) -> None:
    """
    Deletes TTF specific tables from a font.
    """
    ttf_tables = ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]
    for table in ttf_tables:
        if table in font:
            del font[table]


def get_ps_name(font: TTFont) -> str:
    """
    Gets the PostScript name of a font from a CFF table.

    Parameters:
        font (TTFont): The TTFont object.

    Returns:
        str: The PostScript name of the font.
    """
    if "CFF " not in font:
        return font["name"].getDebugName(6)

    cff_table = font["CFF "]
    return cff_table.cff.fontNames[0]


def get_font_info_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Gets the font info from a CFF table.

    Parameters:
        font (TTFont): The TTFont object.

    Returns:
        dict: The font info.

    """

    if "CFF " not in font:
        return build_font_info_dict(font)

    cff_table = font["CFF "]
    return {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }


def build_font_info_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Builds CFF topDict from a TTFont object.
    """

    font_revision = str(round(font["head"].fontRevision, 3)).split(".")
    major_version = str(font_revision[0])
    minor_version = str(font_revision[1]).ljust(3, "0")

    cff_font_info = {
        "version": ".".join([major_version, str(int(minor_version))]),
        "FullName": font["name"].getBestFullName(),
        "FamilyName": font["name"].getBestFamilyName(),
        "ItalicAngle": font["post"].italicAngle,
        "UnderlinePosition": font["post"].underlinePosition,
        "UnderlineThickness": font["post"].underlineThickness,
        "isFixedPitch": bool(font["post"].isFixedPitch),
    }

    return cff_font_info


def get_private_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Gets the private dict from a CFF table.

    Parameters:
        font (TTFont): The TTFont object.

    Returns:
        dict: The private dict.

    """
    if "CFF " not in font:
        return {}

    cff_table = font["CFF "]
    return {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].Private.rawDict.items()
        if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
    }


def get_hmtx_values(
    font: TTFont, charstrings: t.Dict[str, T2CharString]
) -> t.Dict[str, t.Tuple[int, int]]:
    """
    Get the horizontal metrics for a font.
    """
    glyph_set = font.getGlyphSet()
    advance_widths = {k: v.width for k, v in glyph_set.items()}
    lsb = {}
    for gn, cs in charstrings.items():
        lsb[gn] = cs.calcBounds(None)[0] if cs.calcBounds(None) is not None else 0
    metrics = {}
    for gn, advance_width in advance_widths.items():
        metrics[gn] = (advance_width, lsb[gn])
    return metrics


def get_post_values(font: TTFont) -> dict:
    """
    Setup CFF post table values
    """
    post_info = {
        "italicAngle": round(font["post"].italicAngle),
        "underlinePosition": font["post"].underlinePosition,
        "underlineThickness": font["post"].underlineThickness,
        "isFixedPitch": font["post"].isFixedPitch,
        "minMemType42": font["post"].minMemType42,
        "maxMemType42": font["post"].maxMemType42,
        "minMemType1": font["post"].minMemType1,
        "maxMemType1": font["post"].maxMemType1,
    }
    return post_info
