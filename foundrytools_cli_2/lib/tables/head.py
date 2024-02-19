from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.bits_tools import is_nth_bit_set


class HeadTable(DefaultTbl):
    """
    This class extends the fontTools `head` table to add some useful methods.
    """

    def __init__(self, font: TTFont) -> None:
        """
        Initializes the head table handler.
        """
        super().__init__(font=font, table_tag="head")

    @property
    def is_bold(self) -> bool:
        """
        Check if the bold bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, 0)

    @is_bold.setter
    def is_bold(self, value: bool) -> None:
        """
        Set or unset the bold bit in the macStyle field of the 'head' table
        """
        self.set_bit(field_name="macStyle", pos=0, value=value)

    @property
    def is_italic(self) -> bool:
        """
        Check if the italic bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, 1)

    @is_italic.setter
    def is_italic(self, value: bool) -> None:
        """
        Set or unset the italic bit in the macStyle field of the 'head' table
        """
        self.set_bit(field_name="macStyle", pos=1, value=value)
