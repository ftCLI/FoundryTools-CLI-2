import typing as t
from pathlib import Path

from afdko.fdkutils import run_shell_command

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_builder.font_builder_tools import build_otf
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.t2_charstrings import (
    fix_charstrings,
    from_true_type,
    get_t2_charstrings,
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
    """
    out_file = font.make_out_file_name(extension=".otf", output_dir=output_dir, overwrite=overwrite)

    logger.info("Decomponentizing source font...")
    font.tt_decomponentize()

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)

    logger.info("Getting charstrings...")
    charstrings = from_true_type(font=font.ttfont, tolerance=tolerance)

    logger.info("Converting to OTF...")
    build_otf(font=font.ttfont, charstrings_dict=charstrings)
    font.save(out_file, reorder_tables=None)
    otf = Font(out_file, recalc_timestamp=recalc_timestamp)

    logger.info("Correcting contours...")
    fixed_charstrings, _ = fix_charstrings(font=otf.ttfont)
    build_otf(font=otf.ttfont, charstrings_dict=fixed_charstrings)

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

    out_file = font.make_out_file_name(extension=".otf", output_dir=output_dir, overwrite=overwrite)
    cff_file = font.make_out_file_name(extension=".cff", output_dir=output_dir, overwrite=overwrite)

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
    charstrings_dict, _ = fix_charstrings(font=font.ttfont)
    build_otf(font=font.ttfont, charstrings_dict=charstrings_dict)
    font.save(out_file, reorder_tables=None)

    logger.info("Getting hinting values...")
    zones = font.ps_recalc_zones()
    stems = font.ps_recalc_stems()
    font.ps_set_zones(zones[0], zones[1])
    font.ps_set_stems(stems[0], stems[1])
    font.save(out_file, reorder_tables=True)

    if subroutinize:
        logger.info("Subroutinizing...")
        tx_command = ["tx", "-cff", "+S", "+V", "+b", str(out_file), str(cff_file)]
        run_shell_command(tx_command, suppress_output=True)
        run_shell_command(sfntedit_command)

    cff_file.unlink(missing_ok=True)

    logger.success(f"File saved to {out_file}")
