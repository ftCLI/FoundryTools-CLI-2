import typing as t
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from foundrytools_cli_2.lib import Font, logger
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderFilter,
)


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


class LoggerError(Exception):
    """Raised when there is an error with the logger"""


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


@dataclass
class FontSaveOptions:
    """
    A class that specifies how to save the font.
    """

    output_dir: t.Optional[Path] = None
    overwrite: bool = False
    reorder_tables: t.Optional[bool] = True


@dataclass
class FontInitOptions:
    """
    A class that specifies how to initialize the font.
    """

    lazy: t.Optional[bool] = None
    recalc_timestamp: bool = False
    recalc_bboxes: bool = True


class BaseRunner(metaclass=ABCMeta):
    """Base class for all runners"""

    def __init__(
        self,
        input_path: Path,
        recursive: bool = False,
        load_options: t.Optional[FontInitOptions] = None,
        save_options: t.Optional[FontSaveOptions] = None,
        font_filter: t.Optional[FontFinderFilter] = None,
        task_name: str = "Processing",
    ) -> None:
        self.input_path = input_path
        self.recursive = recursive
        self.font_init_options = load_options or FontInitOptions()
        self.font_save_options = save_options or FontSaveOptions()
        self.font_filter = font_filter or FontFinderFilter()
        self.task_name = task_name

    def run(self, *args: t.Any, **kwargs: t.Any) -> None:
        """
        Run method

        Parameters:
            *args (Any): Variable-length argument list.
            **kwargs (Any): Keyword arguments.

        Returns:
            None
        """
        fonts = self._get_valid_fonts()
        if fonts:
            self._process_fonts(fonts, *args, **kwargs)

    def _get_valid_fonts(self) -> t.Optional[t.List[Font]]:
        fonts = self._try_run(self._find_fonts)
        if self._try_run(self._validate_fonts, fonts):
            return fonts

    def _process_fonts(self, fonts: t.List[Font], *args: t.Any, **kwargs: t.Any) -> None:
        for font in fonts:
            with font:
                self._try_run(self.process_font, font, *args, **kwargs)

    @abstractmethod
    def process_font(self, font: Font, *args: t.Any, **kwargs: t.Any) -> None:
        """
        Process Font

        This method is used to process a font. Must be implemented by subclasses.
        """
        raise NotImplementedError

    @staticmethod
    def _try_run(command: t.Callable, *args: t.Any, **kwargs: t.Any) -> t.Optional[t.Any]:
        try:
            return command(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{type(e).__name__}: {e}")
            return None

    def _find_fonts(self) -> t.List[Font]:
        return FontFinder(
            self.input_path,
            recursive=self.recursive,
            font_options=self.font_init_options,
            font_filter=self.font_filter,
        ).find_fonts()

    def _validate_fonts(self, fonts: t.List[Font]) -> None:
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")

    def _log_current_font(self, font: Font) -> None:
        logger.info(f"{self.task_name} {font.file}")

    def _save_font(self, font: Font) -> None:
        output_file = font.make_out_file_name(
            output_dir=self.font_save_options.output_dir, overwrite=self.font_save_options.overwrite
        )
        font.save(output_file, reorder_tables=self.font_save_options.reorder_tables)
        logger.success(f"File saved to {output_file}")
