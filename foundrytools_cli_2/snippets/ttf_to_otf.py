from typing import Dict

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.snippets.otf_to_ttf import otf_to_ttf


def ttf_to_otf(font: Font, charstrings: dict) -> Font:
    """
    Convert a TrueType font to a OpenType-PS font.

    Args:
        font (Font): The TrueType font to convert.
        charstrings (dict): The CFF charstrings.
    """
    cff_font_info = get_cff_font_info(font)
    post_values = get_post_values(font)

    fb = FontBuilder(font=font)
    fb.isTTF = False
    for table in ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]:
        if table in fb.font:
            del fb.font[table]

    fb.setupCFF(
        psName=font["name"].getDebugName(6),
        charStringsDict=charstrings,
        fontInfo=cff_font_info,
        privateDict={},
    )
    fb.setupDummyDSIG()
    fb.setupMaxp()
    fb.setupPost(**post_values)

    return fb.font


def get_cff_font_info(font: Font) -> dict:
    """
    Setup CFF topDict

    :return: A dictionary of the font info.
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


def get_post_values(font: Font) -> dict:
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


def get_charstrings(font: Font, tolerance: float = 1.0) -> Dict:
    """
    Get CFF charstrings using Qu2CuPen, falling back to T2CharStringPen if Qu2CuPen fails.

    :return: CFF charstrings.
    """

    charstrings = {}
    try:
        tolerance = tolerance / 1000 * font["head"].unitsPerEm
        failed, charstrings = get_qu2cu_charstrings(font, tolerance=tolerance)

        if len(failed) > 0:
            logger.info(f"Retrying to get {len(failed)} charstrings...")
            fallback_charstrings = get_fallback_charstrings(font, tolerance=tolerance)

            for c in failed:
                try:
                    charstrings[c] = fallback_charstrings[c]
                    logger.info(f"Successfully got charstring for {c}")
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"Failed to get charstring for {c}: {e}")

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Failed to convert {font.reader.file.name}: {e}")

    return charstrings


def get_qu2cu_charstrings(font: Font, tolerance: float = 1.0):
    """
    Get CFF charstrings using Qu2CuPen

    :return: CFF charstrings.
    """

    qu2cu_charstrings = {}
    failed = []
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
        try:
            glyph_set[k].draw(qu2cu_pen)
            qu2cu_charstrings[k] = t2_pen.getCharString()
        except NotImplementedError as e:
            logger.warning(f"Failed to get charstring for {k}: {e}")
            failed.append(k)

    return failed, qu2cu_charstrings


def get_t2_charstrings(font: Font) -> dict:
    """
    Get CFF charstrings using T2CharStringPen

    :return: CFF charstrings.
    """
    t2_charstrings = {}
    glyph_set = font.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        glyph_set[k].draw(t2_pen)
        charstring = t2_pen.getCharString()
        t2_charstrings[k] = charstring

    return t2_charstrings


def get_fallback_charstrings(font: Font, tolerance: float = 1.0) -> dict:
    """
    Get the charstrings from a fallback OTF font.
    """
    t2_charstrings = get_t2_charstrings(font=font)
    ps = ttf_to_otf(font=font, charstrings=t2_charstrings)
    tt = otf_to_ttf(font=ps, max_err=tolerance, reverse_direction=True)
    _, fallback_charstrings = get_qu2cu_charstrings(tt, tolerance=tolerance)
    return fallback_charstrings
