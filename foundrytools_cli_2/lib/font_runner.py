import typing as t
from dataclasses import dataclass
from pathlib import Path

from foundrytools_cli_2.lib import Font, logger, Timer, FontFinder
from foundrytools_cli_2.lib.font_finder import FinderFilter, FinderOptions, FinderError


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
    output_dir: t.Optional[Path] = None
    overwrite: bool = False


class FontRunner:
    """Base class for all runners"""

    def __init__(self, task: t.Callable, task_name: str = "Processing", **options: t.Any) -> None:
        self.options = options
        self.finder_options, self.save_options, self.callable_options = self._parse_options()
        self.font_filter = FinderFilter()
        self.task = task
        self.task_name = task_name

    @Timer(logger=logger.opt(colors=True).info, text=f"Elapsed time <cyan>{{:0.4f}} seconds</>")
    def run(self) -> None:
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

                self._log_current_font(font)

                try:
                    self.task(font, **self.callable_options)
                except Exception as e:
                    logger.error(f"{type(e).__name__}: {e}")
                    continue

                try:
                    self._save_font(font)
                except Exception as e:
                    logger.error(f"{type(e).__name__}: {e}")
                    continue
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

    def _log_current_font(self, font: Font) -> None:
        if hasattr(font, "file"):
            logger.info(f"{self.task_name} {font.file}")
        elif hasattr(font, "bytesio"):
            logger.info(f"{self.task_name} {font.bytesio}")
        else:
            logger.info(f"{self.task_name} {font}")

    def _save_font(self, font: Font, suffix: str = "") -> None:
        output_file = font.make_out_file_name(
            output_dir=self.save_options.output_dir, overwrite=self.save_options.overwrite
        )
        font.save(output_file, reorder_tables=self.save_options.reorder_tables)
        logger.success(f"File saved to {output_file}")

    def _parse_options(self) -> t.Tuple[FinderOptions, SaveOptions, t.Dict[str, t.Any]]:
        font_options = FinderOptions()
        path_options = SaveOptions()
        run_options = {}

        def _set_opts_attr(option_group, key, value):
            if hasattr(option_group, key):
                setattr(option_group, key, value)
                return True
            return False

        for k, v in self.options.items():
            if not _set_opts_attr(font_options, k, v) and not _set_opts_attr(path_options, k, v):
                run_options[k] = v

        return font_options, path_options, run_options
