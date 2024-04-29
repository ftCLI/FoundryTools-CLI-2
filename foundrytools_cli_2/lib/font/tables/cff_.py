from fontTools.cffLib import CharStrings, PrivateDict, TopDict
from fontTools.misc.psCharStrings import T2CharString
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CFF
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class CFFTable(DefaultTbl):
    """
    This class extends the fontTools ``CFF `` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``CFF `` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_CFF)

    @property
    def top_dict(self) -> TopDict:
        """
        Returns the topDictIndex field of the 'CFF ' table.
        """
        return self.table.cff.topDictIndex[0]

    @property
    def private_dict(self) -> PrivateDict:
        """
        Returns the private field of the 'CFF ' table.
        """
        return self.top_dict.Private

    @property
    def charstrings(self) -> CharStrings:
        """
        Returns the charStrings field of the 'CFF ' table.
        """
        return self.top_dict.CharStrings

    def get_charstring(self, glyph_name: str) -> T2CharString:
        """
        Returns the charstring of a given glyph name.

        Args:
            glyph_name (str): The glyph name to get the char string from.

        Returns:
            bytes: The char string of the given glyph name.
        """
        return self.charstrings[glyph_name]
