import os
import tempfile
import typing as t
from pathlib import Path


def get_temp_file_path(directory: t.Optional[t.Union[str, Path]] = None) -> Path:
    """
    Returns a temporary file path.
    """
    file_descriptor, path = tempfile.mkstemp(dir=directory)
    os.close(file_descriptor)
    return Path(path)
