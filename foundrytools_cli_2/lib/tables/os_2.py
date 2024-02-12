from fontTools.misc.textTools import num2binary
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import (
    MAX_US_WEIGHT_CLASS,
    MAX_US_WIDTH_CLASS,
    MIN_US_WEIGHT_CLASS,
    MIN_US_WIDTH_CLASS,
    OS_2_TABLE_TAG,
)
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.misc import is_nth_bit_set, set_nth_bit, unset_nth_bit


class OS2Table(DefaultTbl):  # pylint: disable=too-many-public-methods
    """
    This class extends the fontTools `OS/2` table to add some useful methods.
    """

    def __init__(self, font: TTFont):
        """
        Initializes the OS/2 table handler.
        """
        super().__init__(font=font, table_tag=OS_2_TABLE_TAG)

    def get_avg_char_width(self) -> int:
        """
        Returns the xAvgCharWidth value of the OS/2 table of the given font.
        """
        return self.table.xAvgCharWidth

    def set_avg_char_width(self, value: int) -> None:
        """
        Sets the xAvgCharWidth value of the OS/2 table of the given font.
        """
        self.table.xAvgCharWidth = value

    def recalc_avg_char_width(self) -> None:
        """
        Recalculates the xAvgCharWidth value of the OS/2 table of the given font.
        """
        self.table.recalcAvgCharWidth(ttFont=self.font)

    def get_embed_level(self) -> int:
        """
        Returns the fsType value of the OS/2 table of the given font.
        """
        return int(num2binary(self.table.fsType, 16)[9:17], 2)

    def set_embed_level(self, value: int) -> None:
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
            raise ValueError("Invalid value: embed_level must be 0, 2, 4 or 8.")

        bits_to_unset, bit_to_set = bit_operands[value]

        for b in bits_to_unset:
            self.table.fsType = unset_nth_bit(self.table.fsType, b)

        if bit_to_set is not None:
            self.table.fsType = set_nth_bit(self.table.fsType, bit_to_set)

    def is_no_subsetting_bit_set(self) -> bool:
        """
        Check if the no_subsetting bit is set in the fsType field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsType, 8)

    def set_no_subsetting_bit(self) -> None:
        """
        Set the no_subsetting bit in the fsType field of the OS/2 table.
        """
        self.table.fsType = set_nth_bit(self.table.fsType, 8)

    def clear_no_subsetting_bit(self) -> None:
        """
        Clear the no_subsetting bit in the fsType field of the OS/2 table.
        """
        self.table.fsType = unset_nth_bit(self.table.fsType, 8)

    def is_bitmap_embed_only_bit_set(self) -> bool:
        """
        Check if the bitmap_embed_only bit is set in the fsType field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsType, 9)

    def set_bitmap_embed_only_bit(self) -> None:
        """
        Set the bitmap_embed_only bit in the fsType field of the OS/2 table.
        """
        self.table.fsType = set_nth_bit(self.table.fsType, 9)

    def clear_bitmap_embed_only_bit(self) -> None:
        """
        Clear the bitmap_embed_only bit in the fsType field of the OS/2 table.
        """
        self.table.fsType = unset_nth_bit(self.table.fsType, 9)

    def get_weight_class(self) -> int:
        """
        Returns the usWeightClass value of the OS/2 table of the given font.
        """
        return self.table.usWeightClass

    def set_weight_class(self, value: int) -> None:
        """
        Sets the usWeightClass value of the OS/2 table of the given font.
        """
        if not self.validate_value(
                value, MIN_US_WEIGHT_CLASS, MAX_US_WEIGHT_CLASS, "usWeightClass"
        ):
            return
        self.table.usWeightClass = value

    def get_width_class(self) -> int:
        """
        Returns the usWidthClass value of the OS/2 table of the given font.
        """
        return self.table.usWidthClass

    def set_width_class(self, value: int) -> None:
        """
        Sets the usWidthClass value of the OS/2 table of the given font.
        """
        if not self.validate_value(value, MIN_US_WIDTH_CLASS, MAX_US_WIDTH_CLASS, "usWidthClass"):
            return
        self.table.usWidthClass = value

    def is_italic_bit_set(self) -> bool:
        """
        Check if the italic bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 0)

    def set_italic_bit(self) -> None:
        """
        Set the italic bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 0)

    def clear_italic_bit(self) -> None:
        """
        Clear the italic bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 0)

    def is_underscore_bit_set(self) -> bool:
        """
        Check if the underscore bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 1)

    def set_underscore_bit(self) -> None:
        """
        Set the underscore bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 1)

    def clear_underscore_bit(self) -> None:
        """
        Clear the underscore bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 1)

    def is_negative_bit_set(self) -> bool:
        """
        Check if the negative bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 2)

    def set_negative_bit(self) -> None:
        """
        Set the negative bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 2)

    def clear_negative_bit(self) -> None:
        """
        Clear the negative bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 2)

    def is_outlined_bit_set(self) -> bool:
        """
        Check if the outlined bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 3)

    def set_outlined_bit(self) -> None:
        """
        Set the outlined bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 3)

    def clear_outlined_bit(self) -> None:
        """
        Clear the outlined bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 3)

    def is_strikeout_bit_set(self) -> bool:
        """
        Check if the strikeout bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 4)

    def set_strikeout_bit(self) -> None:
        """
        Set the strikeout bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 4)

    def clear_strikeout_bit(self) -> None:
        """
        Clear the strikeout bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 4)

    def is_bold_bit_set(self) -> bool:
        """
        Check if the bold bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 5)

    def set_bold_bit(self) -> None:
        """
        Set the bold bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 5)

    def clear_bold_bit(self) -> None:
        """
        Clear the bold bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 5)

    def is_regular_bit_set(self) -> bool:
        """
        Check if the regular bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 6)

    def set_regular_bit(self) -> None:
        """
        Set the regular bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 6)

    def clear_regular_bit(self) -> None:
        """
        Clear the regular bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 6)

    def is_use_typo_metrics_bit_set(self) -> bool:
        """
        Check if the useTypoMetrics bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 7)

    def set_use_typo_metrics_bit(self) -> None:
        """
        Set the useTypoMetrics bit in the fsSelection field of the OS/2 table.
        """
        if self.table.version < 4:
            logger.warning(
                "fsSelection bit 7 (USE_TYPO_METRICS) is only defined in OS/2 version 4 and up."
            )
            return
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 7)

    def clear_use_typo_metrics_bit(self) -> None:
        """
        Clear the useTypoMetrics bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 7)

    def is_wws_bit_set(self) -> bool:
        """
        Check if the wws bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 8)

    def set_wws_bit(self) -> None:
        """
        Set the wws bit in the fsSelection field of the OS/2 table.
        """
        if self.table.version < 4:
            logger.warning(
                "fsSelection bit 8 (WWS) is only defined in OS/2 version 4 and up."
            )
            return
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 8)

    def clear_wws_bit(self) -> None:
        """
        Clear the wws bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 8)

    def is_oblique_bit_set(self) -> bool:
        """
        Check if the oblique bit is set in the fsSelection field of the OS/2 table.
        """
        return is_nth_bit_set(self.table.fsSelection, 9)

    def set_oblique_bit(self) -> None:
        """
        Set the oblique bit in the fsSelection field of the OS/2 table.
        """
        if self.table.version < 4:
            logger.warning(
                "fsSelection bit 9 (OBLIQUE) is only defined in OS/2 version 4 and up."
            )
            return
        self.table.fsSelection = set_nth_bit(self.table.fsSelection, 9)

    def clear_oblique_bit(self) -> None:
        """
        Clear the oblique bit in the fsSelection field of the OS/2 table.
        """
        self.table.fsSelection = unset_nth_bit(self.table.fsSelection, 9)

    def get_x_height(self) -> float:
        """
        Returns the sxHeight value of the OS/2 table of the given font.
        """
        return self.table.sxHeight

    def set_x_height(self, value: float) -> None:
        """
        Sets the sxHeight value of the OS/2 table of the given font.
        """
        self.table.sxHeight = value

    def get_cap_height(self) -> float:
        """
        Returns the sCapHeight value of the OS/2 table of the given font.
        """
        return self.table.sCapHeight

    def set_cap_height(self, value: float) -> None:
        """
        Sets the sCapHeight value of the OS/2 table of the given font.
        """
        self.table.sCapHeight = value

    @staticmethod
    def validate_value(value: int, min_value: int, max_value: int, attribute: str) -> bool:
        """
        Validates values to be set
        """
        if value < min_value or value > max_value:
            logger.warning(
                f"Invalid value for {attribute}: {value}. "
                f"Expected a value between {min_value} and {max_value}."
            )
            return False
        return True
