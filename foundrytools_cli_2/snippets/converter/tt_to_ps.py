import typing as t
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.snippets.converter.ps_to_tt import build_ttf


def delete_ttf_tables(font: TTFont) -> None:
    """
    Deletes TTF specific tables from a font.
    """
    ttf_tables = ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]
    for table in ttf_tables:
        if table in font:
            del font[table]


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
    metrics = get_hmtx_values(font=fb.font, charstrings=charstrings)
    fb.setupHorizontalMetrics(metrics)
    fb.setupDummyDSIG()
    fb.setupMaxp()
    fb.setupPost(**post_values)

    return font


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


def get_cff_font_info(font: Font) -> dict:
    """
    Setup CFF topDict
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
    ttf = build_ttf(font=otf, max_err=tolerance, reverse_direction=False)
    _, fallback_charstrings = get_qu2cu_charstrings(ttf, tolerance=tolerance)
    return fallback_charstrings


def ttf2otf(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
    subroutinize: bool = True,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    out_file = font.make_out_file_name(extension=".otf", output_dir=output_dir, overwrite=overwrite)

    logger.info("Decomponentizing source font...")
    font.tt_decomponentize()

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)

    logger.info("Getting charstrings...")
    charstrings = get_charstrings(font=font, tolerance=tolerance)

    logger.info("Converting to OTF...")
    otf = build_otf(font=font, charstrings=charstrings)

    otf.save(out_file, reorder_tables=None)
    otf = Font(out_file, recalc_timestamp=recalc_timestamp)

    # logger.info("Correcting contours...")
    # otf.ps_correct_contours(min_area=25, subroutinize=False)

    logger.info("Getting hinting values...")
    zones = otf.ps_recalc_zones()
    stems = otf.ps_recalc_stems()
    otf.ps_set_zones(zones[0], zones[1])
    otf.ps_set_stems(stems[0], stems[1])

    if subroutinize:
        logger.info("Subroutinizing...")
        otf.ps_subroutinize()

    otf.save(out_file, reorder_tables=True)

    logger.success(f"File saved to {out_file}")


def ttf2otf_with_tx(
    font: Font,
    target_upm: t.Optional[int] = None,
    subroutinize: bool = True,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts using tx.
    """
    from foundrytools_cli_2.lib.otf.ps_correct_contours import get_fixed_charstrings
    from afdko.fdkutils import run_shell_command

    out_file = font.make_out_file_name(extension=".otf", output_dir=output_dir, overwrite=overwrite)
    cff_file = font.make_out_file_name(extension=".cff", output_dir=output_dir, overwrite=overwrite)

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)
        font.ttfont.save(out_file, reorderTables=None)
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        tx_command = ["tx", "-cff", "-S", "+V", "+b", str(out_file), str(cff_file)]
        run_shell_command(tx_command, suppress_output=True)

    tx_command = ["tx", "-cff", "-S", "+V", "+b", str(font.file), str(cff_file)]
    run_shell_command(tx_command, suppress_output=True)

    ps_name = font.ttfont["name"].getDebugName(6)
    charstrings_dict = get_t2_charstrings(font=font)
    font_info = get_cff_font_info(font)
    post_values = get_post_values(font)
    private_dict = {}

    fb = FontBuilder(font=font.ttfont)
    fb.setupGlyphOrder(font.ttfont.getGlyphOrder())
    fb.isTTF = False
    delete_ttf_tables(font=fb.font)
    fb.setupCFF(
        psName=ps_name,
        charStringsDict=charstrings_dict,
        fontInfo=font_info,
        privateDict=private_dict,
    )
    fb.setupMaxp()
    fb.setupPost(**post_values)
    fb.font.save(out_file, reorderTables=True)

    sfntedit_command = ["sfntedit", "-a", "CFF=" + str(cff_file), str(out_file)]
    run_shell_command(sfntedit_command, suppress_output=True)

    font = Font(out_file, recalc_timestamp=recalc_timestamp)
    fb = FontBuilder(font=font.ttfont)
    fb.setupGlyphOrder(font.ttfont.getGlyphOrder())
    fb.isTTF = False
    charstrings_dict, _ = get_fixed_charstrings(font=font.ttfont)

    fb.setupCFF(
        psName=ps_name,
        charStringsDict=charstrings_dict,
        fontInfo=font_info,
        privateDict=private_dict,
    )
    mtx = get_hmtx_values(font=font.ttfont, charstrings=charstrings_dict)
    fb.setupHorizontalMetrics(mtx)
    fb.setupDummyDSIG()
    fb.setupMaxp()
    fb.setupPost(**post_values)

    fb.font.save(out_file, reorderTables=None)
    zones = font.ps_recalc_zones()
    stems = font.ps_recalc_stems()
    font.ps_set_zones(zones[0], zones[1])
    font.ps_set_stems(stems[0], stems[1])

    fb.font.save(out_file, reorderTables=True)
    logger.success(f"File saved to {out_file}")

    if subroutinize:
        tx_command = ["tx", "-cff", "+S", "+V", "+b", str(out_file), str(cff_file)]
        run_shell_command(tx_command, suppress_output=True)
        run_shell_command(sfntedit_command)

    cff_file.unlink(missing_ok=True)
