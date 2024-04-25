import os
import tempfile
import typing as t
from pathlib import Path


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
        raise NotADirectoryError(f"{directory} is not a directory.")
    file_descriptor, path = tempfile.mkstemp(dir=directory)
    os.close(file_descriptor)
    return Path(path)
