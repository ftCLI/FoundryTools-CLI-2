import os
import tempfile
import typing as t
from pathlib import Path

from foundrytools_cli_2.cli.logger import logger


def get_temp_file_path(directory: t.Optional[t.Union[str, Path]] = None) -> Path:
    """
    Returns a temporary file path.

    Args:
        directory (str, optional): The directory to create the temporary file in. Defaults to
            ``None``.

    Returns:
        Path: The temporary file path.
    """
    if directory and not Path(directory).is_dir():
        logger.warning(f"{directory} is not a directory, using default temp directory")
        directory = None
    file_descriptor, path = tempfile.mkstemp(dir=directory)
    os.close(file_descriptor)
    return Path(path)
