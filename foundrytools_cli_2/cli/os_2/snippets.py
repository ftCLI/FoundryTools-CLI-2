import typing as t

from afdko.fdkutils import run_shell_command

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import HeadTable, OS2Table
from foundrytools_cli_2.lib.utils.path_tools import get_temp_file_path


def recalc_avg_char_width(font: Font) -> None:
    """
    Recalculates the ``OS/2.xAvgCharWidth`` value.

    Args:
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.recalc_avg_char_width()
    font.modified = os_2_table.modified


def recalc_cap_height(font: Font) -> None:
    """
    Recalculates the ``OS/2.sCapHeight`` value.

    Args:
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.recalc_cap_height()
    font.modified = os_2_table.modified


def recalc_x_height(font: Font) -> None:
    """
    Recalculates the ``OS/2.sXHeight`` value.

    Args:
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.recalc_x_height()
    font.modified = os_2_table.modified


def recalc_max_context(font: Font) -> None:
    """
    Recalculates the ``OS/2.usMaxContext`` value.

    Args:
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.recalc_max_context()
    font.modified = os_2_table.modified


def recalc_unicode_ranges(font: Font, percentage: float = 33) -> None:
    """
    Recalculates the ``OS/2.ulUnicodeRange1`` through ``OS/2.ulUnicodeRange4`` values.

    Args:
        percentage: The minimum percentage of codepoints required for support. Default is 33.
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    result = os_2_table.recalc_unicode_ranges(percentage=percentage)

    if result:
        for block in result:
            logger.info(f"({block[0]}) {block[1]}: {block[2]}")
        font.modified = True


def recalc_ranges_afdko(font: Font) -> None:
    """
    Recalculates the ``OS/2.ulUnicodeRange1`` through ``OS/2.ulUnicodeRange4`` values.

    Args:
        font (Font): The Font object representing the font file.
    """

    # This is no more used in the codebase. Left here for reference.

    os2_table = OS2Table(font.ttfont)
    flavor = font.ttfont.flavor
    font.ttfont.flavor = None
    font.save_to_temp_file()
    temp_t1_file = get_temp_file_path()
    temp_otf_file = get_temp_file_path()
    run_shell_command(["tx", "-t1", font.temp_file, temp_t1_file], suppress_output=True)
    run_shell_command(["makeotf", "-f", temp_t1_file, "-o", temp_otf_file], suppress_output=True)
    temp_font = Font(temp_otf_file)
    temp_os2_table = OS2Table(temp_font.ttfont)
    os2_table.unicode_ranges = temp_os2_table.unicode_ranges
    os2_table.codepage_ranges = temp_os2_table.codepage_ranges
    font.ttfont.flavor = flavor
    font.modified = os2_table.modified
    temp_font.close()
    temp_t1_file.unlink()
    temp_otf_file.unlink()


def recalc_codepage_ranges(font: Font) -> None:
    """
    Recalculates the ``OS/2.ulCodePageRange1`` through ``OS/2.ulCodePageRange2`` values.

    Args:
        font (Font): The Font object representing the font file.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.recalc_code_page_ranges()
    font.modified = os_2_table.modified


def set_attrs(
    font: Font,
    weight_class: t.Optional[int] = None,
    width_class: t.Optional[int] = None,
    vendor_id: t.Optional[str] = None,
    typo_ascender: t.Optional[int] = None,
    typo_descender: t.Optional[int] = None,
    typo_line_gap: t.Optional[int] = None,
    win_ascent: t.Optional[int] = None,
    win_descent: t.Optional[int] = None,
    x_height: t.Optional[int] = None,
    cap_height: t.Optional[int] = None,
) -> None:
    """
    Sets the font's OS/2 table properties based on the provided parameters.

    Args:
        font: The Font object representing The font to modify.
        weight_class (optional): The usWeightClass value to set.
        width_class (optional): The usWidthClass value to set.
        vendor_id (optional): The achVendID value to set.
        x_height (optional): The sXHeight value to set.
        cap_height (optional): The sCapHeight value to set.
        typo_ascender (optional): The sTypoAscender value to set.
        typo_descender (optional): The sTypoDescender value to set.
        typo_line_gap (optional): The sTypoLineGap value to set.
        win_ascent (optional): The usWinAscent value to set.
        win_descent (optional): The usWinDescent value to set.
    """

    os_2_table = OS2Table(font.ttfont)
    attrs = {
        "weight_class": weight_class,
        "width_class": width_class,
        "vendor_id": vendor_id,
        "typo_ascender": typo_ascender,
        "typo_descender": typo_descender,
        "typo_line_gap": typo_line_gap,
        "win_ascent": win_ascent,
        "win_descent": win_descent,
        "x_height": x_height,
        "cap_height": cap_height,
    }

    for attr, value in attrs.items():
        if value is not None:
            try:
                setattr(os_2_table, attr, value)
            except (ValueError, os_2_table.InvalidOS2VersionError) as e:
                logger.error(f"Error setting {attr} to {value}: {e}")
    font.modified = os_2_table.modified


