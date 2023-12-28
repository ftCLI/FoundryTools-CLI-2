import typing as t
from pathlib import Path

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
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
    recalc_timestamp: bool = False,
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
        recalc_timestamp: [Optional] Whether to recalculate the font's timestamp.
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

    in_file = font.file
    out_file = font.make_out_file_name(output_dir=output_dir, overwrite=overwrite)

    flavor = font.ttfont.flavor
    if flavor is not None:
        font.to_sfnt()

    if in_file != out_file or flavor is not None:
        font.save(out_file)

    hinted_font = hint_font(in_file=out_file, options=options)
    font.ttfont["CFF "] = hinted_font["CFF "]

    if flavor is not None:
        font = Font(out_file, recalc_timestamp=recalc_timestamp)
        font.ttfont.flavor = flavor
        font.ttfont.save(out_file)

    logger.success(f"File saved to {out_file}")
