import typing as t
from dataclasses import dataclass
from pathlib import Path

PS_SFNT_VERSION = "OTTO"
TT_SFNT_VERSION = "\0\1\0\0"

WOFF_FLAVOR = "woff"
WOFF2_FLAVOR = "woff2"
OTF_EXTENSION = ".otf"
TTF_EXTENSION = ".ttf"
WOFF_EXTENSION = ".woff"
WOFF2_EXTENSION = ".woff2"

MIN_UPM = 16
MAX_UPM = 16384
MIN_US_WEIGHT_CLASS = 1
MAX_US_WEIGHT_CLASS = 1000
MIN_US_WIDTH_CLASS = 1
MAX_US_WIDTH_CLASS = 9

# Table tags
T_CFF = "CFF "
T_CMAP = "cmap"
T_CVAR = "cvar"
T_FVAR = "fvar"
T_GDEF = "GDEF"
T_GLYF = "glyf"
T_GSUB = "GSUB"
T_HEAD = "head"
T_HHEA = "hhea"
T_HMTX = "hmtx"
T_LOCA = "loca"
T_MAXP = "maxp"
T_NAME = "name"
T_OS_2 = "OS/2"
T_POST = "post"
T_STAT = "STAT"
T_VORG = "VORG"


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
