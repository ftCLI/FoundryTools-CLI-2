import typing as t

from fontTools.misc.roundTools import otRound
from fontTools.misc.textTools import num2binary
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
    OS_2_TABLE_TAG,
)
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.bits_tools import is_nth_bit_set


class InvalidOS2VersionError(Exception):
    """
    Exception raised when trying to access a field that is not defined in the current OS/2 table
    version.
    """


class OS2Table(DefaultTbl):  # pylint: disable=too-many-public-methods
    """
    This class extends the fontTools `OS/2` table to add some useful methods and properties.
    """

    def __init__(self, font: TTFont):
        """
        Initializes the OS/2 table handler.
        """
        super().__init__(font=font, table_tag=OS_2_TABLE_TAG)

    @property
    def avg_char_width(self) -> int:
        """
        Returns the ``OS/2.xAvgCharWidth`` value.
        """
        return self.table.xAvgCharWidth

    @avg_char_width.setter
    def avg_char_width(self, value: int) -> None:
        """
        Sets the ``OS/2.xAvgCharWidth`` value.
        """
        self.table.xAvgCharWidth = value

    @property
    def weight_class(self) -> int:
        """
        Returns the ``OS/2.usWeightClass`` value.
        """
        return self.table.usWeightClass

    @weight_class.setter
    def weight_class(self, value: int) -> None:
        """
        Sets the ``OS/2.usWeightClass`` value.
        """
        if value < MIN_US_WEIGHT_CLASS or value > MAX_US_WEIGHT_CLASS:
            raise ValueError(
                f"Invalid value for usWeightClass: {value}. "
                f"Expected a value between {MIN_US_WEIGHT_CLASS} and {MAX_US_WEIGHT_CLASS}."
            )
        self.table.usWeightClass = value

    @property
    def width_class(self) -> int:
        """
        Returns the ``OS/2.usWidthClass`` value.
        """
        return self.table.usWidthClass

    @width_class.setter
    def width_class(self, value: int) -> None:
        """
        Sets the ``OS/2.usWidthClass`` value.
        """
        if value < MIN_US_WIDTH_CLASS or value > MAX_US_WIDTH_CLASS:
            raise ValueError(
                f"Invalid value for usWidthClass: {value}. "
                f"Expected a value between {MIN_US_WIDTH_CLASS} and {MAX_US_WIDTH_CLASS}."
            )
        self.table.usWidthClass = value

    @property
    def embed_level(self) -> int:
        """
        Returns the embedding level od the ``OS/2.fsType`` field. The value can be 0, 2, 4 or 8.

        0: Installable Embedding
        2: Restricted License Embedding
        4: Preview & Print Embedding
        8: Editable Embedding
        """
        return int(num2binary(self.table.fsType, 16)[9:17], 2)

    @embed_level.setter
    def embed_level(self, value: int) -> None:
        """
        Sets the embedding level of the ``OS/2.fsType`` field. The value can be 0, 2, 4 or 8.

        0: Installable Embedding
        2: Restricted License Embedding
        4: Preview & Print Embedding
        8: Editable Embedding
        """
        bit_operands = {
            0: ([0, 1, 2, 3], None),
            2: ([0, 2, 3], 1),
            4: ([0, 1, 3], 2),
            8: ([0, 1, 2], 3),
        }

        if value not in bit_operands:
            raise ValueError("Invalid value: embed_level must be 0, 2, 4 or 8.")

        bits_to_unset, bit_to_set = bit_operands[value]

        for b in bits_to_unset:
            self.set_bit(field_name="fsType", pos=b, value=False)

        if bit_to_set is not None:
            self.set_bit(field_name="fsType", pos=bit_to_set, value=True)

    @property
    def no_subsetting(self) -> bool:
        """
        Returns True if the bit 8 (NO_SUBSETTING) of the ``OS/2.fsType`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsType, 8)

    @no_subsetting.setter
    def no_subsetting(self, value: bool) -> None:
        """
        Sets the bit 8 (NO_SUBSETTING) of the ``OS/2.fsType`` field.
        """
        self.set_bit(field_name="fsType", pos=8, value=value)

    @property
    def bitmap_embed_only(self) -> bool:
        """
        Returns True if the bit 9 (BITMAP_EMBED_ONLY) of the ``OS/2.fsType`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsType, 9)

    @bitmap_embed_only.setter
    def bitmap_embed_only(self, value: bool) -> None:
        """
        Sets the bit 9 (BITMAP_EMBED_ONLY) of the ``OS/2.fsType`` field.
        """
        self.set_bit(field_name="fsType", pos=9, value=value)

    @property
    def is_italic(self) -> bool:
        """
        Returns True if the bit 0 (ITALIC) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 0)

    @is_italic.setter
    def is_italic(self, value: bool) -> None:
        """
        Sets the bit 0 (ITALIC) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=0, value=value)

    @property
    def is_underscore(self) -> bool:
        """
        Returns True if the bit 1 (UNDERSCORE) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 1)

    @is_underscore.setter
    def is_underscore(self, value: bool) -> None:
        """
        Sets the bit 1 (UNDERSCORE) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=1, value=value)

    @property
    def is_negative(self) -> bool:
        """
        Returns True if the bit 2 (NEGATIVE) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 2)

    @is_negative.setter
    def is_negative(self, value: bool) -> None:
        """
        Sets the bit 2 (NEGATIVE) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=2, value=value)

    @property
    def is_outlined(self) -> bool:
        """
        Returns True if the bit 3 (OUTLINED) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 3)

    @is_outlined.setter
    def is_outlined(self, value: bool) -> None:
        """
        Sets the bit 3 (OUTLINED) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=3, value=value)

    @property
    def is_strikeout(self) -> bool:
        """
        Returns True if the bit 4 (STRIKEOUT) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 4)

    @is_strikeout.setter
    def is_strikeout(self, value: bool) -> None:
        """
        Sets the bit 4 (STRIKEOUT) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=4, value=value)

    @property
    def is_bold(self) -> bool:
        """
        Returns True if the bit 5 (BOLD) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 5)

    @is_bold.setter
    def is_bold(self, value: bool) -> None:
        """
        Sets the bit 5 (BOLD) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=5, value=value)

    @property
    def is_regular(self) -> bool:
        """
        Returns True if the bit 6 (REGULAR) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 6)

    @is_regular.setter
    def is_regular(self, value: bool) -> None:
        """
        Sets the bit 6 (REGULAR) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=6, value=value)

    @property
    def use_typo_metrics(self) -> bool:
        """
        Returns True if the bit 7 (USE_TYPO_METRICS) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 7)

    @use_typo_metrics.setter
    def use_typo_metrics(self, value: bool) -> None:
        """
        Sets the bit 7 (USE_TYPO_METRICS) of the ``OS/2.fsSelection`` field.
        """
        if self.table.version < 4:
            raise InvalidOS2VersionError(
                "fsSelection bit 7 (USE_TYPO_METRICS) is only defined in OS/2 table versions 4 and "
                "up."
            )
        self.set_bit(field_name="fsSelection", pos=7, value=value)

    @property
    def wws_consistent(self) -> bool:
        """
        Returns True if the bit 8 (WWS) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsSelection, 8)

    @wws_consistent.setter
    def wws_consistent(self, value: bool) -> None:
        """
        Sets the bit 8 (WWS) of the ``OS/2.fsSelection`` field.
        """
        if self.table.version < 4:
            raise InvalidOS2VersionError(
                "fsSelection bit 8 (WWS) is only defined in OS/2 table versions 4 and up."
            )
        self.set_bit(field_name="fsSelection", pos=8, value=value)

    @property
    def is_oblique(self) -> bool:
        """
        Returns True if the bit 9 (OBLIQUE) of the ``OS/2.fsSelection`` field is set, False
        """
        if self.table.version < 4:
            raise InvalidOS2VersionError(
                "fsSelection bit 9 (OBLIQUE) is only defined in OS/2 table versions 4 and up."
            )
        return is_nth_bit_set(self.table.fsSelection, 9)

    @is_oblique.setter
    def is_oblique(self, value: bool) -> None:
        """
        Sets the bit 9 (OBLIQUE) of the ``OS/2.fsSelection`` field.
        """
        self.set_bit(field_name="fsSelection", pos=9, value=value)

    @property
    def x_height(self) -> t.Optional[int]:
        """
        Returns the sxHeight value of the ``OS/2`` table.
        """
        if self.table.version < 2:
            return None
        return otRound(self.table.sxHeight)

    @x_height.setter
    def x_height(self, value: int) -> None:
        """
        Sets the sxHeight value of the ``OS/2`` table.
        """
        if self.table.version < 2:
            raise InvalidOS2VersionError(
                "sxHeight is only defined in OS/2 table versions 2 and up."
            )
        self.table.sxHeight = value

    @property
    def cap_height(self) -> t.Optional[int]:
        """
        Returns the sCapHeight value of the ``OS/2`` table.
        """
        if self.table.version < 2:
            return None
        return otRound(self.table.sCapHeight)

    @cap_height.setter
    def cap_height(self, value: int) -> None:
        """
        Sets the sCapHeight value of the ``OS/2`` table.
        """
        if self.table.version < 2:
            raise InvalidOS2VersionError(
                "sCapHeight is only defined in OS/2 table versions 2 and up."
            )
        self.table.sCapHeight = value

    @property
    def typo_ascender(self) -> int:
        """
        Returns the sTypoAscender value of the ``OS/2`` table.
        """
        return self.table.sTypoAscender

    @typo_ascender.setter
    def typo_ascender(self, value: int) -> None:
        """
        Sets the sTypoAscender value of the ``OS/2`` table.
        """
        self.table.sTypoAscender = value

    @property
    def typo_descender(self) -> int:
        """
        Returns the sTypoDescender value of the ``OS/2`` table.
        """
        return self.table.sTypoDescender

    @typo_descender.setter
    def typo_descender(self, value: int) -> None:
        """
        Sets the sTypoDescender value of the ``OS/2`` table.
        """
        self.table.sTypoDescender = value

    @property
    def typo_line_gap(self) -> int:
        """
        Returns the sTypoLineGap value of the ``OS/2`` table.
        """
        return self.table.sTypoLineGap

    @typo_line_gap.setter
    def typo_line_gap(self, value: int) -> None:
        """
        Sets the sTypoLineGap value of the ``OS/2`` table.
        """
        self.table.sTypoLineGap = value

    @property
    def win_ascent(self) -> int:
        """
        Returns the usWinAscent value of the ``OS/2`` table.
        """
        return self.table.usWinAscent

    @win_ascent.setter
    def win_ascent(self, value: int) -> None:
        """
        Sets the usWinAscent value of the ``OS/2`` table.
        """
        self.table.usWinAscent = value

    @property
    def win_descent(self) -> int:
        """
        Returns the usWinDescent value of the ``OS/2`` table.
        """
        return self.table.usWinDescent

    @win_descent.setter
    def win_descent(self, value: int) -> None:
        """
        Sets the usWinDescent value of the ``OS/2`` table.
        """
        self.table.usWinDescent = value

    def recalc_avg_char_width(self) -> int:
        """
        Recalculates the xAvgCharWidth value of the ``OS/2`` table.
        """
        return self.table.recalcAvgCharWidth(ttFont=self.font)
