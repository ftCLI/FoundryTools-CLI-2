from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(font: Font, source: int = 1, overwrite: bool = False) -> None:
    """
    Renames the given font files.
    """
    if font.file is None:
        raise AttributeError("Font file is None")
    old_file = font.file
    if source in (4, 5) and font.is_tt:
        logger.warning(
            f"source=4 and source=5 can be used for OTF files only. Using source=1 for "
            f"{old_file.name}"
        )
    new_file = font.make_out_file_name(
        file=font.get_best_file_name(source=source),
        extension=font.get_real_extension(),
        output_dir=old_file.parent,
        overwrite=overwrite,
    )
    if new_file == old_file:
        logger.skip(f"{old_file.name} is already named correctly")  # type: ignore
        return
    old_file.rename(new_file)
    logger.opt(colors=True).info(
        f"<light-black>{old_file.name}</> --> " f"<bold><magenta>{new_file.name}</></>"
    )
