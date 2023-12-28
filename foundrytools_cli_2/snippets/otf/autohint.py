import os
import typing as t
from io import BytesIO
from pathlib import Path

from afdko.fdkutils import get_temp_dir_path, get_temp_file_path
from afdko.otfautohint.__main__ import ACOptions

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

    if not font.is_ps:
        raise ValueError("Font is not a PostScript font.")

    options = ACOptions()
    options.allow_changes = allow_changes
    options.allow_no_blues = allow_no_blues
    options.decimal = decimal
    options.no_flex = no_flex
    options.no_hint_sub = no_hint_sub
    options.reference_font = reference_font

    logger.info("Hinting font...")

    flavor = font.ttfont.flavor
    if flavor is not None or font.file is None:
        temp_dir = get_temp_dir_path()
        temp_file = get_temp_file_path(temp_dir)
        font.to_sfnt()
        font.save(temp_file, reorder_tables=None)
        hinted_font = hint_font(in_file=temp_file, options=options)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    else:
        hinted_font = hint_font(in_file=font.file, options=options)

    font.ttfont["CFF "] = hinted_font["CFF "]

    buf = BytesIO()
    font.save(buf, reorder_tables=None)
    temp_font = Font(buf)

    if subroutinize:
        logger.info("Subroutinizing...")
        temp_font.ps_subroutinize()
        font.ttfont["CFF "] = temp_font.ttfont["CFF "]

    font.ttfont.flavor = flavor
    font.modified = True
