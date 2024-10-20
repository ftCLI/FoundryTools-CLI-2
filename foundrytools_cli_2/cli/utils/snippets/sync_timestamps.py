# pylint: disable=import-outside-toplevel
import os
import platform
import typing as t
from pathlib import Path

from fontTools.misc.timeTools import epoch_diff, timestampToString

from foundrytools_cli_2.cli.font_finder import FontFinder
from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.constants import T_HEAD


# Helper function for Python 3.8 compatibility
def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def _get_file_timestamps(
    input_path: Path, recursive: bool = True
) -> t.Dict[Path, t.Tuple[int, int]]:
    finder = FontFinder(input_path)
    finder.options.recursive = recursive
    fonts = finder.find_fonts()

    font_timestamps = {
        font.file: (font.ttfont[T_HEAD].created, font.ttfont[T_HEAD].modified)
        for font in fonts
        if font.file
    }

    return font_timestamps


def _get_folder_timestamps(
    folders: t.Set[Path],
    files_timestamps: t.Dict[Path, t.Tuple[int, int]],
) -> t.Dict[Path, t.Tuple[int, int]]:
    folder_timestamps = {
        folder: (
            min(
                files_timestamps[file][0]
                for file in files_timestamps
                if hasattr(file, "is_relative_to")
                and file.is_relative_to(folder)
                or _is_relative_to(file, folder)
            ),
            max(
                files_timestamps[file][1]
                for file in files_timestamps
                if hasattr(file, "is_relative_to")
                and file.is_relative_to(folder)
                or _is_relative_to(file, folder)
            ),
        )
        for folder in folders
    }

    return folder_timestamps


def _set_timestamps(path_timestamps: t.Dict[Path, t.Tuple[int, int]]) -> None:
    for path, timestamps in path_timestamps.items():
        logger.opt(colors=True).info(f"Current path: <light-cyan>{path}</>")

        # Set the file creation time on Windows. Figure out a way to do this on other platforms.
        if platform.system() == "Windows":
            try:
                from win32_setctime import setctime

                setctime(path, timestamps[0] + epoch_diff)
                logger.info(f"created timestamp  : {timestampToString(timestamps[0])}")
            except ImportError as exc:
                raise ImportError(
                    "The 'win32_setctime' package is required for setting file creation times on "
                    "Windows. Please install it by running 'pip install win32_setctime'."
                ) from exc

        os.utime(path, (timestamps[1] + epoch_diff, timestamps[1] + epoch_diff))
        logger.info(f"modified timestamp : {timestampToString(timestamps[1])}")
        logger.info(f"access timestamp   : {timestampToString(timestamps[1])}")

        print()


def main(input_path: Path, recursive: bool = False) -> None:
    """
    Aligns files created and modified timestamps with the created and modified values stored in the
    head table.
    """

    file_timestamps = _get_file_timestamps(input_path, recursive=recursive)
    if not file_timestamps:
        logger.error("No valid font files found.")
        return

    folders = {file.parent for file in file_timestamps}
    folder_timestamps = _get_folder_timestamps(folders, file_timestamps)

    _set_timestamps(file_timestamps)
    _set_timestamps(folder_timestamps)
