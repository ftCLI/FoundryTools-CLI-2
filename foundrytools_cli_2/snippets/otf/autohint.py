import typing as t
from pathlib import Path

from afdko.otfautohint.__main__ import ACOptions, _validate_path
from afdko.otfautohint.autohint import FontInstance, fontWrapper, openFont
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.snippets.otf import get_file_to_process


def hint_font(
    in_file: Path,
    options: ACOptions,
) -> TTFont:
    """
    Applies hinting to an OpenType-PS font file and returns the hinted TTFont object.

    Parameters:
        in_file: Path to the font file.
        options: An ACOptions object containing the options to use for hinting.

    Returns:
        TTFont: A hinted TTFont object.
    """

    in_file = _validate_path(in_file)
    font = openFont(in_file, options=options)
    font_instance = FontInstance(font=font, inpath=in_file, outpath=None)
    fw = fontWrapper(options=options, fil=[font_instance])
    fw.hint()
    return fw.fontInstances[0].font.ttFont


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
