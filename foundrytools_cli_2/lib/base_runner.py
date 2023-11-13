from abc import abstractmethod
from pathlib import Path
import typing as t

from foundrytools_cli_2.lib.font import Font, TTFontOptions
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.lib.font_finder import FontFinder, FontFinderError, FontFinderFilter


class BaseRunner:
    """
    A base class for runners.
    """
    def __init__(
            self,
            input_path: Path,
            ttfont_options: t.Optional[TTFontOptions] = None,
            finder_filter: t.Optional[FontFinderFilter] = None,
            **kwargs,
    ) -> None:
        """
        Initialize the runner.
        """
        self.input_path = input_path
        self.ttfont_options = ttfont_options or TTFontOptions()
        self.finder_filter = finder_filter or FontFinderFilter()
        self._kwargs = kwargs

    @Timer(text="\nElapsed time: {0:.3f}s")
    def run(self) -> None:
        """
        Run the runner. This method must be overridden by subclasses.
        """
        for font in self._find_fonts():
            self._run(font)

    def _find_fonts(self) -> t.List[Font]:
        """
        Get the source fonts.
        """
        finder = FontFinder(
            self.input_path, options=self.ttfont_options, filters=self.finder_filter
        )
        fonts = finder.find_fonts()
        if not fonts:
            raise FontFinderError("No fonts found.")
        return fonts

    @abstractmethod
    @Timer(text="\nElapsed time: {0:.3f}s")
    def _run(self, font: [Font], **kwargs) -> None:
        """
        Run the runner. This method must be overridden by subclasses.
        """
        raise NotImplementedError
