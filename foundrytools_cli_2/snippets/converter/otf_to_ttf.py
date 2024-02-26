import typing as t
from pathlib import Path

from foundrytools_cli_2.lib import logger
from foundrytools_cli_2.lib.font import Font


def main(
    font: Font,
    tolerance: float = 1.0,
    target_upm: t.Optional[int] = None,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
) -> None:
    """
    Convert PostScript flavored fonts to TrueType flavored fonts.
    """
    flavor = font.ttfont.flavor
    suffix = ".ttf" if flavor is not None else ""
    extension = ".ttf" if flavor is None else f".{flavor}"
    out_file = font.make_out_file_name(
        output_dir=output_dir, overwrite=overwrite, extension=extension, suffix=suffix
    )

    logger.info("Convert to TTF...")
    font.to_ttf(max_err=tolerance, reverse_direction=True)

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(new_upem=target_upm)

    font.save(out_file)
    logger.success(f"File saved to {out_file}")
