import typing as t
from pathlib import Path

from afdko.otfautohint.__main__ import ACOptions

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.otf.afdko_tools import hint_font

from . import get_file_to_process


def main(
    font: Font,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: t.Optional[Path] = None,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
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
        output_dir: [Optional] The directory where the font will be saved.
        overwrite: [Optional] Whether to overwrite the output file if it already exists.
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

    flavor = font.ttfont.flavor
    file_to_process = get_file_to_process(font, output_dir=output_dir, overwrite=overwrite)
    hinted_font = hint_font(in_file=file_to_process, options=options)
    font.ttfont["CFF "] = hinted_font["CFF "]
    font.ttfont.flavor = flavor
    font.modified = True
