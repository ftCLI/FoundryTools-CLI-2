from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import HEAD_TABLE_TAG
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl
from foundrytools_cli_2.lib.utils.bits_tools import is_nth_bit_set

BOLD_BIT = 0
ITALIC_BIT = 1


class HeadTable(DefaultTbl):
    """
    This class extends the fontTools ``head`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``head`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=HEAD_TABLE_TAG)

    @property
    def is_bold(self) -> bool:
        """
        Check if the bold bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, BOLD_BIT)

    @is_bold.setter
    def is_bold(self, value: bool) -> None:
        """
        Set or unset the bold bit in the macStyle field of the 'head' table
        """
        self.set_bit(field_name="macStyle", pos=BOLD_BIT, value=value)

    @property
    def is_italic(self) -> bool:
        """
        Check if the italic bit is set in the macStyle field of the 'head' table
        """
        return is_nth_bit_set(self.table.macStyle, ITALIC_BIT)

    @is_italic.setter
    def is_italic(self, value: bool) -> None:
        """
        Set or unset the italic bit in the macStyle field of the 'head' table
        """
        self.set_bit(field_name="macStyle", pos=ITALIC_BIT, value=value)
