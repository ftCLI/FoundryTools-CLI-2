"""
A subclass of fontTools.ttLib.TTFont
"""


from pathlib import Path
import typing as t

from fontTools.ttLib.ttFont import TTFont

SFNT_POSTSCRIPT = "OTTO"
SFNT_TRUETYPE = "0/1/0/0"
FLAVOR_WOFF = "woff"
FLAVOR_WOFF2 = "woff2"
FVAR_TABLE = "fvar"


class Font(TTFont):
    """
    The Font class is a subclass of TTFont and provides additional properties to check the type and
    flavor of a font file.

    Example Usage:
    >>>font = Font("font.ttf")
    >>>print(font.is_postscript)  # False
    >>>print(font.is_truetype)  # True
    >>>print(font.is_woff)  # False
    >>>print(font.is_woff2)  # False
    >>>print(font.is_static)  # True
    >>>print(font.is_variable)  # False
    """

    def __init__(
        self,
        file: t.Optional[t.Union[str, Path]] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
        lazy: t.Optional[bool] = None,
    ) -> None:
        super().__init__(
            file=file,
            recalcBBoxes=recalc_bboxes,
            recalcTimestamp=recalc_timestamp,
            lazy=lazy,
        )

    @property
    def is_postscript(self) -> bool:
        """
        Check if the font has PostScript outlines font.

        :return: True if the font is a PostScript font, False otherwise.
        """
        return self.sfntVersion == SFNT_POSTSCRIPT

    @property
    def is_truetype(self):
        """
        Check if the font has TrueType outlines.

        :return: True if the font is a TrueType font, False otherwise.
        """
        return self.sfntVersion == SFNT_TRUETYPE

    @property
    def is_woff(self):
        """
        Check if the font is a WOFF font.

        :return: True if the font is a WOFF font, False otherwise.
        """
        return self.flavor == FLAVOR_WOFF

    @property
    def is_woff2(self):
        """
        Check if the font is a WOFF2 font.

        :return: True if the font is a WOFF2 font, False otherwise.
        """
        return self.flavor == FLAVOR_WOFF2

    def is_sfnt(self):
        """
        Check if the font is a SFNT font.

        :return: True if the font is a SFNT font, False otherwise.
        """
        return self.flavor is None

    @property
    def is_static(self):
        """
        Check if the font is a static font.

        :return: True if the font is a static font, False otherwise.
        """
        return self.get(FVAR_TABLE) is None

    @property
    def is_variable(self):
        """
        Check if the font is a variable font.

        :return: True if the font is a variable font, False otherwise.
        """
        return self.get(FVAR_TABLE) is not None
