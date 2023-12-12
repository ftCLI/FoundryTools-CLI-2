from fontTools.ttLib.tables.C_F_F_ import table_C_F_F_


def get_ps_name(cff_table: table_C_F_F_) -> str:
    """
    Gets the PostScript name of a font from a CFF table.

    Parameters:
        cff_table (table_C_F_F_): The CFF table.

    Returns:
        str: The PostScript name of the font.

    """
    return cff_table.cff.fontNames[0]


def get_font_info(cff_table: table_C_F_F_) -> dict:
    """
    Gets the font info from a CFF table.

    Parameters:
        cff_table (table_C_F_F_): The CFF table.

    Returns:
        dict: The font info.

    """
    return {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].rawDict.items()
        if key not in ("FontBBox", "charset", "Encoding", "Private", "CharStrings")
    }


def get_private_dict(cff_table: table_C_F_F_) -> dict:
    """
    Gets the private dict from a CFF table.

    Parameters:
        cff_table (table_C_F_F_): The CFF table.

    Returns:
        dict: The private dict.

    """
    return {
        key: value
        for key, value in cff_table.cff.topDictIndex[0].Private.rawDict.items()
        if key not in ("Subrs", "defaultWidthX", "nominalWidthX")
    }