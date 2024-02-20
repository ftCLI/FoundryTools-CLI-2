import typing as t

from foundrytools_cli_2.lib import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import InvalidOS2VersionError, OS2Table


def recalc_avg_char_width(font: Font) -> None:
    """
    Recalculates the ``OS/2.xAvgCharWidth`` value.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    avg_char_width = os_2_table.recalc_avg_char_width()
    os_2_table.avg_char_width = avg_char_width
    font.modified = os_2_table.modified


def recalc_cap_height(font: Font) -> None:
    """
    Recalculates the ``OS/2.sCapHeight`` value.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    cap_height = font.recalc_cap_height()
    os_2_table.cap_height = cap_height
    font.modified = os_2_table.modified


def recalc_x_height(font: Font) -> None:
    """
    Recalculates the ``OS/2.sXHeight`` value.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    x_height = font.recalc_x_height()
    os_2_table.x_height = x_height
    font.modified = os_2_table.modified


def recalc_max_context(font: Font) -> None:
    """
    Recalculates the ``OS/2.usMaxContext`` value.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    max_context = os_2_table.recalc_max_context()
    os_2_table.max_context = max_context
    font.modified = os_2_table.modified


def set_attrs(
    font: Font,
    weight_class: t.Optional[int] = None,
    width_class: t.Optional[int] = None,
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

    Parameters:
        font: The Font object representing The font to modify.
        weight_class (optional): The usWeightClass value to set.
        width_class (optional): The usWidthClass value to set.
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
        "typo_ascender": typo_ascender,
        "typo_descender": typo_descender,
        "typo_line_gap": typo_line_gap,
        "win_ascent": win_ascent,
        "win_descent": win_descent,
        "x_height": x_height,
        "cap_height": cap_height,
    }

    if all(value is None for value in attrs.values()):
        logger.warning("No attributes provided to set.")
        return

    for attr, value in attrs.items():
        if value is not None:
            try:
                setattr(os_2_table, attr, value)
            except (ValueError, InvalidOS2VersionError) as e:
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
    set_fs_selection method modifies the font's attributes based on the provided parameters. It
    updates the font's italic, bold, regular, use_typo_metrics, wws_consistent, and oblique
    attributes based on the provided parameters.

    Parameters:
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

    Returns:
        None
    """
    if all(
        value is None
        for value in (italic, bold, regular, use_typo_metrics, wws_consistent, oblique)
    ):
        logger.warning("No flags provided to set.")
        return

    os_2_table = OS2Table(font.ttfont)
    if italic is not None:
        font.set_italic(italic)
    if bold is not None:
        font.set_bold(bold)
    if regular is not None:
        font.set_regular(regular)
    if use_typo_metrics is not None:
        os_2_table.use_typo_metrics = use_typo_metrics
    if wws_consistent is not None:
        os_2_table.wws_consistent = wws_consistent
    if oblique is not None:
        os_2_table.is_oblique = oblique
    font.modified = os_2_table.modified or font.modified


def set_fs_type(
    font: Font,
    embed_level: t.Optional[int] = None,
    no_subsetting: t.Optional[bool] = None,
    bitmap_embed_only: t.Optional[bool] = None,
) -> None:
    """
    Sets the font's OS/2 table properties related to font embedding and subsetting.

    Parameters:
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
