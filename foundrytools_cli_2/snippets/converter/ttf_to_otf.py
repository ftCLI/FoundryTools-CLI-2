import typing as t
from pathlib import Path

from afdko.fdkutils import run_shell_command

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.otf_builder import build_otf
from foundrytools_cli_2.lib.otf.t2_charstrings import get_t2_charstrings


def _build_out_file_name(font: Font, output_dir: t.Optional[Path], overwrite: bool) -> Path:
    """
    When converting a TrueType flavored web font to PS flavored web font, we need to add a suffix to
    the output file name to avoid overwriting the input file. This function builds the output file
    name.

    A file named "font.ttf" will be converted to "font.otf", while a file named
    "font.woff" will be converted to "font.otf.woff".
    """
    flavor = font.ttfont.flavor
    suffix = ".otf" if flavor is not None else ""
    extension = ".otf" if flavor is None else f".{flavor}"
    return font.make_out_file_name(
        output_dir=output_dir, overwrite=overwrite, extension=extension, suffix=suffix
    )


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

    Args:
        font: The font to convert.
        tolerance: The tolerance to use when converting to OTF.
        target_upm: The UPM to scale the font to.
        subroutinize: Whether to subroutinize the font.
        output_dir: The directory to save the font to.
        recalc_timestamp: Whether to recalculate the font's timestamp.
        overwrite: Whether to overwrite the existing file.
    """
    out_file = _build_out_file_name(font=font, output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    font.ttfont.flavor = None

    logger.info("Decomponentizing source font...")
    font.tt_decomponentize()

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)

    logger.info("Converting to OTF...")
    font.to_otf(tolerance=tolerance)

    font.save(out_file, reorder_tables=None)
    otf = Font(out_file, recalc_timestamp=recalc_timestamp)

    logger.info("Correcting contours...")
    otf.ps_correct_contours()

    if subroutinize:
        logger.info("Subroutinizing...")
        otf.ps_subroutinize()

    otf.ttfont.flavor = flavor
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
    out_file = _build_out_file_name(font=font, output_dir=output_dir, overwrite=overwrite)
    cff_file = font.make_out_file_name(extension=".cff", output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    if flavor is not None:
        font.ttfont.flavor = None
        font.save(out_file, reorder_tables=None)
        font = Font(out_file, recalc_timestamp=recalc_timestamp)

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)
        font.ttfont.save(out_file, reorderTables=None)
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        tx_command = ["tx", "-cff", "-S", "+V", "+b", str(out_file), str(cff_file)]
        run_shell_command(tx_command, suppress_output=True)

    logger.info("Dumping the CFF table...")
    tx_command = ["tx", "-cff", "-S", "+V", "+b", str(font.file), str(cff_file)]
    run_shell_command(tx_command, suppress_output=True)

    logger.info("Building OTF...")
    charstrings_dict = get_t2_charstrings(font=font.ttfont)
    build_otf(font=font.ttfont, charstrings_dict=charstrings_dict)
    font.save(out_file, reorder_tables=None)
    sfntedit_command = ["sfntedit", "-a", "CFF=" + str(cff_file), str(out_file)]
    run_shell_command(sfntedit_command, suppress_output=True)

    logger.info("Correcting contours...")
    font = Font(out_file, recalc_timestamp=recalc_timestamp)
    font.ps_correct_contours()

    if subroutinize:
        logger.info("Subroutinizing...")
        font.ps_subroutinize()

    font.ttfont.flavor = flavor

    font.save(out_file, reorder_tables=None)
    cff_file.unlink(missing_ok=True)
    logger.success(f"File saved to {out_file}")
