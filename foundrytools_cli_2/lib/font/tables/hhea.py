import math
import typing as t

from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import HEAD_TABLE_TAG, HHEA_TABLE_TAG, POST_TABLE_TAG
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class HheaTable(DefaultTbl):
    """
    This class extends the fontTools ``hhea`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``hhea`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=HHEA_TABLE_TAG)

    @property
    def ascent(self) -> int:
        """
        Returns the ascent field of the 'hhea' table.
        """
        return self.table.ascent

    @ascent.setter
    def ascent(self, value: int) -> None:
        """
        Sets the ascent field of the 'hhea' table.
        """
        self.table.ascent = value

    @property
    def descent(self) -> int:
        """
        Returns the descent field of the 'hhea' table.
        """
        return self.table.descent

    @descent.setter
    def descent(self, value: int) -> None:
        """
        Sets the descent field of the 'hhea' table.
        """
        self.table.descent = value

    @property
    def line_gap(self) -> int:
        """
        Returns the lineGap field of the 'hhea' table.
        """
        return self.table.lineGap

    @line_gap.setter
    def line_gap(self, value: int) -> None:
        """
        Sets the lineGap field of the 'hhea' table.
        """
        self.table.lineGap = value

    @property
    def advance_width_max(self) -> int:
        """
        Returns the advanceWidthMax field of the 'hhea' table.
        """
        return self.table.advanceWidthMax

    @advance_width_max.setter
    def advance_width_max(self, value: int) -> None:
        """
        Sets the advanceWidthMax field of the 'hhea' table.
        """
        self.table.advanceWidthMax = value

    @property
    def min_left_side_bearing(self) -> int:
        """
        Returns the minLeftSideBearing field of the 'hhea' table.
        """
        return self.table.minLeftSideBearing

    @property
    def min_right_side_bearing(self) -> int:
        """
        Returns the minRightSideBearing field of the 'hhea' table.
        """
        return self.table.minRightSideBearing

    @property
    def x_max_extent(self) -> int:
        """
        Returns the xMaxExtent field of the 'hhea' table.
        """
        return self.table.xMaxExtent

    @property
    def caret_slope_rise(self) -> int:
        """
        Returns the caretSlopeRise field of the 'hhea' table.
        """
        return self.table.caretSlopeRise

    @caret_slope_rise.setter
    def caret_slope_rise(self, value: int) -> None:
        """
        Sets the caretSlopeRise field of the 'hhea' table.
        """
        self.table.caretSlopeRise = value

    @property
    def caret_slope_run(self) -> int:
        """
        Returns the caretSlopeRun field of the 'hhea' table.
        """
        return self.table.caretSlopeRun

    @caret_slope_run.setter
    def caret_slope_run(self, value: int) -> None:
        """
        Sets the caretSlopeRun field of the 'hhea' table.
        """
        self.table.caretSlopeRun = value

    @property
    def caret_offset(self) -> int:
        """
        Returns the caretOffset field of the 'hhea' table.
        """
        return self.table.caretOffset

    @caret_offset.setter
    def caret_offset(self, value: int) -> None:
        """
        Sets the caretOffset field of the 'hhea' table.
        """
        self.table.caretOffset = value

    @property
    def metric_data_format(self) -> int:
        """
        Returns the metricDataFormat field of the 'hhea' table.
        """
        return self.table.metricDataFormat

    @property
    def number_of_hmetrics(self) -> int:
        """
        Returns the numberOfHMetrics field of the 'hhea' table.
        """
        return self.table.numberOfHMetrics

    @property
    def run_rise_angle(self) -> float:
        """
        Calculate the slope angle by dividing the caret slope run by the caret slope rise

        Returns:
            float: The run/rise angle in degrees.
        """
        rise = self.table.caretSlopeRise
        run = self.table.caretSlopeRun
        run_rise_angle = math.degrees(math.atan(-run / rise))
        return run_rise_angle

    def calculate_caret_slope_rise(
        self, italic_angle: t.Optional[t.Union[int, float]] = None
    ) -> int:
        """
        Calculate the caret ``hhea.caretSlopeRise`` of the font.

        Args:
            italic_angle (t.Optional[t.Union[int, float]]): The italic to use for the calculation.
                If ``None``, the italic angle from the ``post`` table will be used.

        Returns:
            int: The caret slope rise value.
        """

        if italic_angle is None:
            italic_angle = self.ttfont[POST_TABLE_TAG].italicAngle

        if italic_angle == 0:
            return 1
        return self.ttfont[HEAD_TABLE_TAG].unitsPerEm

    def calculate_caret_slope_run(
        self, italic_angle: t.Optional[t.Union[int, float]] = None
    ) -> int:
        """
        Calculate the caret ``hhea.caretSlopeRun`` of the font.

        Args:
            italic_angle (t.Optional[t.Union[int, float]]): The italic to use for the calculation.
                If ``None``, the italic angle from the ``post`` table will be used.

        Returns:
            int: The caret slope run value.
        """

        if italic_angle is None:
            italic_angle = self.ttfont[POST_TABLE_TAG].italicAngle

        if italic_angle == 0:
            return 0
        return otRound(
            math.tan(math.radians(-self.ttfont[POST_TABLE_TAG].italicAngle))
            * self.ttfont[HEAD_TABLE_TAG].unitsPerEm
        )
