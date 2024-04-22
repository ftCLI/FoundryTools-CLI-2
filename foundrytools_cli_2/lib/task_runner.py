import typing as t
from pathlib import Path

from foundrytools_cli_2.lib.constants import FinderOptions, SaveOptions
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font_finder import FinderError, FinderFilter, FontFinder
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer


class FontSaveError(Exception):
    """Raised when there is an error saving a font"""


class NoFontsFoundError(Exception):
    """Raised when no fonts are found by the FontFinder"""


class TaskRunnerConfig:  # pylint: disable=too-few-public-methods
    """
    Handle options for TaskRunner.
    """

    def __init__(self, options: t.Dict[str, t.Any], task: t.Callable):
        self.filter = FinderFilter()
        self.finder_options = FinderOptions()
        self.save_options = SaveOptions()
        self.task_options: t.Dict[str, t.Any] = {}
        self.task = task
        self._parse_options(options)

    def _parse_options(self, options: t.Dict[str, t.Any]) -> None:
        """
        Parses and set options provided as a dictionary for: FinderOptions,
        SaveOptions, and specific task options.
        """
        for k, v in options.items():
            self._set_opts_attr(self.finder_options, k, v)
            self._set_opts_attr(self.save_options, k, v)
            if "kwargs" in self.task.__annotations__:  # type: ignore
                self.task_options.update(
                    {
                        k: v
                        for k, v in options.items()
                        if k not in self.finder_options.__dict__.items()
                        and k not in self.save_options.__dict__.items()
                    }
                )
            else:
                if k != "return" and k in self.task.__annotations__:  # type: ignore
                    self.task_options[k] = v

    @staticmethod
    def _set_opts_attr(
        option_group: t.Union[FinderOptions, SaveOptions], key: str, value: t.Any
    ) -> bool:
        """
        Set an attribute on an option group if the attribute exists.
        """
        if hasattr(option_group, key):
            setattr(option_group, key, value)
            return True
        return False


class TaskRunner:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    A class for running tasks on multiple fonts.

    Attributes:
        input_path (Path): The input path to search for fonts.
        task (Callable): The task to be executed.
        filter (FinderFilter): The filter to apply to the FontFinder.
        save_if_modified (bool): Whether to save the font if it has been modified. Set to False
            when the saving process is handled by the task itself. Defaults to True.
        force_modified (bool): Whether to force the font to be saved even if it has not been
            modified. Set to True when it's not possible to determine if the font has been modified,
            or when it's too expensive to check. Defaults to False.
        options (TaskRunnerConfig): A configuration object containing FinderOptions, SaveOptions,
            and specific task options.
    """

    def __init__(
        self,
        input_path: Path,
        task: t.Callable,
        **options: t.Dict[str, t.Any],
    ) -> None:
        """
        Initialize a new instance of the class.

        Args:
            input_path (Path): The input path to search for fonts.
            task (Callable): The task to be executed.
            **options (Dict[str, Any]): A dictionary containing the options to be parsed.
        """
        self.input_path = input_path
        self.task = task
        self.filter = FinderFilter()
        self.save_if_modified = True
        self.force_modified = False
        self.options = TaskRunnerConfig(options=options, task=task)

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
            self._process_font(font, timer=timer)

    def _find_fonts(self) -> t.List[Font]:
        finder = FontFinder(
            input_path=self.input_path, options=self.options.finder_options, filter_=self.filter
        )
        fonts = finder.find_fonts()
        if not fonts:
            raise NoFontsFoundError(f"No fonts found in {self.input_path}")
        return fonts

    def _process_font(self, font: Font, timer: Timer) -> None:
        with font:
            timer.start()
            logger.info(f"Processing file {font.file}")
            self._execute_task(font)
            self._save_or_skip(font)
            timer.stop()
            print()  # add a newline after each font

    def _execute_task(self, font: Font) -> None:
        try:
            self.task(font, **self.options.task_options)
        except Exception as e:  # pylint: disable=broad-except
            self._log_error(e)
            return

    def _save_or_skip(self, font: Font) -> None:
        if not self._font_should_be_saved(font):
            if self.save_if_modified:
                logger.skip("No changes made")  # type: ignore
        else:
            self._save_font_to_file(font)

    def _font_should_be_saved(self, font: Font) -> bool:
        return (self.save_if_modified and font.modified) or self.force_modified

    def _save_font_to_file(self, font: Font) -> None:
        try:
            out_file = self._get_out_file_name(font)
            font.save(out_file, reorder_tables=self.options.save_options.reorder_tables)
            logger.success(f"File saved to {out_file}")
        except Exception as e:  # pylint: disable=broad-except
            self._log_error(e)

    def _get_out_file_name(self, font: Font) -> Path:
        return font.make_out_file_name(
            output_dir=self.options.save_options.output_dir,
            extension=font.get_real_extension(),
            overwrite=self.options.save_options.overwrite,
            suffix=self.options.save_options.suffix,
        )

    @staticmethod
    def _log_error(e: Exception) -> None:
        logger.error(f"{type(e).__name__}: {e}")
