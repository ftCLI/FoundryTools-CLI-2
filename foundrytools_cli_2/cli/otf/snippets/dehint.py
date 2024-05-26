from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import CFFTable


def main(font: Font, drop_zones_stems: bool = False) -> None:
    """
    This function removes hints from the CFF table of an OpenType font.
    """
    if not font.is_ps:
        raise ValueError("Font is not a PostScript font.")

    cff_table = CFFTable(font.ttfont)
    private = cff_table.private_dict.rawDict
    cff_table.table.cff.remove_hints()

    if not drop_zones_stems:
        cff_table.private_dict.BlueValues = private.get("BlueValues", None)
        cff_table.private_dict.OtherBlues = private.get("OtherBlues", None)
        cff_table.private_dict.FamilyBlues = private.get("FamilyBlues", None)
        cff_table.private_dict.FamilyOtherBlues = private.get("FamilyOtherBlues", None)
        cff_table.private_dict.StdHW = private.get("StdHW", None)
        cff_table.private_dict.StdVW = private.get("StdVW", None)
        cff_table.private_dict.StemSnapH = private.get("StemSnapH", None)
        cff_table.private_dict.StemSnapV = private.get("StemSnapV", None)

    font.modified = True
