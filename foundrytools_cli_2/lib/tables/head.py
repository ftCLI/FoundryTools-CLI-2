from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.misc import is_nth_bit_set, set_nth_bit, unset_nth_bit


class HeadTable(DefaultTbl):
    """
    This class extends the fontTools `head` table to add some useful methods.
    """
    def __init__(self, font: TTFont) -> None:
        """
        Initializes the head table handler.
        """
        super().__init__(font=font, table_tag="head")

    def is_bold_bit_set(self) -> bool:
        """
        Check if the bold bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, 0)

    def set_bold_bit(self) -> None:
        """
        Set the bold bit in the macStyle field of the 'head' table
        """
        self.table.macStyle = set_nth_bit(self.table.macStyle, 0)

    def unset_bold_bit(self) -> None:
        """
        Clear the bold bit in the macStyle field of the 'head' table
        """
        self.table.macStyle = unset_nth_bit(self.table.macStyle, 0)

    def is_italic_bit_set(self) -> bool:
        """
        Check if the italic bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, 1)

    def set_italic_bit(self) -> None:
        """
        Set the italic bit in the macStyle field of the 'head' table
        """
        self.table.macStyle = set_nth_bit(self.table.macStyle, 1)

    def unset_italic_bit(self) -> None:
        """
        Clear the italic bit in the macStyle field of the 'head' table
        """
        self.table.macStyle = unset_nth_bit(self.table.macStyle, 1)
