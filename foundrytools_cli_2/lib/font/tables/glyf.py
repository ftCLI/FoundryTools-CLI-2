from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph

from foundrytools_cli_2.lib.constants import T_GLYF
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class GlyfTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools ``glyf`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``glyf`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_GLYF)

    @property
    def glyphs(self) -> dict:
        """
        Returns the glyphs of the 'glyf' table.
        """
        return self.table.glyphs

    def get_glyph(self, glyph_name: str) -> Glyph:
        """
        Returns the glyph object of a given glyph name.

        Args:
            glyph_name (str): The glyph name to get the glyph object from.

        Returns:
            Glyph: The glyph object of the given glyph name.
        """
        return self.table.glyphs[glyph_name]
