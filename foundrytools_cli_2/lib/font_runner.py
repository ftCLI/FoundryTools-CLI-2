import typing as t
from dataclasses import dataclass
from pathlib import Path

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_finder import FontFinder, FinderFilter, FinderOptions, FinderError
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer
from foundrytools_cli_2.lib.utils.misc import log_current_font, save_font


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


@dataclass
class SaveOptions:
    """
    A class that specifies how to save the font.
    """

    reorder_tables: t.Optional[bool] = True
    suffix: str = ""
    output_dir: t.Optional[Path] = None
    overwrite: bool = False


class FontRunner:
    """Base class for all runners"""

    def __init__(
        self,
        task: t.Callable,
        task_name: str = "Processing",
        auto_save: bool = True,
        **options: t.Any,
    ) -> None:  # pylint: disable=too-few-public-methods
        """
        Initialize a new instance of the class.

        Args:
            task (Callable): The task to be executed.
            task_name (str, optional): Name of the task. Defaults to "Processing".
            auto_save (bool, optional): Flag indicating whether to automatically save the task
                results. Defaults to True.
            **options (Any): Additional options for the task.
        """
        self.finder_options, self.save_options, self.callable_options = self._parse_options(options)
        self.font_filter = FinderFilter()
        self.auto_save = auto_save
        self.task = task
        self.task_name = task_name

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
                    text=f"{self.task_name} time: <cyan>{{:0.4f}} seconds</>",
                )
                timer.start()
                log_current_font(font)

                try:
                    self.task(font, **self.callable_options)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(f"{type(e).__name__}: {e}")
                    continue

                if not self.auto_save:
                    timer.stop()
                    print()  # Add a newline after each font
                    continue

                try:
                    save_font(font, **self.save_options.__dict__)
                except Exception as e:  # pylint: disable=broad-except
                    logger.exception(f"{type(e).__name__}: {e}")

                timer.stop()
                print()  # Add a newline after each font

    def _find_fonts(self) -> t.List[Font]:
        fonts = FontFinder(
            options=self.finder_options,
            font_filter=self.font_filter,
        ).find_fonts()

        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.finder_options.input_path}")
        return fonts

    def _parse_options(self, options: t.Dict[str, t.Any]) -> t.Tuple[FinderOptions, SaveOptions, t.Dict[str, t.Any]]:
        finder_options = FinderOptions()
        save_options = SaveOptions()
        callable_options = {}

        def _set_opts_attr(option_group, key, value):
            if hasattr(option_group, key):
                setattr(option_group, key, value)
                return True
            return False

        for k, v in options.items():
            if not _set_opts_attr(finder_options, k, v) and not _set_opts_attr(save_options, k, v):
                callable_options[k] = v

        return finder_options, save_options, callable_options
