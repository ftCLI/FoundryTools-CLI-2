from enum import IntEnum
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
NAMES_TO_UNICODES_FILE = Path.joinpath(DATA_DIR, "names_to_unicodes.json")
UNICODES_TO_NAMES_FILE = Path.joinpath(DATA_DIR, "unicodes_to_names.json")

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
T_FPGM = "fpgm"
T_FVAR = "fvar"
T_GDEF = "GDEF"
T_GLYF = "glyf"
T_GSUB = "GSUB"
T_HEAD = "head"
T_HHEA = "hhea"
T_HMTX = "hmtx"
T_KERN = "kern"
T_LOCA = "loca"
T_MAXP = "maxp"
T_NAME = "name"
T_OS_2 = "OS/2"
T_POST = "post"
T_STAT = "STAT"
T_VORG = "VORG"


class NameIds(IntEnum):
    """
    Name IDs for the name table.
    """

    FAMILY_NAME = 1
    SUBFAMILY_NAME = 2
    UNIQUE_FONT_IDENTIFIER = 3
    FULL_FONT_NAME = 4
    VERSION_STRING = 5
    POSTSCRIPT_NAME = 6
    TRADEMARK = 7
    MANUFACTURER_NAME = 8
    DESIGNER_NAME = 9
    DESCRIPTION = 10
    VENDOR_URL = 11
    DESIGNER_URL = 12
    LICENSE_DESCRIPTION = 13
    LICENSE_INFO_URL = 14
    RESERVED = 15
    TYPO_FAMILY_NAME = 16
    TYPO_SUBFAMILY_NAME = 17
    COMPATIBLE_FULL_NAME_MAC = 18
    SAMPLE_TEXT = 19
    PS_CID_FINDFONT_NAME = 20
    WWS_FAMILY_NAME = 21
    WWS_SUBFAMILY_NAME = 22
    LIGHT_BACKGROUND_PALETTE = 23
    DARK_BACKGROUND_PALETTE = 24
    VARIATIONS_POSTSCRIPT_NAME_PREFIX = 25


TOP_DICT_NAMES = {
    "full-name": "FullName",
    "family-name": "FamilyName",
    "weight": "Weight",
    "version": "version",
    "notice": "Notice",
    "copyright": "Copyright",
}
