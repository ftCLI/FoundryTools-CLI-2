import typing as t

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.psCharStrings import T2CharString
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import (
    T_CFF,
    T_HEAD,
    T_NAME,
    T_POST,
)


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
        charstrings_dict (dict): The charstrings dictionary.
        ps_name (str, optional): The PostScript name of the font. Defaults to None.
        font_info (dict, optional): The font info dictionary. Defaults to None.
        private_dict (dict, optional): The private dictionary. Defaults to None.
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

    Args:
        font (TTFont): The TTFont object.
    """
    ttf_tables = ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]
    for table in ttf_tables:
        if table in font:
            del font[table]


def get_ps_name(font: TTFont) -> str:
    """
    Gets the PostScript name of a font from a CFF table.

    Args:
        font (TTFont): The TTFont object.

    Returns:
        str: The PostScript name of the font.
    """
    if T_CFF not in font:
        return font[T_NAME].getDebugName(6)

    cff_table = font[T_CFF]
    return cff_table.cff.fontNames[0]


def get_font_info_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Gets the font info from a CFF table.

    Args:
        font (TTFont): The TTFont object.

    Returns:
        dict: The font info.
    """

    if T_CFF not in font:
        return build_font_info_dict(font)

    cff_table = font[T_CFF]
    return {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }


def build_font_info_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Builds CFF topDict from a TTFont object.

    Args:
        font (TTFont): The TTFont object.

    Returns:
        dict: The CFF topDict.
    """

    font_revision = str(round(font[T_HEAD].fontRevision, 3)).split(".")
    major_version = str(font_revision[0])
    minor_version = str(font_revision[1]).ljust(3, "0")

    name_table = font[T_NAME]
    post_table = font[T_POST]
    cff_font_info = {
        "version": ".".join([major_version, str(int(minor_version))]),
        "FullName": name_table.getBestFullName(),
        "FamilyName": name_table.getBestFamilyName(),
        "ItalicAngle": post_table.italicAngle,
        "UnderlinePosition": post_table.underlinePosition,
        "UnderlineThickness": post_table.underlineThickness,
        "isFixedPitch": bool(post_table.isFixedPitch),
    }

    return cff_font_info


def get_private_dict(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Gets the private dict from a CFF table.

    Args:
        font (TTFont): The TTFont object.

    Returns:
        dict: The private dict.
    """
    if T_CFF not in font:
        return {}

    cff_table = font[T_CFF]
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

    Args:
        font (TTFont): The TTFont object.
        charstrings (dict): The charstrings dictionary.

    Returns:
        dict: The horizontal metrics.
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


def get_post_values(font: TTFont) -> t.Dict[str, t.Any]:
    """
    Setup CFF post table values

    Args:
        font (TTFont): The TTFont object.

    Returns:
        dict: The post table values.
    """
    post_table = font[T_POST]
    post_info = {
        "italicAngle": round(post_table.italicAngle),
        "underlinePosition": post_table.underlinePosition,
        "underlineThickness": post_table.underlineThickness,
        "isFixedPitch": post_table.isFixedPitch,
        "minMemType42": post_table.minMemType42,
        "maxMemType42": post_table.maxMemType42,
        "minMemType1": post_table.minMemType1,
        "maxMemType1": post_table.maxMemType1,
    }
    return post_info
