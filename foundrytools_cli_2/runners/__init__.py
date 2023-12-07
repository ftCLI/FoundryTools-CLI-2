from abc import ABCMeta, abstractmethod
from pathlib import Path
import typing as t

from foundrytools_cli_2.lib import Font, logger
from foundrytools_cli_2.lib.font_finder import (
    FontFinder,
    FontFinderFilter,
    FontFinderError,
    FontInitOptions,
)


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


class LoggerError(Exception):
    """Raised when there is an error with the logger"""


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


class BaseArgs:  # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """
    Base arguments for all runners
    """

    def __init__(
        self,
        input_path: Path,
        recursive: bool = False,
        lazy: t.Optional[bool] = None,
        recalc_timestamp: bool = False,
        recalc_bboxes: bool = True,
        output_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        reorder_tables: t.Optional[bool] = True,
    ) -> None:
        self.input_path = input_path
        self.recursive = recursive
        self.lazy = lazy
        self.recalc_timestamp = recalc_timestamp
        self.recalc_bboxes = recalc_bboxes
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.reorder_tables = reorder_tables


class BaseRunner(metaclass=ABCMeta):
    """Base class for all runners"""

    def __init__(
        self,
        input_path: Path,
        config: t.Optional[BaseArgs],
    ) -> None:
        self.input_path = input_path
        self.config = config or BaseArgs(input_path)
        self.font_filter = FontFinderFilter()
        self.task_name = "Processing"

    def run(self, *args: t.Any, **kwargs: t.Any) -> None:
        """
        Run method

        Parameters:
            *args (Any): Variable-length argument list.
            **kwargs (Any): Keyword arguments.

        Returns:
            None
        """
        try:
            fonts = self._find_fonts()
        except FontFinderError as e:
            logger.error(e)
            return

        try:
            self._validate_fonts(fonts)
        except NoFontsFoundError as e:
            logger.error(e)
            return

        for font in fonts:
            with font:
                log_success = self._try_run(self._log_current_font, font)
                if not log_success:
                    return

                # We assume the font has changed by default, the _process_font method should set
                # this to False if the font has not changed.
                font_has_changed = True

                self._try_run(self.process_font, font, *args, **kwargs)

                if not font_has_changed:
                    logger.skip(f"Skipped {font.file}")  # type: ignore
                    continue

                save_success = self._try_run(self._save_font, font)
                if not save_success:
                    return

    @abstractmethod
    def process_font(self, font: Font, *args: t.Any, **kwargs: t.Any) -> None:
        """
        Process Font

        This method is used to process a font. Must be implemented by subclasses.
        """
        raise NotImplementedError

    @staticmethod
    def _try_run(command: t.Callable, *args: t.Any, **kwargs: t.Any) -> t.Optional[t.Any]:
        """
        Run a given command and handle any exceptions that may occur.

        Parameters:
            command (Callable): The command to be executed.
            *args: Variable length argument list to be passed to the command.
            **kwargs: Arbitrary keyword arguments to be passed to the command.

        Returns:
            Any: The return value of the command if it is executed successfully, otherwise None.

        Raises:
            FontFinderError: If there is an error related to the font finder.
            NoFontsFoundError: If no fonts are found.
            LoggerError: If there is an error related to the logger.
            FontSaveError: If there is an error while saving the font.
            Exception: If there is an unhandled exception.
        """
        try:
            return command(*args, **kwargs)
        except (  # pylint: disable=broad-except
            FontFinderError,
            NoFontsFoundError,
            LoggerError,
            FontSaveError,
            Exception,
        ) as e:
            logger.error(e)
            return None

    def _find_fonts(self) -> t.List[Font]:
        """
        Find Fonts

        This method is used to find fonts according to the specified filters.

        Returns:
            A list of Font objects representing the found fonts.
        """
        font_filter = self.font_filter
        font_options = FontInitOptions()
        font_options.lazy = self.config.lazy
        font_options.recalc_timestamp = self.config.recalc_timestamp
        font_options.recalc_bboxes = self.config.recalc_bboxes
        return FontFinder(
            self.input_path,
            recursive=self.config.recursive,
            font_filter=font_filter,
        ).find_fonts()

    def _validate_fonts(self, fonts: t.List[Font]) -> None:
        """
        Validate Fonts

        Check if the given list of fonts is empty. If it is empty, raise a ValueError with the
        message "No fonts found".

        Parameters:
            fonts (List[Font]): A list of Font objects to validate.

        Returns:
            None: This method does not return anything.

        Raises:
            ValueError: If the list of fonts is empty.
        """
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")

    def _log_current_font(self, font: Font) -> None:
        """
        Logs the processing of the current font.

        :param font: The current font being processed.
        :return: None
        """
        try:
            logger.info(f"{self.task_name} {font.file}")
        except Exception as e:
            raise LoggerError("Error logging current font") from e

    def _save_font(self, font: Font) -> None:
        """
        Save the given font.

        Parameters:
            font (Font): The font object to save.

        Returns:
            None.
        """
        output_file = font.make_out_file_name(
            output_dir=self.config.output_dir, overwrite=self.config.overwrite
        )
        font.save(output_file, reorder_tables=self.config.reorder_tables)
        logger.success(f"File saved to {output_file}")
