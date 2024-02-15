from fontTools.misc.textTools import num2binary
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
    OS_2_TABLE_TAG,
)
from foundrytools_cli_2.lib.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.misc import is_nth_bit_set, set_nth_bit, unset_nth_bit


class InvalidOS2VersionError(Exception):
    """
    Exception raised when trying to access a field that is not defined in the current OS/2 table
    version.
    """


class InvalidEmbedLevelError(Exception):
    """
    Exception raised when trying to set an invalid value for the embed_level field.
    """


class OS2Table(DefaultTbl):  # pylint: disable=too-many-public-methods
    """
    This class extends the fontTools `OS/2` table to add some useful methods.
    """

    def __init__(self, font: TTFont):
        """
        Initializes the OS/2 table handler.
        """
        super().__init__(font=font, table_tag=OS_2_TABLE_TAG)

    @property
    def avg_char_width(self) -> int:
        """
        Returns the xAvgCharWidth value of the OS/2 table of the given font.
        """
        return self.table.xAvgCharWidth

    @avg_char_width.setter
    def avg_char_width(self, value: int) -> None:
        """
        Sets the xAvgCharWidth value of the OS/2 table of the given font.
        """
        self.table.xAvgCharWidth = value

    def recalc_avg_char_width(self) -> None:
        """
        Recalculates the xAvgCharWidth value of the OS/2 table of the given font.
        """
        self.table.recalcAvgCharWidth(ttFont=self.font)

    @property
    def weight_class(self) -> int:
        """
        Returns the usWeightClass value of the OS/2 table of the given font.
        """
        return self.table.usWeightClass

    @weight_class.setter
    def weight_class(self, value: int) -> None:
        """
        Sets the usWeightClass value of the OS/2 table of the given font.
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
        Returns the usWidthClass value of the OS/2 table of the given font.
        """
        return self.table.usWidthClass

    @width_class.setter
    def width_class(self, value: int) -> None:
        """
        Sets the usWidthClass value of the OS/2 table of the given font.
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
        Returns the fsType value of the OS/2 table of the given font.
        """
        return int(num2binary(self.table.fsType, 16)[9:17], 2)

    @embed_level.setter
    def embed_level(self, value: int) -> None:
        """
        Sets the fsType value of the OS/2 table of the given font.
        """
        bit_operands = {
            0: ([0, 1, 2, 3], None),
            2: ([0, 2, 3], 1),
            4: ([0, 1, 3], 2),
            8: ([0, 1, 2], 3),
        }

        if value not in bit_operands:
            raise InvalidEmbedLevelError("Invalid value: embed_level must be 0, 2, 4 or 8.")

        bits_to_unset, bit_to_set = bit_operands[value]

        for b in bits_to_unset:
            self.table.fsType = unset_nth_bit(self.table.fsType, b)

        if bit_to_set is not None:
            self.table.fsType = set_nth_bit(self.table.fsType, bit_to_set)

    @property
    def no_subsetting(self) -> bool:
        """
        Returns the no_subsetting bit of the fsType field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsType, 8)

    @no_subsetting.setter
    def no_subsetting(self, value: bool) -> None:
        """
        Sets the no_subsetting bit of the fsType field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsType = set_nth_bit(self.table.fsType, 8)
        else:
            self.table.fsType = unset_nth_bit(self.table.fsType, 8)

    @property
    def bitmap_embed_only(self) -> bool:
        """
        Returns the bitmap_embed_only bit of the fsType field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsType, 9)

    @bitmap_embed_only.setter
    def bitmap_embed_only(self, value: bool) -> None:
        """
        Sets the bitmap_embed_only bit of the fsType field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsType = set_nth_bit(self.table.fsType, 9)
        else:
            self.table.fsType = unset_nth_bit(self.table.fsType, 9)

    @property
    def is_italic(self) -> bool:
        """
        Returns the italic bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 0)

    @is_italic.setter
    def is_italic(self, value: bool) -> None:
        """
        Sets the italic bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 0)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 0)

    @property
    def is_underscore(self) -> bool:
        """
        Returns the underscore bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 1)

    @is_underscore.setter
    def is_underscore(self, value: bool) -> None:
        """
        Sets the underscore bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 1)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 1)

    @property
    def is_negative(self) -> bool:
        """
        Returns the negative bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 2)

    @is_negative.setter
    def is_negative(self, value: bool) -> None:
        """
        Sets the negative bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 2)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 2)

    @property
    def is_outlined(self) -> bool:
        """
        Returns the outlined bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 3)

    @is_outlined.setter
    def is_outlined(self, value: bool) -> None:
        """
        Sets the outlined bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 3)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 3)

    @property
    def is_strikeout(self) -> bool:
        """
        Returns the strikeout bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 4)

    @is_strikeout.setter
    def is_strikeout(self, value: bool) -> None:
        """
        Sets the strikeout bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 4)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 4)

    @property
    def is_bold(self) -> bool:
        """
        Returns the bold bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 5)

    @is_bold.setter
    def is_bold(self, value: bool) -> None:
        """
        Sets the bold bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 5)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 5)

    @property
    def is_regular(self) -> bool:
        """
        Returns the regular bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 6)

    @is_regular.setter
    def is_regular(self, value: bool) -> None:
        """
        Sets the regular bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 6)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 6)

    @property
    def use_typo_metrics(self) -> bool:
        """
        Returns the useTypoMetrics bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 7)

    @use_typo_metrics.setter
    def use_typo_metrics(self, value: bool) -> None:
        """
        Sets the useTypoMetrics bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 7)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 7)

    @property
    def wws(self) -> bool:
        """
        Returns the wws bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 8)

    @wws.setter
    def wws(self, value: bool) -> None:
        """
        Sets the wws bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 8)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 8)

    @property
    def is_oblique(self) -> bool:
        """
        Returns the oblique bit of the fsSelection field of the OS/2 table of the given font.
        """
        return is_nth_bit_set(self.table.fsSelection, 9)

    @is_oblique.setter
    def is_oblique(self, value: bool) -> None:
        """
        Sets the oblique bit of the fsSelection field of the OS/2 table of the given font.
        """
        if value:
            self.table.fsSelection = set_nth_bit(self.table.fsSelection, 9)
        else:
            self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 9)

    @property
    def x_height(self) -> float:
        """
        Returns the sxHeight value of the OS/2 table of the given font.
        """
        return self.table.sxHeight

    @x_height.setter
    def x_height(self, value: float) -> None:
        """
        Sets the sxHeight value of the OS/2 table of the given font.
        """
        self.table.sxHeight = value

    @property
    def cap_height(self) -> float:
        """
        Returns the sCapHeight value of the OS/2 table of the given font.
        """
        return self.table.sCapHeight

    @cap_height.setter
    def cap_height(self, value: float) -> None:
        """
        Sets the sCapHeight value of the OS/2 table of the given font.
        """
        self.table.sCapHeight = value

    @property
    def typo_ascender(self) -> int:
        """
        Sets the usTypoAscent value of the OS/2 table of the given font.
        """
        return self.table.sTypoAscender

    @typo_ascender.setter
    def typo_ascender(self, value: int) -> None:
        """
        Sets the usTypoAscent value of the OS/2 table of the given font.
        """
        self.table.sTypoAscender = value

    @property
    def typo_descender(self) -> int:
        """
        Sets the usTypoDescent value of the OS/2 table of the given font.
        """
        return self.table.sTypoDescender

    @typo_descender.setter
    def typo_descender(self, value: int) -> None:
        """
        Sets the usTypoDescent value of the OS/2 table of the given font.
        """
        self.table.sTypoDescender = value

    @property
    def typo_line_gap(self) -> int:
        """
        Sets the usTypoLineGap value of the OS/2 table of the given font.
        """
        return self.table.sTypoLineGap

    @typo_line_gap.setter
    def typo_line_gap(self, value: int) -> None:
        """
        Sets the usTypoLineGap value of the OS/2 table of the given font.
        """
        self.table.sTypoLineGap = value

    @property
    def win_ascent(self) -> int:
        """
        Sets the usWinAscent value of the OS/2 table of the given font.
        """
        return self.table.usWinAscent

    @win_ascent.setter
    def win_ascent(self, value: int) -> None:
        """
        Sets the usWinAscent value of the OS/2 table of the given font.
        """
        self.table.usWinAscent = value

    @property
    def win_descent(self) -> int:
        """
        Sets the usWinDescent value of the OS/2 table of the given font.
        """
        return self.table.usWinDescent

    @win_descent.setter
    def win_descent(self, value: int) -> None:
        """
        Sets the usWinDescent value of the OS/2 table of the given font.
        """
        self.table.usWinDescent = value