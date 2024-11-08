from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_POST
from foundrytools_cli_2.lib.tables.default import DefaultTbl


class PostTable(DefaultTbl):
    """
    This class extends the fontTools ``post`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``post`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_POST)

    @property
    def italic_angle(self) -> float:
        """
        Returns the italicAngle field of the 'post' table.
        """
        return self.table.italicAngle

    @italic_angle.setter
    def italic_angle(self, value: float) -> None:
        """
        Sets the italicAngle field of the 'post' table.
        """
        self.table.italicAngle = value

    @property
    def underline_position(self) -> int:
        """
        Returns the underlinePosition field of the 'post' table.
        """
        return self.table.underlinePosition

    @underline_position.setter
    def underline_position(self, value: int) -> None:
        """
        Sets the underlinePosition field of the 'post' table.
        """
        self.table.underlinePosition = value

    @property
    def underline_thickness(self) -> int:
        """
        Returns the underlineThickness field of the 'post' table.
        """
        return self.table.underlineThickness

    @underline_thickness.setter
    def underline_thickness(self, value: int) -> None:
        """
        Sets the underlineThickness field of the 'post' table.
        """
        self.table.underlineThickness = value

    @property
    def fixed_pitch(self) -> bool:
        """
        Returns the isFixedPitch field of the 'post' table.
        """
        return bool(self.table.isFixedPitch)

    @fixed_pitch.setter
    def fixed_pitch(self, value: bool) -> None:
        """
        Sets the isFixedPitch field of the 'post' table.
        """
        self.table.isFixedPitch = abs(int(value))
