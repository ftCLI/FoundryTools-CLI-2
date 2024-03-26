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
CFF_TABLE_TAG = "CFF "
CMAP_TABLE_TAG = "cmap"
CVAR_TABLE_TAG = "cvar"
FVAR_TABLE_TAG = "fvar"
GDEF_TABLE_TAG = "GDEF"
GLYF_TABLE_TAG = "glyf"
GSUB_TABLE_TAG = "GSUB"
HEAD_TABLE_TAG = "head"
HHEA_TABLE_TAG = "hhea"
HMTX_TABLE_TAG = "hmtx"
NAME_TABLE_TAG = "name"
OS_2_TABLE_TAG = "OS/2"
POST_TABLE_TAG = "post"
STAT_TABLE_TAG = "STAT"


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
