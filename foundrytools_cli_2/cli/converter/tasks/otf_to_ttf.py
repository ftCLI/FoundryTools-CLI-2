import typing as t
from pathlib import Path

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.constants import T_HEAD
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

    Args:
        font (Font): The font to convert
        tolerance (float, optional): The maximum error allowed when converting the font to TrueType.
            Defaults to 1.0.
        target_upm (t.Optional[int], optional): The target UPM to scale the font to. Defaults to
            ``None``.
        output_dir (t.Optional[Path], optional): The output directory. If ``None``, the output file
            will be saved in the same directory as the input file. Defaults to ``None``.
        overwrite (bool, optional): Whether to overwrite the output file if it already exists.
            Defaults to ``True``.
    """
    flavor = font.ttfont.flavor
    suffix = ".ttf" if flavor is not None else ""
    extension = font.get_file_ext() if flavor is not None else ".ttf"
    out_file = font.get_file_path(
        output_dir=output_dir, overwrite=overwrite, extension=extension, suffix=suffix
    )

    tolerance = tolerance / 1000 * font.ttfont[T_HEAD].unitsPerEm

    logger.info("Converting to TTF...")
    font.to_ttf(max_err=tolerance, reverse_direction=True)

    if target_upm:
        logger.info(f"Scaling UPM to {target_upm}...")
        font.tt_scale_upem(target_upm=target_upm)

    font.save(out_file)
    logger.success(f"File saved to {out_file}")
