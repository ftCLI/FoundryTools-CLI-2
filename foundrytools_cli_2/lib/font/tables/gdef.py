from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_GDEF
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class GdefTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``GDEF`` table.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``GSUB`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_GDEF)
