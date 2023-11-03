from copy import deepcopy

from fontTools.ttLib.scaleUpem import scale_upem

from foundrytools_cli_2.lib.font import Font


def scale_upm(font: Font, units_per_em: int) -> Font:
    """
    Scale the font's unitsPerEm value to the given value.

    Args:
        font (Font): The font to scale.
        units_per_em (int): The new unitsPerEm value.
    """

    font_copy = deepcopy(font)

    if not font_copy.is_tt:
        raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

    if font_copy["head"].unitsPerEm == units_per_em:
        raise ValueError(
            f"Font already has {units_per_em} units per em. No need to scale upem."
        )

    scale_upem(font_copy, units_per_em)

    return font_copy
