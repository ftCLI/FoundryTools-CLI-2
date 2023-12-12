import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.font import Font, WOFF_FLAVOR, WOFF2_FLAVOR
from foundrytools_cli_2.lib.logger import logger


def sfnt_to_wf(
    font: Font,
    output_dir: t.Optional[Path] = None,
    out_format: t.Optional[t.Literal["woff", "woff2"]] = None,
    overwrite: bool = True,
    reorder_tables: bool = False,
) -> None:
    """
    Convert SFNT fonts to WOFF and/or WOFF2 fonts.
    """

    # Get the extension of the input file to reuse it later as suffix.
    # If we don't add a suffix to the output file name here, an undesired overwriting
    # may occur. For example, if we convert a WOFF and a WOFF2 with the same stem and
    # the same sfntVersion, the file converted first will be overwritten by the second
    # one.
    suffix = font.get_real_extension()

    if out_format is None:
        out_formats = [WOFF_FLAVOR, WOFF2_FLAVOR]
    else:
        out_formats = [out_format]

    if WOFF_FLAVOR in out_formats:
        logger.info("Converting to WOFF")
        font.to_woff()
        out_file = font.make_out_file_name(
            output_dir=output_dir, overwrite=overwrite, suffix=suffix
        )
        font.save(out_file, reorder_tables=reorder_tables)
        logger.success(f"File saved to {out_file}")

    if WOFF2_FLAVOR in out_formats:
        logger.info("Converting to WOFF2")
        font.to_woff2()
        out_file = font.make_out_file_name(
            output_dir=output_dir, overwrite=overwrite, suffix=suffix
        )
        font.save(out_file, reorder_tables=reorder_tables)
        logger.success(f"File saved to {out_file}")
