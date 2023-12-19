import os
from pathlib import Path

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
    reference_font: Path = None,
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


def validate_font(font: Font):
    if not font.is_ps:
        raise ValueError("Font is not a PostScript font.")


def process_font_file(
    font: Font,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: Path = None,
):
    # Create a temporary file using os module
    temp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp.otf")
    try:
        flavor = font.ttfont.flavor
        if flavor:
            font.to_sfnt()
        font.ttfont.save(temp, reorderTables=None)
        hint_font_file(
            font,
            Path(temp),
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
        if os.path.exists(temp):
            os.remove(temp)


def hint_font_file(
    font: Font,
    in_file: Path,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: Path = None,
):
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
