from dataclasses import dataclass
import typing as t

PS_SFNT_VERSION = "OTTO"
TT_SFNT_VERSION = "\0\1\0\0"
WOFF_FLAVOR = "woff"
WOFF2_FLAVOR = "woff2"
OTF_EXTENSION = ".otf"
TTF_EXTENSION = ".ttf"
WOFF_EXTENSION = ".woff"
WOFF2_EXTENSION = ".woff2"
FVAR_TABLE_TAG = "fvar"
GLYF_TABLE_TAG = "glyf"
MIN_UPM = 16
MAX_UPM = 16384


@dataclass
class TTFontOptions:
    """
    A class that specifies how to load the font.
    """

    lazy: t.Optional[bool] = None
    recalc_timestamp: bool = False
    recalc_bboxes: bool = True
