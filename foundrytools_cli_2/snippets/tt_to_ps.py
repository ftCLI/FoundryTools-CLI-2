import typing as t

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.snippets.ps_to_tt import build_ttf


def build_otf(font: Font, charstrings: dict) -> Font:
    """
    Convert a TrueType font to a OpenType-PS font.

    Args:
        font (Font): The TrueType font to convert.
        charstrings (dict): The CFF charstrings.
    """
    cff_font_info = get_cff_font_info(font)
    post_values = get_post_values(font)

    fb = FontBuilder(font=font.ttfont)
    fb.isTTF = False
    for table in ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]:
        if table in fb.font:
            del fb.font[table]

    fb.setupCFF(
        psName=font.ttfont["name"].getDebugName(6),
        charStringsDict=charstrings,
        fontInfo=cff_font_info,
        privateDict={},
    )

    advance_widths = font.get_advance_widths()

    lsb = {}
    for gn, cs in charstrings.items():
        lsb[gn] = cs.calcBounds(None)[0] if cs.calcBounds(None) is not None else 0
    metrics = {}
    for gn, advance_width in advance_widths.items():
        metrics[gn] = (advance_width, lsb[gn])

    fb.setupHorizontalMetrics(metrics)
    fb.setupDummyDSIG()
    fb.setupMaxp()
    fb.setupPost(**post_values)

    return font


def get_cff_font_info(font: Font) -> dict:
    """
    Setup CFF topDict

    :return: A dictionary of the font info.
    """

    font_revision = str(round(font.ttfont["head"].fontRevision, 3)).split(".")
    major_version = str(font_revision[0])
    minor_version = str(font_revision[1]).ljust(3, "0")

    cff_font_info = {
        "version": ".".join([major_version, str(int(minor_version))]),
        "FullName": font.ttfont["name"].getBestFullName(),
        "FamilyName": font.ttfont["name"].getBestFamilyName(),
        "ItalicAngle": font.ttfont["post"].italicAngle,
        "UnderlinePosition": font.ttfont["post"].underlinePosition,
        "UnderlineThickness": font.ttfont["post"].underlineThickness,
        "isFixedPitch": bool(font.ttfont["post"].isFixedPitch),
    }

    return cff_font_info


def get_post_values(font: Font) -> dict:
    """
    Setup CFF post table values
    """
    post_info = {
        "italicAngle": round(font.ttfont["post"].italicAngle),
        "underlinePosition": font.ttfont["post"].underlinePosition,
        "underlineThickness": font.ttfont["post"].underlineThickness,
        "isFixedPitch": font.ttfont["post"].isFixedPitch,
        "minMemType42": font.ttfont["post"].minMemType42,
        "maxMemType42": font.ttfont["post"].maxMemType42,
        "minMemType1": font.ttfont["post"].minMemType1,
        "maxMemType1": font.ttfont["post"].maxMemType1,
    }
    return post_info


def get_charstrings(font: Font, tolerance: float = 1.0) -> t.Dict:
    """
    Get CFF charstrings using Qu2CuPen, falling back to T2CharStringPen if Qu2CuPen fails.

    :return: CFF charstrings.
    """

    charstrings: t.Dict = {}
    try:
        tolerance = tolerance / 1000 * font.ttfont["head"].unitsPerEm
        failed, charstrings = get_qu2cu_charstrings(font, tolerance=tolerance)

        if len(failed) > 0:
            logger.debug(f"Retrying to get {len(failed)} charstrings...")
            fallback_charstrings = get_fallback_charstrings(font, tolerance=tolerance)

            for c in failed:
                try:
                    charstrings[c] = fallback_charstrings[c]
                    logger.debug(f"Successfully got charstring for {c}")
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"Failed to get charstring for {c}: {e}")

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Failed to convert {font.file}: {e}")

    return charstrings


def get_qu2cu_charstrings(font: Font, tolerance: float = 1.0) -> t.Tuple[t.List, t.Dict]:
    """
    Get CFF charstrings using Qu2CuPen

    :return: CFF charstrings.
    """

    qu2cu_charstrings = {}
    failed = []
    glyph_set = font.ttfont.getGlyphSet()

    for k, v in glyph_set.items():
        t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
        qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=True, reverse_direction=True)
        try:
            glyph_set[k].draw(qu2cu_pen)
            qu2cu_charstrings[k] = t2_pen.getCharString()
        except NotImplementedError as e:
            logger.debug(f"Failed to get charstring for {k}: {e}")
            failed.append(k)

    return failed, qu2cu_charstrings


def get_t2_charstrings(font: Font) -> dict:
    """
    Get CFF charstrings using T2CharStringPen

    :return: CFF charstrings.
    """
    t2_charstrings = {}
    glyph_set = font.ttfont.getGlyphSet()

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
    otf = build_otf(font=font, charstrings=t2_charstrings)
    # We have a fallback OTF font with incorrect contours direction here, so we need to set
    # reverse_direction to False. Later Qu2CuPen will reverse the direction of the contours.
    ttf = build_ttf(font=otf, max_err=tolerance, reverse_direction=False)
    _, fallback_charstrings = get_qu2cu_charstrings(ttf, tolerance=tolerance)
    return fallback_charstrings


def ttf2otf(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
    subroutinize: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    logger.info("Decomponentizing source font...")
    font.tt_decomponentize()

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}")
        font.tt_scale_upem(new_upem=target_upm)

    logger.info("Getting charstrings...")
    charstrings = get_charstrings(font=font, tolerance=tolerance)

    logger.info("Converting to OTF...")
    otf = build_otf(font=font, charstrings=charstrings)

    if subroutinize:
        logger.info("Subroutinizing...")
        otf.ps_subroutinize()
