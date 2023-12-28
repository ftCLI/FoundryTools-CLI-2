import typing as t
from contextlib import contextmanager
from pathlib import Path

from afdko.otfautohint.__main__ import ACOptions, _validate_path
from afdko.otfautohint.autohint import FontInstance, fontWrapper, openFont
from cffsubr import desubroutinize, subroutinize
from fontTools.ttLib import TTFont

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
