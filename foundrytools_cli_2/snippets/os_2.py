import typing as t

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.os_2 import OS2Table


def recalc_cap_height(font: Font) -> None:
    """
    Recalculates the capHeight value of the OS/2 table of the given font.

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
    Recalculates the xHeight value of the OS/2 table of the given font.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    x_height = font.recalc_x_height()
    os_2_table.x_height = x_height
    font.modified = os_2_table.modified


def set_weight_class(font: Font, weight_class: int) -> None:
    """
    Sets the usWeightClass value of the OS/2 table of the given font.

    Parameters:
        font (Font): The Font object representing the font file.
        weight_class (int): The new usWeightClass value.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    os_2_table.weight_class = weight_class
    font.modified = os_2_table.modified


def set_width_class(font: Font, width_class: int) -> None:
    """
    Sets the usWidthClass value of the OS/2 table of the given font.

    Parameters:
        font (Font): The Font object representing the font file.
        width_class (int): The new usWidthClass value.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    os_2_table.width_class = width_class
    font.modified = os_2_table.modified


def set_fs_type(
    font: Font,
    embed_level: t.Optional[int] = None,
    no_subsetting: t.Optional[bool] = None,
    bitmap_embed_only: t.Optional[bool] = None,
) -> None:
    """
    Sets the font's OS/2 table properties related to font embedding.

    :param font: The `Font` object to modify.
    :param embed_level: (Optional) The embed level to set in the OS/2 table. If not provided,
        the embed level will not be modified.
    :param no_subsetting: (Optional) Whether subsetting is allowed in the font. If not provided,
        the subsetting property will not be modified.
    :param bitmap_embed_only: (Optional) Whether only bitmap embedding is allowed in the font. If
        not provided, the bitmap embedding property will not be modified.
    :return: None
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
        os_2_table.wws = wws_consistent
    if oblique is not None:
        os_2_table.is_oblique = oblique
    font.modified = os_2_table.modified or font.modified
