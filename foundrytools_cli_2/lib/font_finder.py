import typing as t
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib.ttFont import TTLibError

from foundrytools_cli_2.lib.constants import FontInitOptions
from foundrytools_cli_2.lib.font import Font


@dataclass
class FontFinderFilter:
    """
    A class that specifies which fonts to filter out when searching for fonts.
    """

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

    The class returns a list of Font objects that meet the specified criteria.

    Attributes:

        input_path: A Path object pointing to the input path. The input path can be a directory or a
            file.
        recursive: A boolean indicating whether to search recursively.
        font_options: A FontLoadOptions object that specifies how to load the fonts.
        font_filter: A FontFinderFilters object that specifies which fonts to filter out.
    """

    def __init__(
        self,
        input_path: t.Union[str, Path],
        recursive: bool = False,
        font_options: t.Optional[FontInitOptions] = None,
        font_filter: t.Optional[FontFinderFilter] = None,
    ) -> None:
        """
        Initialize the FontFinder class.

        Args:
            input_path: A Path object pointing to the input path. The input path can be a directory
                or a file.
            recursive: A boolean indicating whether to search recursively.
            font_options: A FontLoadOptions object that specifies how to load the fonts.
            font_filter: A FontFinderFilters object that specifies which fonts to filter out.

        Returns:
            None
        """

        try:
            self.input_path = Path(input_path).resolve(strict=True)
        except Exception as e:
            raise FontFinderError(f"Invalid input path: {input_path}") from e
        self.recursive = recursive
        self.font_options = font_options or FontInitOptions()
        self.font_filter = font_filter or FontFinderFilter()
        self._filter_conditions = self._generate_filter_conditions(self.font_filter)
        self._validate_font_filter()

    def find_fonts(self) -> t.List[Font]:
        """
        Returns a list of TTFont objects found in the input path.

        Returns:
            A list of TTFont objects.
        """
        return list(self.generate_fonts())

    def generate_fonts(self) -> t.Generator[Font, None, None]:
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
                    lazy=self.font_options.lazy,
                    recalc_timestamp=self.font_options.recalc_timestamp,
                    recalc_bboxes=self.font_options.recalc_bboxes,
                )
                if not any(condition and func(font) for condition, func in self._filter_conditions):
                    yield font
            except TTLibError:
                pass

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

    def _validate_font_filter(self) -> None:
        """
        Validates the font filter options.

        The font filter is used to specify which types of fonts to include or exclude
        when searching for fonts.

        Raises:
            FontFinderError: If the font filter options are invalid.
        """
        if self.font_filter.filter_out_tt and self.font_filter.filter_out_ps:
            raise FontFinderError("Cannot filter out both TrueType and PostScript fonts.")
        if (
            self.font_filter.filter_out_woff
            and self.font_filter.filter_out_woff2
            and self.font_filter.filter_out_sfnt
        ):
            raise FontFinderError("Cannot filter out both web fonts and SFNT fonts.")
        if self.font_filter.filter_out_static and self.font_filter.filter_out_variable:
            raise FontFinderError("Cannot filter out both static and variable fonts.")

    @staticmethod
    def _generate_filter_conditions(filter_: FontFinderFilter) -> t.List[t.Tuple[bool, t.Callable]]:
        """
        Generate filter conditions based on the provided FontFinderFilter object.

        Parameters:
            filter_: A FontFinderFilter object.

        Returns:
            List[t.Tuple[bool, t.Callable]]: A list of tuples containing a boolean and a callable.
            The boolean indicates whether the filter condition is active, and the callable is a
            function that returns a boolean indicating whether the given font meets the filter
            condition.
        """
        conditions = [
            (filter_.filter_out_tt, _is_tt),
            (filter_.filter_out_ps, _is_ps),
            (filter_.filter_out_woff, _is_woff),
            (filter_.filter_out_woff2, _is_woff2),
            (filter_.filter_out_sfnt, _is_sfnt),
            (filter_.filter_out_static, _is_static),
            (filter_.filter_out_variable, _is_variable),
        ]
        return conditions


def _is_woff(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a WOFF font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a WOFF font.
    """
    return font.is_woff


def _is_woff2(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a WOFF2 font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a WOFF2 font.
    """
    return font.is_woff2


def _is_sfnt(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a sfnt font.

    Args:
        font (Font): A TTFont object.

    Returns:
        bool: A boolean indicating whether the given font is a sfnt font.
    """
    return font.is_sfnt


def _is_ps(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is an OpenType font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is an OpenType font.
    """
    return font.is_ps


def _is_tt(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a TrueType font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a TrueType font.
    """
    return font.is_tt


def _is_static(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a static font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a static font.
    """
    return font.is_static


def _is_variable(font: Font) -> bool:
    """
    Returns a boolean indicating whether the given font is a variable font.

    Args:
        font (Font): A Font object.

    Returns:
        bool: A boolean indicating whether the given font is a variable font.
    """
    return font.is_variable


__all__ = ["FontFinder", "FontFinderError", "FontFinderFilter"]
