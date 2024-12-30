import typing as t
from pathlib import Path

from afdko.fdkutils import run_shell_command
from foundrytools import Font
from foundrytools.app.otf_check_outlines import run as otf_check_outlines
from foundrytools.lib.otf_builder import build_otf
from foundrytools.lib.qu2cu import quadratics_to_cubics_2

from foundrytools_cli_2.cli.logger import logger


def _build_out_file_name(font: Font, output_dir: t.Optional[Path], overwrite: bool = True) -> Path:
    """
    When converting a TrueType flavored web font to PS flavored web font, we need to add a suffix to
    the output file name to avoid overwriting the input file. This function builds the output file
    name.

    A file named "font.ttf" will be converted to "font.otf", while a file named
    "font.woff" will be converted to "font.otf.woff".

    Args:
        font (Font): The font to convert
        output_dir (t.Optional[Path]): The output directory
        overwrite (bool, optional): Whether to overwrite the output file if it already exists.
            Defaults to ``True``.

    Returns:
        Path: The output file name
    """
    flavor = font.ttfont.flavor
    suffix = ".otf" if flavor is not None else ""
    extension = font.get_file_ext() if flavor is not None else ".otf"
    return font.get_file_path(
        output_dir=output_dir, overwrite=overwrite, extension=extension, suffix=suffix
    )


def ttf2otf(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
    correct_contours: bool = True,
    check_outlines: bool = False,
    subroutinize: bool = True,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.

    Args:
        font (Font): The font to convert
        tolerance (float, optional): The maximum error allowed when converting the font to TrueType.
            Defaults to 1.0.
        target_upm (t.Optional[int], optional): The target UPM to scale the font to. Defaults to
            ``None``.
        correct_contours (bool, optional): Whether to correct the contours with pathops. Defaults to
            ``True``.
        check_outlines (bool, optional): Whether to check the outlines with tx. Default is ``True``.
        subroutinize (bool, optional): Whether to subroutinize the font. Defaults to ``True``.
        output_dir (t.Optional[Path], optional): The output directory. If ``None``, the output file
            will be saved in the same directory as the input file. Defaults to ``None``.
        overwrite (bool, optional): Whether to overwrite the output file if it already exists.
            Defaults to ``True``.
    """
    out_file = _build_out_file_name(font=font, output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    font.ttfont.flavor = None

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.scale_upm(target_upm=target_upm)

    # Adjust tolerance to font units per em after scaling, not before
    tolerance = tolerance / 1000 * font.t_head.units_per_em

    logger.info("Converting to OTF...")
    font.to_otf(tolerance=tolerance, correct_contours=correct_contours)

    if check_outlines:
        logger.info("Checking outlines...")
        otf_check_outlines(font)

    if subroutinize:
        logger.info("Subroutinizing...")
        font.subroutinize()

    font.ttfont.flavor = flavor
    font.save(out_file, reorder_tables=True)
    logger.success(f"File saved to {out_file}")


def ttf2otf_with_tx(
    font: Font,
    target_upm: t.Optional[int] = None,
    correct_contours: bool = True,
    check_outlines: bool = False,
    subroutinize: bool = True,
    output_dir: t.Optional[Path] = None,
    recalc_timestamp: bool = False,
    overwrite: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts using tx.

    Args:
        font (Font): The font to convert
        target_upm (t.Optional[int], optional): The target UPM to scale the font to. Defaults to
            ``None``, which means that the font will not be scaled.
        correct_contours (bool, optional): Whether to correct the contours with pathops. Defaults to
            ``True``.
        check_outlines (bool, optional): Whether to check the outlines with tx. Default is ``True``.
        subroutinize (bool, optional): Whether to subroutinize the font. Defaults to ``True``.
        output_dir (t.Optional[Path], optional): The output directory. If ``None``, the output file
            will be saved in the same directory as the input file. Defaults to ``None``.
        recalc_timestamp (bool, optional): Whether to recalculate the font's timestamp. Defaults to
            ``False``.
        overwrite (bool, optional): Whether to overwrite the output file if it already exists.
            Defaults to ``True``.
    """
    out_file = _build_out_file_name(font=font, output_dir=output_dir, overwrite=overwrite)
    cff_file = font.get_file_path(extension=".cff", output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    if flavor is not None:
        font.ttfont.flavor = None
        font.save(out_file, reorder_tables=None)
        font = Font(out_file, recalc_timestamp=recalc_timestamp)

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.scale_upm(target_upm=target_upm)
        font.ttfont.save(out_file, reorderTables=None)
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        tx_command = ["tx", "-cff", "-S", "+V", "+b", str(out_file), str(cff_file)]
        run_shell_command(tx_command, suppress_output=True)

    logger.info("Dumping the CFF table...")
    tx_command = ["tx", "-cff", "-S", "+V", "+b", str(font.file), str(cff_file)]
    run_shell_command(tx_command, suppress_output=True)

    logger.info("Building OTF...")
    charstrings_dict = quadratics_to_cubics_2(font=font.ttfont)
    build_otf(font=font.ttfont, charstrings_dict=charstrings_dict)
    font.save(out_file, reorder_tables=None)
    sfntedit_command = ["sfntedit", "-a", "CFF=" + str(cff_file), str(out_file)]
    run_shell_command(sfntedit_command, suppress_output=True)

    if correct_contours:
        logger.info("Correcting contours...")
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        font.correct_contours()

    font.t_os_2.recalc_avg_char_width()

    if check_outlines:
        logger.info("Checking outlines...")
        otf_check_outlines(font)

    if subroutinize:
        logger.info("Subroutinizing...")
        font.subroutinize()

    font.ttfont.flavor = flavor

    font.save(out_file, reorder_tables=None)
    cff_file.unlink(missing_ok=True)
    logger.success(f"File saved to {out_file}")
