import typing as t

from fontTools.misc.roundTools import otRound

from foundrytools_cli_2.lib import logger
from foundrytools_cli_2.lib.constants import T_OS_2
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import CFFTable, HheaTable, PostTable


def log_check_results(check_passed: bool, old: t.Any, new: t.Any, attr_name: str) -> None:
    """
    Log the results of the check.

    Args:
        check_passed (bool): The result of the check.
        old (int): The old value.
        new (int): The new value.
        attr_name (str): The name of the attribute.
    """

    if check_passed:
        logger.opt(colors=True).info(
            "{attr_name}: {old} --> <green>OK</>", attr_name=attr_name, old=old
        )
    else:
        logger.opt(colors=True).info(
            "{attr_name}: <red>{old}</> --> <green>{new}</>", attr_name=attr_name, old=old, new=new
        )


def check_post_table(font: Font, calculated_italic_angle: int) -> None:
    """
    Check the italic angle in the ``post`` table.

    Args:
        font (Font): The Font object representing the font file.
        calculated_italic_angle (int): The calculated italic angle.
    """

    post_table = PostTable(ttfont=font.ttfont)
    old = post_table.italic_angle
    new = calculated_italic_angle
    check_passed = otRound(post_table.italic_angle) == calculated_italic_angle
    log_check_results(check_passed=check_passed, old=old, new=new, attr_name="post.italicAngle")

    if check_passed:
        return
    post_table.italic_angle = calculated_italic_angle
    font.modified = True


def check_hhea_table(font: Font, calculated_italic_angle: int) -> None:
    """
    Check the italic angle the ``hhea`` table.

    Args:
        font (Font): The Font object representing the font file.
        calculated_italic_angle (int): The calculated italic angle.
    """

    hhea_table = HheaTable(ttfont=font.ttfont)
    old = (hhea_table.caret_slope_rise, hhea_table.caret_slope_run)
    calculated_rise = hhea_table.calculate_caret_slope_rise(calculated_italic_angle)
    calculated_run = hhea_table.calculate_caret_slope_run(calculated_italic_angle)
    new = (calculated_rise, calculated_run)
    check_passed = otRound(hhea_table.run_rise_angle) == calculated_italic_angle
    log_check_results(
        check_passed=check_passed, old=old, new=new, attr_name="hhea.caretSlopeRise/Run"
    )

    if check_passed:
        return
    hhea_table.caret_slope_rise = calculated_rise
    hhea_table.caret_slope_run = calculated_run
    font.modified = True


def check_cff_table(font: Font, calculated_italic_angle: int) -> None:
    """
    Check the italic angle and related attributes in the ``CFF`` table.

    Args:
        font (Font): The Font object representing the font file.
        calculated_italic_angle (int): The calculated italic angle.
    """

    cff_table = CFFTable(ttfont=font.ttfont)
    old = cff_table.top_dict.ItalicAngle
    new = calculated_italic_angle
    check_passed = otRound(cff_table.top_dict.ItalicAngle) == calculated_italic_angle
    log_check_results(
        check_passed=check_passed, old=old, new=new, attr_name="CFF.TopDict.ItalicAngle"
    )

    if check_passed:
        return
    cff_table.top_dict.ItalicAngle = calculated_italic_angle
    font.modified = True


def check_italic_bits(font: Font, calculated_italic_angle: int, mode: int) -> None:
    """
    Check the italic and oblique bits in the font.

    Args:
        font (Font): The Font object representing the font file.
        calculated_italic_angle (int): The calculated italic angle.
        mode (int): Which attributes to set when the calculated italic angle is not 0.

            1: Only set the italic bits.
            2: Only set the oblique bit.
            3: Set the italic and oblique bits.
    """

    should_be_italic = calculated_italic_angle != 0 and mode in (1, 3)
    old = font.is_italic
    new = should_be_italic
    check_passed = old == new
    log_check_results(check_passed=check_passed, old=old, new=new, attr_name="Italic")

    if check_passed:
        return
    font.is_italic = should_be_italic
    font.modified = True


def check_oblique_bit(font: Font, calculated_italic_angle: int, mode: int) -> None:
    """
    Check the oblique bit in the font.

    Args:
        font (Font): The Font object representing the font file.
        calculated_italic_angle (int): The calculated italic angle.
        mode (int): Which attributes to set when the calculated italic angle is not 0.

            1: Only set the italic bits.
            2: Only set the oblique bit.
            3: Set the italic and oblique bits.
    """

    should_be_oblique = calculated_italic_angle != 0 and mode in (2, 3)
    old = font.is_oblique
    new = should_be_oblique
    check_passed = old == new
    log_check_results(check_passed=check_passed, old=old, new=new, attr_name="Oblique")

    if check_passed:
        return
    font.is_oblique = should_be_oblique
    font.modified = True


def main(font: Font, min_slant: float = 2.0, mode: int = 1) -> None:
    """
    Fix the italic angle and related attributes in the font.

    Args:
        font (Font): The Font object representing the font file.
        min_slant (float, optional): The minimum slant value to consider a font italic. Defaults to
        2.0.
        mode (int, optional): Which attributes to set when the calculated italic angle is not 0.

            1: Only set the italic bits.
            2: Only set the oblique bit.
            3: Set the italic and oblique bits.

            Defaults to 1.
    """

    calculated_italic_angle = otRound(font.calculate_italic_angle(min_slant=min_slant))
    check_post_table(font=font, calculated_italic_angle=calculated_italic_angle)
    check_hhea_table(font=font, calculated_italic_angle=calculated_italic_angle)
    if font.is_ps:
        check_cff_table(font=font, calculated_italic_angle=calculated_italic_angle)
    check_italic_bits(font=font, calculated_italic_angle=calculated_italic_angle, mode=mode)
    if font.ttfont[T_OS_2].version >= 4:
        check_oblique_bit(font=font, calculated_italic_angle=calculated_italic_angle, mode=mode)
