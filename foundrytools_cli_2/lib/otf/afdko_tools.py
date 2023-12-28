import typing as t
from contextlib import contextmanager
from pathlib import Path

from afdko.otfautohint.__main__ import ACOptions, _validate_path
from afdko.otfautohint.autohint import FontInstance, fontWrapper, openFont
from cffsubr import desubroutinize, subroutinize
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.C_F_F_ import table_C_F_F_

__all__ = ["cff_subr", "cff_desubr", "hint_font"]


@contextmanager
def _restore_flavor(font: TTFont) -> t.Iterator[None]:
    """
    This is a workaround to support subroutinization and desubroutinization for WOFF and WOFF2
    fonts with cffsubr without raising an exception. This context manager is used to temporarily
    set the font flavor to None and restore it after subroutinization or desubroutinization.
    """
    original_flavor = font.flavor
    font.flavor = None
    try:
        yield
    finally:
        font.flavor = original_flavor


def _validate_sfnt_version(font: TTFont) -> None:
    """
    Validate the sfntVersion of a font.
    """
    if not font.sfntVersion == "OTTO":
        raise NotImplementedError("Subroutinization is only supported for PostScript fonts.")


def cff_subr(font: TTFont) -> None:
    """
    Subroutinize a PostScript font.
    """
    _validate_sfnt_version(font=font)
    with _restore_flavor(font):
        subroutinize(otf=font)


def cff_desubr(font: TTFont) -> None:
    """
    Desubroutinize a PostScript font.
    """
    _validate_sfnt_version(font=font)
    with _restore_flavor(font):
        desubroutinize(otf=font)


def hint_font(
    in_file: Path,
    allow_changes: bool = False,
    allow_no_blues: bool = False,
    decimal: bool = False,
    no_flex: bool = False,
    no_hint_sub: bool = False,
    reference_font: t.Optional[Path] = None,
) -> table_C_F_F_:
    """
    Applies hinting to an OpenType-PS font file and returns the font's 'CFF ' table.

    Parameters:
        in_file: Path to the font file.
        allow_changes: [Optional] Boolean flag to allow changes to the font during hinting.
        allow_no_blues: [Optional] Boolean flag to allow hinting without blue zones.
        decimal: [Optional] Boolean flag to specify whether to round coordinates to integers during
            hinting.
        no_flex: [Optional] Boolean flag to disable flex hinting.
        no_hint_sub: [Optional] Boolean flag to disable hint substitution during hinting.
        reference_font: [Optional] Path to a reference font file.

    Returns:
        table_C_F_F_: The 'CFF ' table of the hinted font.
    """

    in_file = _validate_path(in_file)
    options = ACOptions()
    options.allowChanges = allow_changes
    options.allowNoBlues = allow_no_blues
    options.roundCoords = not decimal
    options.referenceFont = reference_font
    options.noFlex = no_flex
    options.noHintSub = no_hint_sub

    font = openFont(in_file, options=options)
    font_instance = FontInstance(font=font, inpath=in_file, outpath=None)
    fw = fontWrapper(options=options, fil=[font_instance])
    fw.hint()
    return fw.fontInstances[0].font.ttFont["CFF "]
