import os
import typing as t
from io import BytesIO
from pathlib import Path

from afdko.fdkutils import get_temp_dir_path, get_temp_file_path

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.otf.afdko_tools import hint_font


def main(
    font: Font,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: t.Optional[Path] = None,
    subroutinize: bool = True,
) -> None:
    """
    Applies hinting to an OpenType-PS font file and returns the font's 'CFF ' table.

    Args:
        font: The font to hint.
        allow_changes: [Optional] Boolean flag to allow changes to the font during hinting.
        allow_no_blues: [Optional] Boolean flag to allow hinting without blue zones.
        decimal: [Optional] Boolean flag to specify whether to round coordinates to integers during
            hinting.
        no_flex: [Optional] Boolean flag to disable flex hinting.
        no_hint_sub: [Optional] Boolean flag to disable hint substitution during hinting.
        reference_font: [Optional] Path to a reference font file.
        subroutinize: [Optional] Boolean flag to subroutinize the font after hinting.
    """

    validate_font(font)

    if not font.is_sfnt or font.file is None:
        process_font_file(
            font, allow_changes, allow_no_blues, decimal, no_flex, no_hint_sub, reference_font
        )
    else:
        hint_font_file(
            font,
            font.file,
            allow_changes,
            allow_no_blues,
            decimal,
            no_flex,
            no_hint_sub,
            reference_font,
        )

    buf = BytesIO()
    font.ttfont.save(buf, reorderTables=None)
    temp_font = Font(buf)

    if subroutinize:
        logger.info("Subroutinizing...")
        temp_font.ps_subroutinize()
        font.ttfont["CFF "] = temp_font.ttfont["CFF "]


def validate_font(font: Font) -> None:
    """
    Checks that the font is a PostScript font.
    """
    if not font.is_ps:
        raise ValueError("Font is not a PostScript font.")


def process_font_file(
    font: Font,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: t.Optional[Path] = None,
) -> None:
    """
    Applies hinting to an OpenType-PS font file and returns the font's 'CFF ' table.
    """
    # Create a temporary file
    temp_dir = get_temp_dir_path()
    temp_file = Path(get_temp_file_path(temp_dir))
    logger.info(f"Hinting font to {temp_file}...")
    try:
        flavor = font.ttfont.flavor
        if flavor:
            font.to_sfnt()
        font.ttfont.save(temp_file, reorderTables=None)
        hint_font_file(
            font,
            temp_file,
            allow_changes,
            allow_no_blues,
            decimal,
            no_flex,
            no_hint_sub,
            reference_font,
        )
        font.ttfont.flavor = flavor
    finally:
        # Remove the temporary file if it exists
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


def hint_font_file(
    font: Font,
    in_file: Path,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: t.Optional[Path] = None,
) -> None:
    """
    Applies hinting to an OpenType-PS font file and returns the font's 'CFF ' table.
    """
    logger.info("Hinting font...")
    font.ttfont["CFF "] = hint_font(
        in_file=in_file,
        allow_changes=allow_changes,
        allow_no_blues=allow_no_blues,
        decimal=decimal,
        no_flex=no_flex,
        no_hint_sub=no_hint_sub,
        reference_font=reference_font,
    )
    font.modified = True
