from pathlib import Path

from pathvalidate import sanitize_filepath

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def main(
    font: Font,
    in_path: Path,
    sort_by_manufacturer: bool = False,
    sort_by_font_revision: bool = False,
    sort_by_extension: bool = False,
    delete_empty_directories: bool = False,
) -> None:
    """
    Renames the given font files.
    """
    if font.file is None:
        raise AttributeError("Font file is None")

    out_dir = in_path
    old_dir = font.file.parent

    family_name = font.get_best_family_name().strip()
    manufacturer_name = font.get_manufacturer().strip()
    font_revision = "v" + font.get_font_revision().strip()
    extension = font.get_real_extension().replace(".", "").strip()

    if sort_by_manufacturer:
        out_dir = in_path.joinpath(manufacturer_name)

    if sort_by_font_revision:
        out_dir = out_dir.joinpath(family_name + " " + font_revision)
    else:
        out_dir = out_dir.joinpath(family_name)

    if sort_by_extension:
        out_dir = out_dir.joinpath(extension)

    out_dir = sanitize_filepath(out_dir, platform="auto")
    out_dir.mkdir(parents=True, exist_ok=True)
    new_file = font.make_out_file_name(file=out_dir.joinpath(font.file.name), overwrite=True)

    if font.file == new_file:
        logger.skip("No changes made, the file is already in the correct location")  # type: ignore
    elif new_file.exists():
        logger.warning(f"<red>{new_file.relative_to(in_path)}</> already exists")
    else:
        font.file.rename(new_file)
        logger.opt(colors=True).success(
            f"{font.file.relative_to(in_path)} <magenta>--></> "
            f"<green>{new_file.relative_to(in_path)}</>"
        )

    if delete_empty_directories:
        while not any(old_dir.iterdir()):
            old_dir.rmdir()
            logger.opt(colors=True).success(f"{old_dir} <magenta>--></> <red>Deleted</>")
            old_dir = old_dir.parent
