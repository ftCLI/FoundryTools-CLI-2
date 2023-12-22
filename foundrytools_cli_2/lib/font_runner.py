import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.constants import FinderOptions, SaveOptions
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_finder import FontFinder, FinderError, FinderFilter
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer


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
        self.task = task
        self.filter = FinderFilter()
        self.auto_save = True
        self._finder_options, self._save_options, self._callable_options = self._parse_options(
            options
        )

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

        timer = Timer(
            logger=logger.opt(colors=True).info,
            text="Processing time: <cyan>{:0.4f} seconds</>",
        )

        for font in fonts:
            with font:
                timer.start()
                out_file = self._get_out_file_name(font)

                try:
                    self._log_current_file(font)
                    self.task(font, **self._callable_options)
                except Exception as e:  # pylint: disable=broad-except
                    timer.stop()
                    logger.exception(f"{type(e).__name__}: {e}")
                    continue

                if not self.auto_save:
                    timer.stop()
                    print()  # Add a newline after each font
                    continue

                try:
                    font.save(out_file, reorder_tables=self._save_options.reorder_tables)
                    logger.success(f"File saved to {out_file}")
                except Exception as e:  # pylint: disable=broad-except
                    timer.stop()
                    logger.exception(f"{type(e).__name__}: {e}")

                timer.stop()
                print()  # Add a newline after each font

    def _find_fonts(self) -> t.List[Font]:
        finder = FontFinder(
            input_path=self.input_path, options=self._finder_options, filter_=self.filter
        )
        fonts = finder.find_fonts()
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")
        return fonts

    def _parse_options(
        self, options: t.Dict[str, t.Any]
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
            _set_opts_attr(finder_options, k, v)
            _set_opts_attr(save_options, k, v)
            if k != "return" and k in self.task.__annotations__:  # type: ignore
                callable_options[k] = v

        return finder_options, save_options, callable_options

    @staticmethod
    def _log_current_file(font: Font) -> None:
        """
        Logs the current font information.

        Parameters:
            font (Font): The font to log.
        """
        if font.file is None:
            raise ValueError("Font file is None")
        logger.info(f"Processing file {font.file}")

    def _get_out_file_name(self, font: Font) -> Path:
        """
        Returns the output file name for a given font.

        Parameters:
            font (Font): The font to get the output file name for.

        Returns:
            str: The output file name.
        """
        return font.make_out_file_name(
            output_dir=self._save_options.output_dir,
            extension=font.get_real_extension(),
            overwrite=self._save_options.overwrite,
            suffix=self._save_options.suffix,
        )
