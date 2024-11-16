from pathlib import Path

from pathvalidate import sanitize_filename

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.tables import CFFTable, NameTable


def _get_file_stem(font: Font, source: int = 1) -> str:
    """
    Get the best file name for a font.

    Args:
        source (int, optional): The source string(s) from which to extract the new file name.
            Default is 1 (FamilyName-StyleName), used also as fallback name when 4 or 5 are
            passed but the font is TrueType.

            1: FamilyName-StyleName
            2: PostScript Name
            3: Full Font Name
            4: CFF fontNames (CFF fonts only)
            5: CFF TopDict FullName (CFF fonts only)

    Returns:
        A sanitized file name for the font.
    """
    name_table = NameTable(font.ttfont)
    cff_table = CFFTable(font.ttfont) if font.is_ps else None

    if font.is_variable:
        family_name = name_table.get_best_family_name().replace(" ", "").strip()
        if font.is_italic:
            family_name += "-Italic"
        axes = font.get_axes()
        file_name = f"{family_name}[{','.join([axis.axisTag for axis in axes])}]"
        return sanitize_filename(file_name, platform="auto")

    if font.is_tt and source in (4, 5):
        source = 1
    if source == 1:
        family_name = name_table.get_best_family_name()
        subfamily_name = name_table.get_best_subfamily_name()
        file_name = f"{family_name}-{subfamily_name}".replace(" ", "").replace(".", "")
    elif source == 2:
        file_name = name_table.get_debug_name(name_id=6)
    elif source == 3:
        file_name = name_table.get_best_full_name()
    elif source == 4 and cff_table is not None:
        file_name = cff_table.table.cff.fontNames[0]
    elif source == 5 and cff_table is not None:
        file_name = cff_table.table.cff.topDictIndex[0].FullName
    else:
        raise ValueError("Invalid source value.")
    return sanitize_filename(file_name, platform="auto")


def main(font: Font, source: int = 1) -> None:
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
    new_file_name = sanitize_filename(_get_file_stem(font=font, source=source))
    new_file = font.get_file_path(
        file=Path(new_file_name),
        extension=font.get_file_ext(),
        output_dir=old_file.parent,
        overwrite=True,
    )
    if new_file == old_file:
        logger.skip(f"{old_file.name} is already named correctly")  # type: ignore
        return
    if new_file.exists():
        logger.warning(f"Another file named {new_file.name} already exists")
        logger.skip(f"{old_file.name} was not renamed")  # type: ignore
        return
    try:
        old_file.rename(new_file)
        logger.opt(colors=True).info(
            f"<light-black>{old_file.name}</> --> " f"<bold><magenta>{new_file.name}</></>"
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error renaming {old_file.name}: {e}")
        return
