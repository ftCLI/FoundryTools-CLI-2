from dataclasses import dataclass
import typing as t
from pathlib import Path


@dataclass
class SaveOptions:
    """
    A class that specifies how to save the font.
    """

    reorder_tables: t.Optional[bool] = True
    suffix: str = ""
    output_dir: t.Optional[Path] = None
    overwrite: bool = False


@dataclass
class FinderOptions:
    """
    A class that specifies the options to pass to the FontFinder class.
    """

    recursive: bool = False
    lazy: t.Optional[bool] = None
    recalc_bboxes: bool = True
    recalc_timestamp: bool = False
