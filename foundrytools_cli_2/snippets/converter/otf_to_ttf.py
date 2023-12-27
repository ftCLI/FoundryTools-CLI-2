import typing as t

from foundrytools_cli_2.lib import logger
from foundrytools_cli_2.lib.font import Font


def main(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    font.to_ttf(max_err=tolerance, reverse_direction=True)
    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}")
        font.tt_scale_upem(new_upem=target_upm)
