import typing as t

from fontTools.misc.roundTools import otRound
from fontTools.misc.textTools import num2binary
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
    T_OS_2,
)
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.bits_tools import is_nth_bit_set
from foundrytools_cli_2.lib.utils.misc import get_glyph_bounds
from foundrytools_cli_2.lib.utils.string_tools import adjust_string_length

ITALIC_BIT = 0
UNDERSCORE_BIT = 1
NEGATIVE_BIT = 2
OUTLINED_BIT = 3
STRIKEOUT_BIT = 4
BOLD_BIT = 5
REGULAR_BIT = 6
USE_TYPO_METRICS_BIT = 7
WWWS_BIT = 8
OBLIQUE_BIT = 9
NO_SUBSETTING_BIT = 8
BITMAP_EMBED_ONLY_BIT = 9


class FsSelection:
    """
    A wrapper class for the ``fsSelection`` field of the ``OS/2`` table.
    """

    def __init__(self, os_2_table: "OS2Table"):
        self.os_2_table = os_2_table

    def __repr__(self) -> str:
        return f"fsSelection({num2binary(self.os_2_table.table.fsSelection)})"

    @property
    def italic(self) -> bool:
        """
        Returns True if the bit 0 (ITALIC) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, ITALIC_BIT)

    @italic.setter
    def italic(self, value: bool) -> None:
        """
        Sets the bit 0 (ITALIC) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=ITALIC_BIT, value=value)

    @property
    def underscore(self) -> bool:
        """
        Returns True if the bit 1 (UNDERSCORE) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, UNDERSCORE_BIT)

    @underscore.setter
    def underscore(self, value: bool) -> None:
        """
        Sets the bit 1 (UNDERSCORE) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=UNDERSCORE_BIT, value=value)

    @property
    def negative(self) -> bool:
        """
        Returns True if the bit 2 (NEGATIVE) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, NEGATIVE_BIT)

    @negative.setter
    def negative(self, value: bool) -> None:
        """
        Sets the bit 2 (NEGATIVE) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=NEGATIVE_BIT, value=value)

    @property
    def outlined(self) -> bool:
        """
        Returns True if the bit 3 (OUTLINED) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, OUTLINED_BIT)

    @outlined.setter
    def outlined(self, value: bool) -> None:
        """
        Sets the bit 3 (OUTLINED) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=OUTLINED_BIT, value=value)

    @property
    def strikeout(self) -> bool:
        """
        Returns True if the bit 4 (STRIKEOUT) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, STRIKEOUT_BIT)

    @strikeout.setter
    def strikeout(self, value: bool) -> None:
        """
        Sets the bit 4 (STRIKEOUT) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=STRIKEOUT_BIT, value=value)

    @property
    def bold(self) -> bool:
        """
        Returns True if the bit 5 (BOLD) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, BOLD_BIT)

    @bold.setter
    def bold(self, value: bool) -> None:
        """
        Sets the bit 5 (BOLD) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=BOLD_BIT, value=value)

    @property
    def regular(self) -> bool:
        """
        Returns True if the bit 6 (REGULAR) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, REGULAR_BIT)

    @regular.setter
    def regular(self, value: bool) -> None:
        """
        Sets the bit 6 (REGULAR) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=REGULAR_BIT, value=value)

    @property
    def use_typo_metrics(self) -> bool:
        """
        Returns True if the bit 7 (USE_TYPO_METRICS) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, USE_TYPO_METRICS_BIT)

    @use_typo_metrics.setter
    def use_typo_metrics(self, value: bool) -> None:
        """
        Sets the bit 7 (USE_TYPO_METRICS) of the ``OS/2.fsSelection`` field.
        """
        if self.os_2_table.version < 4 and value is True:
            raise self.os_2_table.InvalidOS2VersionError(
                "fsSelection bit 7 (USE_TYPO_METRICS) is only defined in OS/2 table versions 4 and "
                "up."
            )
        self.os_2_table.set_bit(field_name="fsSelection", pos=USE_TYPO_METRICS_BIT, value=value)

    @property
    def wws_consistent(self) -> bool:
        """
        Returns True if the bit 8 (WWWS) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.os_2_table.table.fsSelection, WWWS_BIT)

    @wws_consistent.setter
    def wws_consistent(self, value: bool) -> None:
        """
        Sets the bit 8 (WWWS) of the ``OS/2.fsSelection`` field.
        """
        if self.os_2_table.version < 4 and value is True:
            raise self.os_2_table.InvalidOS2VersionError(
                "fsSelection bit 8 (WWWS) is only defined in OS/2 table versions 4 and up."
            )
        self.os_2_table.set_bit(field_name="fsSelection", pos=WWWS_BIT, value=value)

    @property
    def oblique(self) -> bool:
        """
        Returns True if the bit 9 (OBLIQUE) of the ``OS/2.fsSelection`` field is set, False
        otherwise.
        """
        if self.os_2_table.version < 4:
            raise self.os_2_table.InvalidOS2VersionError(
                "fsSelection bit 9 (OBLIQUE) is only defined in OS/2 table versions 4 and up."
            )
        return is_nth_bit_set(self.os_2_table.table.fsSelection, OBLIQUE_BIT)

    @oblique.setter
    def oblique(self, value: bool) -> None:
        """
        Sets the bit 9 (OBLIQUE) of the ``OS/2.fsSelection`` field.
        """
        self.os_2_table.set_bit(field_name="fsSelection", pos=OBLIQUE_BIT, value=value)


