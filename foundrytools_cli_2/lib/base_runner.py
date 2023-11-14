import abc
from pathlib import Path
from typing import Optional, Dict, List

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger
from foundrytools_cli_2.lib.timer import Timer


class NoFontsFoundError(Exception):
    """
    An exception raised when no fonts are found.
    """


class BaseRunner(abc.ABC):
    """
    A base class for runners.
    """

    def __init__(
        self,
        fonts: List[Font],
        output_dir: Optional[Path] = None,
        overwrite: bool = False,
        reorder_tables: bool = False,
        **kwargs: Dict,
    ) -> None:
        """
        Initialize the runner.
        """
        self.fonts = fonts
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.reorder_tables = reorder_tables
        self._kwargs = kwargs

    @Timer(text="\nElapsed time: {0:.3f}s")
    def run(self) -> None:
        """
        Run the runner. This method must be overridden by subclasses.
        """
        self._validate_fonts()
        for font in self.fonts:
            try:
                logger.info(f"Processing {font.file}")
                self._process_font(font, **self._kwargs)
                self._save_font(font)
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(e)

    def _validate_fonts(self) -> None:
        """
        Validate the fonts.
        """
        if not self.fonts:
            raise NoFontsFoundError("No valid fonts found")

    @abc.abstractmethod
    def _process_font(self, font: Font, **kwargs: Dict) -> None:
        """
        Run the runner. This method must be overridden by subclasses.
        """
        raise NotImplementedError

    def _get_out_file_name(self, font: Font) -> Path:
        """
        Get the output file name.
        """
        return font.make_out_file_name(
            output_dir=self.output_dir,
            overwrite=self.overwrite,
        )

    def _save_font(self, font: Font) -> None:
        """
        Save the font.
        """
        out_file = self._get_out_file_name(font)
        font.save(out_file, reorder_tables=self.reorder_tables)
        logger.success(f"Saved {out_file}")
