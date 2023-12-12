import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.constants import FinderOptions, SaveOptions
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_finder import FontFinder, FinderError, FinderFilter
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.lib.utils.misc import log_current_font, save_font


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


class FontRunner:  # pylint: disable=too-few-public-methods
    """Base class for all runners"""

    def __init__(
        self,
        input_path: Path,
        task: t.Callable,
        **options: t.Dict[str, t.Any],
    ) -> None:
        """
        Initialize a new instance of the class.

        Args:
            task (Callable): The task to be executed.
            auto_save (bool, optional): Flag indicating whether to automatically save the task
                results. Defaults to True.
            **options (Dict[str, Any]): A dictionary containing various options.
        """
        self.input_path = input_path
        self._finder_options, self._save_options, self._callable_options = self._parse_options(
            options
        )
        self.filter = FinderFilter()
        self.auto_save = True
        self.task = task

    @Timer(logger=logger.opt(colors=True).info, text="Elapsed time <cyan>{:0.4f} seconds</>")
    def run(self) -> None:
        """
        Executes a task processing multiple fonts.
        """
        try:
            fonts = self._find_fonts()
        except (FinderError, NoFontsFoundError) as e:
            logger.error(e)
            return

        for font in fonts:
            with font:
                timer = Timer(
                    logger=logger.opt(colors=True).info,
                    text="Processing time: <cyan>{:0.4f} seconds</>",
                )
                timer.start()
                log_current_font(font)

                try:
                    self.task(font, **self._callable_options)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"{type(e).__name__}: {e}")
                    continue

                if not self.auto_save:
                    timer.stop()
                    print()  # Add a newline after each font
                    continue

                try:
                    save_font(font, **self._save_options.__dict__)
                except Exception as e:  # pylint: disable=broad-except
                    logger.exception(f"{type(e).__name__}: {e}")

                timer.stop()
                print()  # Add a newline after each font

    def _init_font_finder(self) -> FontFinder:
        return FontFinder(
            input_path=self.input_path,
            options=self._finder_options,
            filter_=self.filter,
        )

    def _find_fonts(self) -> t.List[Font]:
        finder = self._init_font_finder()
        fonts = finder.find_fonts()
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")
        return fonts

    @staticmethod
    def _parse_options(
        options: t.Dict[str, t.Any]
    ) -> t.Tuple[FinderOptions, SaveOptions, t.Dict[str, t.Any]]:
        """
        Parses options provided as a dictionary and returns three objects: FinderOptions,
        SaveOptions, and a dictionary of callable options.

        Parameters:
            options (Dict[str, Any]): A dictionary containing various options.

        Returns:
            Tuple[FinderOptions, SaveOptions, Dict[str, Any]]: A tuple containing three objects:
            FinderOptions, SaveOptions, and a dictionary of callable options.
        """
        finder_options = FinderOptions()
        save_options = SaveOptions()
        callable_options = {}

        def _set_opts_attr(
            option_group: t.Union[FinderOptions, SaveOptions], key: str, value: t.Any
        ) -> bool:
            """Set an attribute on an option group"""
            if hasattr(option_group, key):
                setattr(option_group, key, value)
                return True
            return False

        for k, v in options.items():
            if not _set_opts_attr(finder_options, k, v) and not _set_opts_attr(save_options, k, v):
                callable_options[k] = v

        return finder_options, save_options, callable_options
