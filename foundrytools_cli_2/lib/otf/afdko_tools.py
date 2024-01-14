import typing as t
from contextlib import contextmanager

from cffsubr import desubroutinize, subroutinize
from fontTools.ttLib import TTFont

__all__ = ["cff_subr", "cff_desubr"]


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
