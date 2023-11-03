"""
A helper class to find fonts in a given path.
"""

import logging
import typing as t
from pathlib import Path

from fontTools.ttLib.ttFont import TTFont

F = t.TypeVar("F", bound="TTFont")

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

WOFF_FLAVOR = "woff"
WOFF2_FLAVOR = "woff2"
SFNT_FLAVOR: t.Optional[str] = None
OTF_SFNT_VERSION = "OTTO"
TTF_SFNT_VERSION = "\x00\x01\x00\x00"
FVAR_TABLE = "fvar"


class FontFinderError(Exception):
    pass


class FontFinder:
    """
    A class that finds fonts in a given path. It can search for fonts in a directory and its
    subdirectories, and can also handle a single font file.

    The class allows for filtering based on various criteria such as outline format (TrueType or
    PostScript), font variations (static or variable), and font flavor ('woff', 'woff2' or
    ``None``).

    The class returns a list of TTFont objects, or of TTFont subclass objects, that meet the
    specified criteria.

    Attributes:

        input_path: A Path object pointing to the input path. The input path can be a directory or a
            file.
        recursive: A boolean indicating whether to search recursively.
        return_cls: The return type of the find_fonts() method. The default is ``TTFont``.
        recalc_timestamp: A boolean indicating whether to recalculate the modified timestamp on
            save.
        recalc_bboxes: A boolean indicating whether to recalculate the bounding boxes on save.
        lazy: A boolean indicating whether to load the font lazily. If lazy is set to True, many
            data structures are loaded lazily, upon access only. If it is set to False, many data
            structures are loaded immediately. The default is ``lazy=None`` which is somewhere in
            between.
        filter_out_tt: A boolean indicating whether to filter out TrueType fonts.
        filter_out_ps: A boolean indicating whether to filter out PostScript fonts.
        filter_out_woff: A boolean indicating whether to filter out WOFF fonts.
        filter_out_woff2: A boolean indicating whether to filter out WOFF2 fonts.
        filter_out_sfnt: A boolean indicating whether to filter out sfnt fonts.
        filter_out_static: A boolean indicating whether to filter out static fonts.
        filter_out_variable: A boolean indicating whether to filter out variable fonts.
    """

    def __init__(
        self,
        input_path: t.Union[str, Path],
        recursive: bool = False,
        return_cls: t.Type[F] = TTFont,
        recalc_timestamp: bool = True,
        recalc_bboxes: bool = True,
        lazy: t.Optional[bool] = None,
        filter_out_tt: bool = False,
        filter_out_ps: bool = False,
        filter_out_woff: bool = False,
        filter_out_woff2: bool = False,
        filter_out_sfnt: bool = False,
        filter_out_static: bool = False,
        filter_out_variable: bool = False,
    ) -> None:
        """
        Initialize the FontFinder class.

        Args:
            input_path: A Path object pointing to the input path. The input path can be a directory
                or a file.
            recursive: A boolean indicating whether to search recursively.
            return_cls: The return type of the find_fonts() method. The default is ``TTFont``.
            recalc_timestamp: A boolean indicating whether to recalculate the modified timestamp on
                save.
            recalc_bboxes: A boolean indicating whether to recalculate the bounding boxes on save.
            lazy: A boolean indicating whether to load the font lazily. If lazy is set to True, many
                data structures are loaded lazily, upon access only. If it is set to False, many
                data structures are loaded immediately. The default is ``lazy=None`` which is
                somewhere in between.
            filter_out_tt: A boolean indicating whether to filter out TrueType fonts.
            filter_out_ps: A boolean indicating whether to filter out PostScript fonts.
            filter_out_woff: A boolean indicating whether to filter out WOFF fonts.
            filter_out_woff2: A boolean indicating whether to filter out WOFF2 fonts.
            filter_out_sfnt: A boolean indicating whether to filter out sfnt fonts.
            filter_out_static: A boolean indicating whether to filter out static fonts.
            filter_out_variable: A boolean indicating whether to filter out variable fonts.

        Returns:
            None
        """

        try:
            self.input_path = Path(input_path).resolve(strict=True)
        except Exception as e:
            raise FontFinderError(f"Invalid input path: {input_path}") from e
        self.recursive = recursive
        self.return_cls = return_cls
        self.recalc_timestamp = recalc_timestamp
        self.recalc_bboxes = recalc_bboxes
        self.lazy = lazy
        self.filter_out_tt = filter_out_tt
        self.filter_out_ps = filter_out_ps
        self.filter_out_woff = filter_out_woff
        self.filter_out_woff2 = filter_out_woff2
        self.filter_out_sfnt = filter_out_sfnt
        self.filter_out_static = filter_out_static
        self.filter_out_variable = filter_out_variable

        self._validate_cls()
        self._validate_filters()

        self._filter_conditions = [
            (self.filter_out_tt, _is_tt),
            (self.filter_out_ps, _is_ps),
            (self.filter_out_woff, _is_woff),
            (self.filter_out_woff2, _is_woff2),
            (self.filter_out_sfnt, _is_sfnt),
            (self.filter_out_static, _is_static),
            (self.filter_out_variable, _is_variable),
        ]

    def find_fonts(self) -> t.List[F]:
        """
        Returns a list of TTFont objects found in the input path.

        Returns:
            A list of TTFont objects.
        """
        fonts: t.Generator = self._generate_fonts()
        self._validate_fonts()
        return list(fonts)

    def generate_fonts(self) -> t.Generator[F, None, None]:
        """
        Returns a generator that yields TTFont objects found in the input path.

        Returns:
            A generator of TTFont objects.
        """
        fonts: t.Generator = self._generate_fonts()
        self._validate_fonts()
        return fonts

    def _validate_fonts(self) -> None:
        """
        Validates the fonts generator, raising an exception if it is empty.

        Returns:
            None
        """
        try:
            next(self._generate_fonts())
        except StopIteration:
            raise FontFinderError(f"No fonts matching the criteria found in {self.input_path}")

    def _validate_cls(self) -> None:
        if not issubclass(self.return_cls, TTFont):
            raise FontFinderError("The cls argument must be a subclass of TTFont.")

    def _validate_filters(self) -> None:
        if self.filter_out_tt and self.filter_out_ps:
            raise FontFinderError("Cannot filter out both TrueType and PostScript fonts.")
        if self.filter_out_woff and self.filter_out_woff2 and self.filter_out_sfnt:
            raise FontFinderError("Cannot filter out both web fonts and SFNT fonts.")
        if self.filter_out_static and self.filter_out_variable:
            raise FontFinderError("Cannot filter out both static and variable fonts.")

    def _generate_fonts(self) -> t.Generator[F, None, None]:
        """
        A generator that yields TTFont or TTFont subclass objects found in the input path.

        Returns:
            A generator of TTFont or TTFont subclass objects.
        """
        files = self._generate_files()
        for file in files:
            try:
                font = self.return_cls(
                    file, lazy=self.lazy,
                    recalcTimestamp=self.recalc_timestamp,
                    recalcBBoxes=self.recalc_bboxes,
                )
                if not any(condition and func(font) for condition, func in self._filter_conditions):
                    logger.debug(f"Found font: {file}")
                    yield font
            except Exception as e:
                logger.debug(f"{file}: {e}")

    def _generate_files(self) -> t.Generator[Path, None, None]:
        """
        Returns a list of files in the given input path.

        Returns:
            List[Path]: A list of files in the input path.
        """
        is_file = self.input_path.is_file()
        is_dir = self.input_path.is_dir()

        if is_file:
            yield self.input_path
        elif is_dir:
            if self.recursive:
                yield from (x for x in self.input_path.rglob("*") if x.is_file())
            else:
                yield from (x for x in self.input_path.glob("*") if x.is_file())


def _is_woff(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a WOFF font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a WOFF font.
    """
    return font.flavor == WOFF_FLAVOR


def _is_woff2(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a WOFF2 font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a WOFF2 font.
    """
    return font.flavor == WOFF2_FLAVOR


def _is_sfnt(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a sfnt font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a sfnt font.
    """
    return font.flavor == SFNT_FLAVOR


def _is_ps(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is an OpenType font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is an OpenType font.
    """
    return font.sfntVersion == OTF_SFNT_VERSION


def _is_tt(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a TrueType font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a TrueType font.
    """
    return font.sfntVersion == TTF_SFNT_VERSION


def _is_static(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a static font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a static font.
    """
    return font.get(FVAR_TABLE) is None


def _is_variable(font: TTFont) -> bool:
    """
    Returns a boolean indicating whether the given font is a variable font.

    Args:
        font (TTFont): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a variable font.
    """
    return font.get(FVAR_TABLE) is not None


__all__ = ["FontFinder", "FontFinderError"]
