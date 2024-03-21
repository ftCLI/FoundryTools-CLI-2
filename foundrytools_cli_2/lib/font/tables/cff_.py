from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import CFF_TABLE_TAG
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class CFFTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``CFF `` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``CFF `` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=CFF_TABLE_TAG)
