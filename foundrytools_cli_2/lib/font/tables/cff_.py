from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class CFFTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools `CFF ` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        super().__init__(ttfont, "CFF ")