def set_fs_selection(
    font: Font,
    italic: t.Optional[bool] = None,
    bold: t.Optional[bool] = None,
    regular: t.Optional[bool] = None,
    use_typo_metrics: t.Optional[bool] = None,
    wws_consistent: t.Optional[bool] = None,
    oblique: t.Optional[bool] = None,
) -> None:
    """
    Modifies the font's ``OS/2.fsSelection`` attributes based on the provided parameters. Updates
    the font's italic, bold, regular, use_typo_metrics, wws_consistent, and oblique attributes based
    on the provided parameters.

    Args:
        font: The Font object representing the font to modify.
        italic (optional): A boolean value indicating whether the font should be italic.
        bold (optional): A boolean value indicating whether the font should be bold.
        regular (optional): A boolean value indicating whether the font should be regular.
        use_typo_metrics (optional): A boolean value indicating whether to set the use_typo_metrics
            bit in the OS/2 table.
        wws_consistent (optional): A boolean value indicating whether to set the wws_consistent bit
            in the OS/2 table.
        oblique (optional): A boolean value indicating whether to set the oblique bit in the OS/2
            table.
    """
    os_2_table = OS2Table(font.ttfont)
    head_table = HeadTable(font.ttfont)
    if italic is not None:
        font.is_italic = italic
    if bold is not None:
        font.is_bold = bold
    if regular is not None:
        font.is_regular = regular
    if use_typo_metrics is not None:
        os_2_table.fs_selection.use_typo_metrics = use_typo_metrics
    if wws_consistent is not None:
        os_2_table.fs_selection.wws_consistent = wws_consistent
    if oblique is not None:
        os_2_table.fs_selection.oblique = oblique
    # IMPORTANT: head_table.modified must be evaluated before os_2_table.modified to suppress
    # fontTools warning about non-matching bits.
    font.modified = head_table.modified or os_2_table.modified


def set_fs_type(
    font: Font,
    embed_level: t.Optional[int] = None,
    no_subsetting: t.Optional[bool] = None,
    bitmap_embed_only: t.Optional[bool] = None,
) -> None:
    """
    Sets the font's OS/2 table properties related to font embedding and subsetting.

    Args:
        font: The Font object representing the font to modify.
        embed_level (optional): The embedding level to set. It can be 0, 2, or 4.
        no_subsetting (optional): A boolean value indicating whether the font can be subsetted.
        bitmap_embed_only (optional): A boolean value indicating whether only bitmaps should be
            embedded.
    """
    os_2_table = OS2Table(font.ttfont)
    attrs = {
        "embed_level": embed_level,
        "no_subsetting": no_subsetting,
        "bitmap_embed_only": bitmap_embed_only,
    }
    for attr, value in attrs.items():
        if value is not None:
            setattr(os_2_table, attr, value)
    font.modified = os_2_table.modified


def upgrade_version(font: Font, target_version: int) -> None:
    """
    Upgrades the OS/2 table version to the specified version.

    Args:
        font: The Font object representing the font to modify.
        target_version: The version to upgrade to.
    """

    os_2_table = OS2Table(font.ttfont)
    os_2_table.upgrade(target_version)
    font.modified = os_2_table.modified


def set_panose(font: Font, **kwargs: t.Dict[str, int]) -> None:
    """
    Sets the PANOSE classification in the OS/2 table.

    Args:
        font: The Font object representing the font to modify.
        kwargs: A dictionary containing the PANOSE classification values to set.
    """
    os_2_table = OS2Table(font.ttfont)
    for key, value in kwargs.items():
        if value is not None:
            setattr(os_2_table.table.panose, key, value)
    font.modified = os_2_table.modified
