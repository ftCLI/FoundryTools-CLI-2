import typing as t
from pathlib import Path

from afdko.otfautohint.__main__ import ReportOptions, _validate_path, get_stemhist_options
from afdko.otfautohint.autohint import FontInstance, fontWrapper, openFont
from afdko.otfautohint.hinter import glyphHinter
from afdko.otfautohint.report import Report
from fontTools.ttLib import TTFont

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.utils.path_tools import get_temp_file_path

H_STEM_GLYPHS = ["A", "H", "T", "S", "C", "O"]
V_STEM_GLYPHS = ["E", "H", "I", "K", "L", "M", "N", "T", "U"]


def get_report(
    file_path: Path, glyph_list: t.List[str]
) -> t.Tuple[t.List[t.Tuple[int, int, t.List[str]]], t.List[t.Tuple[int, int, t.List[str]]]]:
    """
    Retrieves stem data from a font file for a given list of glyphs.

    Args:
        file_path`: The path to the font file.
        glyph_list`: A list of glyph names for which stem data will be
        retrieved.

    Returns:
        Tuple: a tuple containing two lists: the first list contains the horizontal stem data,
        and the second list contains the vertical stem data. Each list contains tuples of the
        form (stem width, stem count, glyph names).
    """
    file_path = _validate_path(file_path)
    _, parsed_args = get_stemhist_options(args=[file_path])
    options = ReportOptions(parsed_args)
    options.report_all_stems = True
    options.report_zones = False
    options.glyphList = glyph_list

    font = openFont(file_path, options=options)
    font_instance = FontInstance(font=font, inpath=file_path, outpath=file_path)

    fw = fontWrapper(options=options, fil=[font_instance])
    dict_record = fw.dictManager.getDictRecord()

    hinter = glyphHinter(options=options, dictRecord=dict_record)
    hinter.initialize(options=options, dictRecord=dict_record)
    gmap = map(hinter.hint, fw)

    report = Report()
    for name, r in gmap:
        report.glyphs[name] = r

    h_stems, v_stems, _, _ = report._get_lists(options)
    h_stems.sort(key=report._sort_count)
    v_stems.sort(key=report._sort_count)

    return h_stems, v_stems


def get_current_stems(font: TTFont) -> t.Tuple[t.Optional[int], t.Optional[int]]:
    """
    Get the current stem values for a given TTFont object.

    Args:
        font: A `TTFont` object representing the font file.

    Returns:
        Tuple: a tuple containing the current stem values for horizontal and vertical stems. The
        first value in the tuple represents the horizontal stem value, and the second value
        represents the vertical stem value.
    """
    private = font["CFF "].cff.topDictIndex[0].Private
    try:
        std_hw = private.StdHW
    except AttributeError:
        std_hw = None
    try:
        std_vw = private.StdVW
    except AttributeError:
        std_vw = None
    return std_hw, std_vw


def set_font_stems(font: TTFont, std_hw: int, std_vw: int) -> None:
    """
    Set the stem values for a given TTFont object.

    Args:
        font: A `TTFont` object representing the font file.
        std_hw: The new value for the horizontal stem.
        std_vw: The new value for the vertical stem.
    """
    private = font["CFF "].cff.topDictIndex[0].Private
    private.StdHW = std_hw
    private.StdVW = std_vw


def recalc_stems(
    file_path: Path,
    h_stems_glyphs: t.Optional[t.List[str]] = None,
    v_stems_glyphs: t.Optional[t.List[str]] = None,
) -> t.Tuple[int, int]:
    """
    Recalculates the StdHW and StdVW values for a given font file.

    Args:
        file_path: A `Path` object representing the path to the file.
        h_stems_glyphs: A list of glyph names to use for calculating the horizontal stems.
        v_stems_glyphs: A list of glyph names to use for calculating the vertical stems.

    Returns:
        Tuple: a tuple containing the new StdHW and StdVW values. The first value in the tuple
        represents the new horizontal stem value, and the second value represents the new vertical
        stem value.
    """

    if h_stems_glyphs is None:
        h_stems_glyphs = H_STEM_GLYPHS
    if v_stems_glyphs is None:
        v_stems_glyphs = V_STEM_GLYPHS

    h_stems, _ = get_report(file_path=file_path, glyph_list=h_stems_glyphs)
    _, v_stems = get_report(file_path=file_path, glyph_list=v_stems_glyphs)

    if not h_stems:
        raise ValueError("No horizontal stems found")
    if not v_stems:
        raise ValueError("No vertical stems found")

    return int(h_stems[0][1]), int(v_stems[0][1])


def main(font: Font) -> None:
    """
    Recalculates the hinting stems of an OTF font.

    Args:
        font (Font): The font object to recalculate the hinting stems for.
    """
    if not font.is_ps:
        logger.error("Font is not a PostScript font")
        return

    if font.file is None:
        logger.error("Font has no file path")
        return

    flavor = font.ttfont.flavor
    temp_file = get_temp_file_path()
    if flavor is not None:
        font.ttfont.flavor = None
        font.save(font.temp_file)
        input_file = font.temp_file
    else:
        input_file = font.file

    logger.info("Getting stems...")
    current_std_h_w, current_std_v_w = get_current_stems(font.ttfont)
    std_h_w, std_v_w = recalc_stems(input_file)
    logger.info(f"StdHW: {current_std_h_w} -> {std_h_w}")
    logger.info(f"StdVW: {current_std_v_w} -> {std_v_w}")
    temp_file.unlink(missing_ok=True)

    if current_std_h_w == std_h_w and current_std_v_w == std_v_w:
        logger.info("Stems are already up-to-date")
    else:
        set_font_stems(font.ttfont, std_h_w, std_v_w)
        font.ttfont.flavor = flavor
        font.is_modified = True