class OS2Table(DefaultTbl):  # pylint: disable=too-many-public-methods
    """
    This class extends the fontTools ``OS/2`` table to add some useful methods and properties.
    """

    def __init__(self, ttfont: TTFont):
        """
        Initializes the ``OS/2`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_OS_2)
        self.fs_selection = FsSelection(os_2_table=self)

    class InvalidOS2VersionError(Exception):
        """
        Exception raised when trying to access a field that is not defined in the current OS/2 table
        version.
        """

    @property
    def version(self) -> int:
        """
        Returns the ``OS/2.version`` value.
        """
        return self.table.version

    @version.setter
    def version(self, value: int) -> None:
        """
        Sets the ``OS/2.version`` value.
        """
        self.table.version = value

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
        return is_nth_bit_set(self.table.fsType, NO_SUBSETTING_BIT)

    @no_subsetting.setter
    def no_subsetting(self, value: bool) -> None:
        """
        Sets the bit 8 (NO_SUBSETTING) of the ``OS/2.fsType`` field.
        """
        self.set_bit(field_name="fsType", pos=NO_SUBSETTING_BIT, value=value)

    @property
    def bitmap_embed_only(self) -> bool:
        """
        Returns True if the bit 9 (BITMAP_EMBED_ONLY) of the ``OS/2.fsType`` field is set, False
        otherwise.
        """
        return is_nth_bit_set(self.table.fsType, BITMAP_EMBED_ONLY_BIT)

    @bitmap_embed_only.setter
    def bitmap_embed_only(self, value: bool) -> None:
        """
        Sets the bit 9 (BITMAP_EMBED_ONLY) of the ``OS/2.fsType`` field.
        """
        self.set_bit(field_name="fsType", pos=BITMAP_EMBED_ONLY_BIT, value=value)

    @property
    def vendor_id(self) -> str:
        """
        Returns the ``OS/2.achVendID`` value.
        """
        return self.table.achVendID

    @vendor_id.setter
    def vendor_id(self, value: str) -> None:
        """
        Sets the ``OS/2.achVendID`` value.
        """
        self.table.achVendID = adjust_string_length(value, length=4, pad_char=" ")

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

    @property
    def x_height(self) -> t.Optional[int]:
        """
        Returns the sxHeight value of the ``OS/2`` table.
        """
        if self.version < 2:
            return None
        return self.table.sxHeight

    @x_height.setter
    def x_height(self, value: int) -> None:
        """
        Sets the sxHeight value of the ``OS/2`` table.
        """
        if self.version < 2:
            raise self.InvalidOS2VersionError(
                "sxHeight is only defined in OS/2 table versions 2 and up."
            )
        self.table.sxHeight = value

    @property
    def cap_height(self) -> t.Optional[int]:
        """
        Returns the sCapHeight value of the ``OS/2`` table.
        """
        if self.version < 2:
            return None
        return self.table.sCapHeight

    @cap_height.setter
    def cap_height(self, value: int) -> None:
        """
        Sets the sCapHeight value of the ``OS/2`` table.
        """
        if self.version < 2:
            raise self.InvalidOS2VersionError(
                "sCapHeight is only defined in OS/2 table versions 2 and up."
            )
        self.table.sCapHeight = value

    @property
    def max_context(self) -> t.Optional[int]:
        """
        Returns the maximum profile's maxContext value.
        """
        if self.version < 2:
            return None
        return self.table.usMaxContext

    @max_context.setter
    def max_context(self, value: int) -> None:
        """
        Sets the maximum profile's maxContext value.
        """
        if self.version < 2:
            raise self.InvalidOS2VersionError(
                "usMaxContext is only defined in OS/2 table versions 2 and up."
            )
        self.table.usMaxContext = value

    @property
    def unicode_ranges(self) -> t.List[int]:
        """
        Returns the Unicode ranges of the ``OS/2`` table.
        """
        return self.table.getUnicodeRanges()

    @unicode_ranges.setter
    def unicode_ranges(self, bits: t.List[int]) -> None:
        """
        Sets the Unicode ranges of the ``OS/2`` table.
        """
        self.table.setUnicodeRanges(bits)

    @property
    def codepage_ranges(self) -> t.List[int]:
        """
        Returns the code page ranges of the ``OS/2`` table.
        """
        return self.table.getCodePageRanges()

    @codepage_ranges.setter
    def codepage_ranges(self, bits: t.List[int]) -> None:
        """
        Sets the code page ranges of the ``OS/2`` table.
        """
        self.table.setCodePageRanges(bits)

    def recalc_x_height(self, glyph_name: str = "x") -> int:
        """
        Recalculates and sets the ``OS/2.sxHeight`` value.
        """
        if not self.version >= 2:
            raise self.InvalidOS2VersionError(
                "sxHeight is only defined in OS/2 table versions 2 and up."
            )
        try:
            x_height = otRound(get_glyph_bounds(font=self.ttfont, glyph_name=glyph_name)["yMax"])
        except KeyError:
            x_height = 0
        self.x_height = x_height
        return x_height

    def recalc_cap_height(self, glyph_name: str = "H") -> int:
        """
        Recalculates and sets the ``OS/2.sCapHeight`` value.
        """
        if not self.version >= 2:
            raise self.InvalidOS2VersionError(
                "sCapHeight is only defined in OS/2 table versions 2 and up."
            )
        try:
            cap_height = otRound(get_glyph_bounds(font=self.ttfont, glyph_name=glyph_name)["yMax"])
        except KeyError:
            cap_height = 0
        self.cap_height = cap_height
        return cap_height

    def recalc_avg_char_width(self) -> int:
        """
        Recalculates and sets the xAvgCharWidth value of the ``OS/2`` table.
        """
        return self.table.recalcAvgCharWidth(ttFont=self.ttfont)

    def recalc_max_context(self) -> None:
        """
        Recalculates the maxContext value of the ``OS/2`` table.
        """
        self.max_context = maxCtxFont(self.ttfont)

    def recalc_unicode_ranges(self) -> None:
        """
        Recalculates the Unicode ranges of the ``OS/2`` table.
        """
        self.table.recalcUnicodeRanges(self.ttfont)

    def recalc_code_page_ranges(self) -> None:
        """
        Recalculates the code page ranges of the ``OS/2`` table.
        """
        self.table.recalcCodePageRanges(self.ttfont)

    def upgrade(self, target_version: int) -> None:
        """
        Upgrades the ``OS/2`` table to the latest version.
        """
        current_version = self.version
        if target_version <= current_version:
            raise self.InvalidOS2VersionError(
                f"The target version must be greater than the current version ({current_version})."
            )

        self.table.version = target_version

        if current_version < 1:
            self.recalc_code_page_ranges()

        if target_version == 1:
            return

        if current_version < 2:
            self.recalc_x_height()
            self.recalc_cap_height()
            self.table.usDefaultChar = 0
            self.table.usBreakChar = 32
            self.recalc_max_context()

        if target_version == 5:
            self.table.usLowerOpticalPointSize = 0
            self.table.usUpperOpticalPointSize = 65535 / 20

        if target_version < 4:
            self.fs_selection.use_typo_metrics = False
            self.fs_selection.wws_consistent = False
            self.fs_selection.oblique = False
