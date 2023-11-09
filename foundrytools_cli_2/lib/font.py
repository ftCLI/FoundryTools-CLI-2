from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
import typing as t

from cffsubr import subroutinize, desubroutinize
from dehinter.font import dehint
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.ttFont import TTFont

from foundrytools_cli_2.lib.constants import (
    WOFF_FLAVOR,
    WOFF2_FLAVOR,
    WOFF_EXTENSION,
    WOFF2_EXTENSION,
    OTF_EXTENSION,
    TTF_EXTENSION,
    PS_SFNT_VERSION,
    TT_SFNT_VERSION,
    FVAR_TABLE_TAG,
    GLYF_TABLE_TAG,
    MIN_UPM,
    MAX_UPM,
)
from foundrytools_cli_2.lib.logger import logger


class Font:
    """
    The Font class is a subclass of TTFont and provides additional properties and methods.
    """

    def __init__(
        self,
        font_source: t.Optional[t.Union[str, Path, BytesIO, TTFont]] = None,
        lazy: t.Optional[bool] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
    ) -> None:
        """
        Initialize a Font object.

        Args:
            font_source: A path to a font file or a BytesIO object.
            lazy: A boolean indicating whether to load the font lazily.
            recalc_bboxes: A boolean indicating whether to recalculate font's bounding boxes on
                save.
            recalc_timestamp: A boolean indicating whether to recalculate the font's modified
            timestamp on save.
        """

        self._file_path: t.Optional[Path]
        self._file_object = t.Optional[BytesIO]
        self._tt_font = None or TTFont()

        self._initialize_file(font_source, lazy)
        self._initialize_tt_font(recalc_bboxes, recalc_timestamp)

    def _initialize_file(
        self,
        input_obj: t.Optional[t.Union[str, Path, BytesIO, TTFont]] = None,
        lazy: t.Optional[bool] = None,
    ) -> None:
        if isinstance(input_obj, (str, Path)):
            self._initialize_file_from_path(input_obj, lazy)
        elif isinstance(input_obj, BytesIO):
            self._initialize_file_from_bytesio(input_obj, lazy)
        elif isinstance(input_obj, TTFont):
            self._initialize_file_from_ttfont(input_obj)
        else:
            self._initialize_empty_file()

    def _initialize_file_from_path(self, path: t.Union[str, Path], lazy: t.Optional[bool]) -> None:
        self._file_path = Path(path)
        self._tt_font = TTFont(path, lazy=lazy)

    def _initialize_file_from_bytesio(self, bytesio: BytesIO, lazy: t.Optional[bool]) -> None:
        self._file_object = bytesio
        self._tt_font = TTFont(bytesio, lazy=lazy)

    def _initialize_file_from_ttfont(self, ttfont: TTFont) -> None:
        self._file_object = BytesIO()
        self._tt_font = ttfont

    def _initialize_empty_file(self) -> None:
        self._tt_font = TTFont()
        self._file_object = BytesIO()

    def _initialize_tt_font(self, recalc_bboxes: bool, recalc_timestamp: bool) -> None:
        self._tt_font.recalcBBoxes = recalc_bboxes
        self._tt_font.recalcTimestamp = recalc_timestamp

    def __enter__(self) -> "Font":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self._tt_font.close()

    @property
    def tt_font(self) -> TTFont:
        """
        Get the underlying TTFont object.
        """
        return self._tt_font

    @property
    def file_path(self) -> t.Optional[Path]:
        """
        Get the file path of the font.

        :return: The file path of the font.
        """
        return self._file_path

    @property
    def is_ps(self) -> bool:
        """
        Check if the font has PostScript outlines font.

        :return: True if the font is a PostScript font, False otherwise.
        """
        return self.tt_font.sfntVersion == PS_SFNT_VERSION

    @property
    def is_tt(self) -> bool:
        """
        Check if the font has TrueType outlines.

        :return: True if the font is a TrueType font, False otherwise.
        """
        return self.tt_font.sfntVersion == TT_SFNT_VERSION

    @property
    def is_woff(self) -> bool:
        """
        Check if the font is a WOFF font.

        :return: True if the font is a WOFF font, False otherwise.
        """
        return self.tt_font.flavor == WOFF_FLAVOR

    @property
    def is_woff2(self) -> bool:
        """
        Check if the font is a WOFF2 font.

        :return: True if the font is a WOFF2 font, False otherwise.
        """
        return self.tt_font.flavor == WOFF2_FLAVOR

    @property
    def is_sfnt(self) -> bool:
        """
        Check if the font is a SFNT font.

        :return: True if the font is a SFNT font, False otherwise.
        """
        return self.tt_font.flavor is None

    @property
    def is_static(self) -> bool:
        """
        Check if the font is a static font.

        :return: True if the font is a static font, False otherwise.
        """
        return self.tt_font.get(FVAR_TABLE_TAG) is None

    @property
    def is_variable(self) -> bool:
        """
        Check if the font is a variable font.

        :return: True if the font is a variable font, False otherwise.
        """
        return self.tt_font.get(FVAR_TABLE_TAG) is not None

    @property
    def real_extension(self) -> str:
        """
        Get the real extension of the font. If the font is a web font, the extension will be
        determined by the font flavor. If the font is a SFNT font, the extension will be determined
        by the sfntVersion attribute.

        Returns:
            The extension of the font.
        """
        if self.is_woff:
            return WOFF_EXTENSION
        if self.is_woff2:
            return WOFF2_EXTENSION
        if self.is_ps:
            return OTF_EXTENSION
        if self.is_tt:
            return TTF_EXTENSION
        return self.tt_font.sfntVersion

    def save_to_file(
        self,
        output_path: t.Optional[Path] = None,
        out_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        suffix: str = "",
    ) -> None:
        """
        Save the font to a file.

        Args:
            output_path: The output path. If not specified, the font will be saved to the same
                location as the input file.
            out_dir: The output directory. If not specified, the font will be saved to the same
                directory as the input file.
            overwrite: A boolean indicating whether to overwrite existing files.
            suffix: An optional suffix to append to the file name.
        """
        if self.file_path is None:
            self.tt_font.save(self._file_object)
            return

        output_path = output_path or self.get_output_path(
            output_dir=out_dir, overwrite=overwrite, suffix=suffix
        )
        self.tt_font.save(output_path)

    def save_to_bytesio(self) -> BytesIO:
        """
        Save the font to a BytesIO object.

        Returns:
            A BytesIO object.
        """
        buf = BytesIO()
        self.tt_font.save(buf)
        buf.seek(0)
        return buf

    def get_output_path(
        self,
        output_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        suffix: str = "",
    ) -> Path:
        """
        Get output file for a Font object. If ``output_dir`` is not specified, the output file will
        be saved in the same directory as the input file. It the output file already exists and
        ``overwrite`` is False, file name will be incremented by adding a number preceded by '#'
        before the extension until a non-existing file name is found.

        Args:
            output_dir: Path to the output directory.
            overwrite: A boolean indicating whether to overwrite existing files.
            suffix: An optional suffix to append to the file name.

        Returns:
            A Path object pointing to the output file.
        """

        if self.file_path is None:
            raise ValueError("Cannot get output file for a BytesIO object.")

        # We check elsewhere if the output directory is writable, no need to check it here.
        out_dir = output_dir or self.file_path.parent
        file_name = self.file_path.stem
        extension = self.real_extension

        # In some cases we may need to add a suffix to the file name. If the suffix is already
        # present, we remove it before adding it again.
        if suffix != "":
            file_name = file_name.replace(suffix, "")

        out_file = Path(
            makeOutputFileName(
                file_name,
                extension=extension,
                suffix=suffix,
                outputDir=out_dir,
                overWrite=overwrite,
            )
        )
        return out_file

    def get_advance_widths(self) -> t.Dict[str, int]:
        """
        Get advance widths from a font.

        :return: Advance widths.
        """
        advance_widths = {}
        glyph_set = self.tt_font.getGlyphSet()

        for k, v in glyph_set.items():
            advance_widths[k] = v.width

        return advance_widths

    def tt_decomponentize(self) -> None:
        """
        Decomponentize a TrueType font.
        """

        if not self.is_tt:
            raise NotImplementedError("Decomponentization is only supported for TrueType fonts.")

        glyph_set = self.tt_font.getGlyphSet()
        glyf_table = self.tt_font[GLYF_TABLE_TAG]
        dr_pen = DecomposingRecordingPen(glyph_set)
        tt_pen = TTGlyphPen(None)

        for glyph_name in self.tt_font.glyphOrder:
            glyph = glyf_table[glyph_name]
            if not glyph.isComposite():
                continue
            dr_pen.value = []
            tt_pen.init()
            glyph.draw(dr_pen, glyf_table)
            dr_pen.replay(tt_pen)
            glyf_table[glyph_name] = tt_pen.glyph()

    def tt_remove_hints(self) -> None:
        """
        Remove hints from a TrueType font.
        """

        if not self.is_tt:
            raise NotImplementedError("Only TrueType fonts are supported.")

        dehint(self)

    def tt_scale_upem(self, units_per_em: int) -> None:
        """
        Scale the font's unitsPerEm value to the given value.

        Args:
            units_per_em (int): The new unitsPerEm value.
        """

        if not self.is_tt:
            raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

        if units_per_em not in range(MIN_UPM, MAX_UPM + 1):
            logger.error(f"units_per_em must be in the range {MAX_UPM} to {MAX_UPM}.")
            return

        if self.tt_font["head"].unitsPerEm == units_per_em:
            logger.warning(f"Font already has {units_per_em} units per em. No need to scale upem.")
            return

        scale_upem(self.tt_font, new_upem=units_per_em)

    @contextmanager
    def _restore_flavor(self) -> t.Iterator[None]:
        """
        This is a workaround to support subroutinization and desubroutinization for WOFF and WOFF2
        fonts. cffsubr requires the font flavor to be set to None. This context manager is used to
        temporarily set the font flavor to None and restore it after subroutinization or
        desubroutinization.
        """
        original_flavor = self.tt_font.flavor
        self.tt_font.flavor = None
        try:
            yield
        finally:
            self.tt_font.flavor = original_flavor

    def ps_subroutinize(self) -> None:
        """
        Subroutinize a PostScript font.
        """

        if not self.is_ps:
            raise NotImplementedError("Subroutinization is only supported for PostScript fonts.")

        # Using compreffor here requires to save the font to a buffer first
        # from io import BytesIO
        # with BytesIO() as buf:
        #     buf = BytesIO()
        #     otf.save(buf)
        #     buf.seek(0)
        #     otf = Font(buf)
        #     compress(otf)
        with self._restore_flavor():
            subroutinize(otf=self.tt_font)

    def ps_desubroutinize(self) -> None:
        """
        Desubroutinize a PostScript font.
        """

        if not self.is_ps:
            raise NotImplementedError("Desubroutinization is only supported for PostScript fonts.")

        with self._restore_flavor():
            desubroutinize(otf=self.tt_font)
