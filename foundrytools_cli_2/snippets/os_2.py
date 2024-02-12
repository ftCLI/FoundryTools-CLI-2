from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables.os_2 import OS2Table


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
    os_2_table.usWeightClass = weight_class
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
    os_2_table.usWidthClass = width_class
    font.modified = os_2_table.modified


def set_embed_level(font: Font, embed_level: int) -> None:
    """
    Sets the fsType value of the OS/2 table of the given font.

    Parameters:
        font (Font): The Font object representing the font file.
        embed_level (int): The new fsType value.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    os_2_table.set_embed_level(embed_level)
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
    os_2_table.set_x_height(x_height)
    font.modified = os_2_table.modified


def recalc_cap_height(font: Font) -> None:
    """
    Recalculates the capHeight value of the OS/2 table of the given font.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2_table = OS2Table(font.ttfont)
    os_2_table.capHeight = font.recalc_cap_height()
    font.modified = os_2_table.modified


def test(font: Font) -> None:
    """
    Test the OS/2 table of the given font file.

    Parameters:
        font (Font): The Font object representing the font file.

    Returns:
        None
    """
    os_2 = OS2Table(font.ttfont)
    print(f"Font file: {font.file}")
    print(f"usWeightClass: {os_2.table.usWeightClass}")
    print(f"usWidthClass: {os_2.table.usWidthClass}")
    print(f"fsSelection: {os_2.table.fsSelection} ({type(os_2.table.fsSelection)})")
    os_2.set_oblique_bit()
    print(f"Modified: {os_2.modified}")
    os_2.clear_oblique_bit()
    print(f"Modified: {os_2.modified}")
