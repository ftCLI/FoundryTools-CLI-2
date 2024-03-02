import typing as t

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import PostTable
from foundrytools_cli_2.lib.logger import logger


def set_attrs(
    font: Font,
    italic_angle: t.Optional[float] = None,
    underline_position: t.Optional[int] = None,
    underline_thickness: t.Optional[int] = None,
    fixed_pitch: t.Optional[bool] = None,
) -> None:
    """
    Sets the attributes of the 'post' table.
    Parameters:
        font (Font): The Font object representing the font file.
        italic_angle (float): The `italicAngle` value.
        underline_position (int): The `underlinePosition` value.
        underline_thickness (int): The `underlineThickness` value.
        fixed_pitch (bool): The `isFixedPitch` value.
    Returns:
        None
    """
    post_table = PostTable(font.ttfont)
    attrs = {
        "italic_angle": italic_angle,
        "underline_position": underline_position,
        "underline_thickness": underline_thickness,
        "fixed_pitch": fixed_pitch,
    }
    for attr, value in attrs.items():
        if value is not None:
            old_value = getattr(post_table, attr)
            logger.info(f"{attr}: {old_value} -> {value}")
            setattr(post_table, attr, value)
    font.modified = post_table.modified
