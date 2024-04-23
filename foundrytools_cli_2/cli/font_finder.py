import typing as t
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib.ttFont import TTLibError

from foundrytools_cli_2.lib.font import Font

__all__ = ["FinderError", "FinderFilter", "FinderOptions", "FontFinder"]

@dataclass
class FinderOptions:
    """
    A class that specifies the options to pass to the FontFinder class.
    """

    recursive: bool = False
    lazy: t.Optional[bool] = None
    recalc_bboxes: bool = True
    recalc_timestamp: bool = False


@dataclass
class FinderFilter:
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


class FinderError(Exception):
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

    The class returns a list or a generator of Font objects that meet the specified criteria.
    """

    def __init__(
        self,
        input_path: Path,
        options: FinderOptions,
        filter_: t.Optional[FinderFilter] = None,
    ) -> None:
        """Initialize the FontFinder class.

        Args:
            options (FinderOptions): An instance of FinderOptions class that contains the options
                for font finding.
            filter_ (FontFinderFilter, optional): An instance of FontFinderFilter class that
                specifies the filter conditions for font finding. Defaults to None.

        Raises:
            FontFinderError: If the input path is invalid.
        """
        self.input_path = input_path
        self.options = options

        try:
            self.input_path = Path(self.input_path).resolve(strict=True)
        except Exception as e:
            raise FinderError(f"Invalid input path: {self.input_path}") from e

        self.filter = filter_ or FinderFilter()
        self._filter_conditions = self._generate_filter_conditions(self.filter)
        self._validate_filter_conditions()

    def find_fonts(self) -> t.List[Font]:
        """
        Returns a list of ``Font`` objects found in the input path.

        Returns:
            A list of ``Font`` objects.
        """
        return list(self.generate_fonts())

    def generate_fonts(self) -> t.Generator[Font, None, None]:
        """
        Generates a collection of fonts.

        Returns:
            Generator[Font, None, None]: A generator that yields ``Font`` objects.
        """
        files = self._generate_files()
        for file in files:
            try:
                font = Font(
                    file,
                    lazy=self.options.lazy,
                    recalc_timestamp=self.options.recalc_timestamp,
                    recalc_bboxes=self.options.recalc_bboxes,
                )
                if not any(condition and func(font) for condition, func in self._filter_conditions):
                    yield font
            except (TTLibError, PermissionError):
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
            if self.options.recursive:
                yield from (x for x in self.input_path.rglob("*") if x.is_file())
            else:
                yield from (x for x in self.input_path.glob("*") if x.is_file())

    def _validate_filter_conditions(self) -> None:
        """
        Validates the font filter options.

        The font filter is used to specify which types of fonts to include or exclude
        when searching for fonts.

        Raises:
            FontFinderError: If the font filter options are invalid.
        """
        if self.filter.filter_out_tt and self.filter.filter_out_ps:
            raise FinderError("Cannot filter out both TrueType and PostScript fonts.")
        if (
            self.filter.filter_out_woff
            and self.filter.filter_out_woff2
            and self.filter.filter_out_sfnt
        ):
            raise FinderError("Cannot filter out both web fonts and SFNT fonts.")
        if self.filter.filter_out_static and self.filter.filter_out_variable:
            raise FinderError("Cannot filter out both static and variable fonts.")

    @staticmethod
    def _generate_filter_conditions(filter_: FinderFilter) -> t.List[t.Tuple[bool, t.Callable]]:
        """
        Generate filter conditions based on the provided FontFinderFilter object.

        Args:
            filter_: A ``FontFinderFilter`` object.

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
    return font.is_woff


def _is_woff2(font: Font) -> bool:
    return font.is_woff2


def _is_sfnt(font: Font) -> bool:
    return font.is_sfnt


def _is_ps(font: Font) -> bool:
    return font.is_ps


def _is_tt(font: Font) -> bool:
    return font.is_tt


def _is_static(font: Font) -> bool:
    return font.is_static


def _is_variable(font: Font) -> bool:
    return font.is_variable
