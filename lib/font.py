from pathlib import Path
import typing as t

from fontTools.ttLib import TTFont


class BaseFont(TTFont):
    def __init__(self, file: t.Optional[t.Union[str, Path]] = None) -> None:
        super().__init__(file=file)
