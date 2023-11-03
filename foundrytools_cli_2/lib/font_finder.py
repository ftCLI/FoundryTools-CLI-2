"""
A helper class to find fonts in a given path.
"""

import logging
import typing as t
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib.ttFont import TTFont, TTLibError

from foundrytools_cli_2.lib.font import Font

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

WOFF_FLAVOR = "woff"
WOFF2_FLAVOR = "woff2"
OTF_SFNT_VERSION = "OTTO"
TTF_SFNT_VERSION = "\x00\x01\x00\x00"
FVAR_TABLE = "fvar"


@dataclass
class FontFinderFilters:
    filter_out_tt: bool = False
    filter_out_ps: bool = False
    filter_out_woff: bool = False
    filter_out_woff2: bool = False
    filter_out_sfnt: bool = False
    filter_out_static: bool = False
    filter_out_variable: bool = False


class FontFinderError(Exception):
    """
    An exception raised by the FontFinder class.
    """


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
        recalc_timestamp: A boolean indicating whether to recalculate the modified timestamp on
            save.
        recalc_bboxes: A boolean indicating whether to recalculate the bounding boxes on save.
        lazy: A boolean indicating whether to load the font lazily. If lazy is set to True, many
            data structures are loaded lazily, upon access only. If it is set to False, many data
            structures are loaded immediately. The default is ``lazy=None`` which is somewhere in
            between.
        filters: A FontFinderFilters object that specifies which fonts to filter out.
    """

    def __init__(
        self,
        input_path: t.Union[str, Path],
        recursive: bool = False,
        recalc_timestamp: bool = True,
        recalc_bboxes: bool = True,
        lazy: t.Optional[bool] = None,
        filters=FontFinderFilters(),
    ) -> None:
        """
        Initialize the FontFinder class.

        Args:
            input_path: A Path object pointing to the input path. The input path can be a directory
                or a file.
            recursive: A boolean indicating whether to search recursively.
            recalc_timestamp: A boolean indicating whether to recalculate the modified timestamp on
                save.
            recalc_bboxes: A boolean indicating whether to recalculate the bounding boxes on save.
            lazy: A boolean indicating whether to load the font lazily. If lazy is set to True, many
                data structures are loaded lazily, upon access only. If it is set to False, many
                data structures are loaded immediately. The default is ``lazy=None`` which is
                somewhere in between.
            filters: A FontFinderFilters object that specifies which fonts to filter out.

        Returns:
            None
        """

        try:
            self.input_path = Path(input_path).resolve(strict=True)
        except Exception as e:
            raise FontFinderError(f"Invalid input path: {input_path}") from e
        self.recursive = recursive
        self.recalc_timestamp = recalc_timestamp
        self.recalc_bboxes = recalc_bboxes
        self.lazy = lazy
        self.filters = filters

        self._validate_filters()

        self._filter_conditions = [
            (self.filters.filter_out_tt, _is_tt),
            (self.filters.filter_out_ps, _is_ps),
            (self.filters.filter_out_woff, _is_woff),
            (self.filters.filter_out_woff2, _is_woff2),
            (self.filters.filter_out_sfnt, _is_sfnt),
            (self.filters.filter_out_static, _is_static),
            (self.filters.filter_out_variable, _is_variable),
        ]

    def find_fonts(self) -> t.List[Font]:
        """
        Returns a list of TTFont objects found in the input path.

        Returns:
            A list of TTFont objects.
        """
        fonts: t.Generator = self._generate_fonts()
        self._validate_fonts()
        return list(fonts)

    def generate_fonts(self) -> t.Generator[Font, None, None]:
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
        except StopIteration as e:
            raise FontFinderError(
                f"No fonts matching the criteria found in {self.input_path}"
            ) from e

    def _validate_filters(self) -> None:
        if self.filters.filter_out_tt and self.filters.filter_out_ps:
            raise FontFinderError("Cannot filter out both TrueType and PostScript fonts.")
        if (
            self.filters.filter_out_woff
            and self.filters.filter_out_woff2
            and self.filters.filter_out_sfnt
        ):
            raise FontFinderError("Cannot filter out both web fonts and SFNT fonts.")
        if self.filters.filter_out_static and self.filters.filter_out_variable:
            raise FontFinderError("Cannot filter out both static and variable fonts.")

    def _generate_fonts(self) -> t.Generator[Font, None, None]:
        """
        A generator that yields TTFont or TTFont subclass objects found in the input path.

        Returns:
            A generator of TTFont or TTFont subclass objects.
        """
        files = self._generate_files()
        for file in files:
            try:
                font = Font(
                    file,
                    lazy=self.lazy,
                    recalc_timestamp=self.recalc_timestamp,
                    recalc_bboxes=self.recalc_bboxes,
                )
                if not any(condition and func(font) for condition, func in self._filter_conditions):
                    logger.debug("Found font: %s", file)
                    yield font
            except TTLibError as e:
                logger.debug("%s: %s", file, e)

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


def _is_sfnt(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a sfnt font.

    Args:
        font (Font): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a sfnt font.
    """
    return font.flavor is None


def _is_ps(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is an OpenType font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is an OpenType font.
    """
    return font.sfntVersion == OTF_SFNT_VERSION


def _is_tt(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a TrueType font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a TrueType font.
    """
    return font.sfntVersion == TTF_SFNT_VERSION


def _is_static(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a static font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a static font.
    """
    return font.get(FVAR_TABLE) is None


def _is_variable(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a variable font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a variable font.
    """
    return font.get(FVAR_TABLE) is not None


__all__ = ["FontFinder", "FontFinderError"]
