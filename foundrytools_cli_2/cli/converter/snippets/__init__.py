from .otf_to_ttf import main as otf_to_ttf
from .sfnt_to_web import main as sfnt_to_web
from .ttf_to_otf import ttf2otf, ttf2otf_with_tx
from .variable_to_static import main as variable_to_static

__all__ = [
    "otf_to_ttf",
    "ttf2otf",
    "ttf2otf_with_tx",
    "sfnt_to_web",
    "variable_to_static",
]
