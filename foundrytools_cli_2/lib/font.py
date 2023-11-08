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
        input_obj: t.Optional[t.Union[str, Path, BytesIO, TTFont]] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
        lazy: t.Optional[bool] = None,
    ) -> None:
        """
        Initialize a Font object.

        Args:
            input_obj: A path to a font file or a BytesIO object.
            recalc_bboxes: A boolean indicating whether to recalculate bounding boxes on save.
            recalc_timestamp: A boolean indicating whether to recalculate the modified timestamp
                on save.
            lazy: A boolean indicating whether to load the font lazily.
        """

        self._file_path = None
        self._file_obj = None
        self._tt_font = None

        if isinstance(input_obj, (str, Path)):
            self._file_path = Path(input_obj)
            self._tt_font = TTFont(input_obj, lazy=lazy)

        elif isinstance(input_obj, BytesIO):
            self._file_obj = BytesIO()
            self._tt_font = TTFont(input_obj, lazy=lazy)

        elif isinstance(input_obj, TTFont):
            self._tt_font = TTFont(input_obj, lazy=lazy)
            self._file_obj = BytesIO()
            self._tt_font.save(self._file_path)
            self._tt_font = TTFont(self._file_path, lazy=lazy)

        else:
            self._tt_font = TTFont()
            self._file_obj = BytesIO()

        self._tt_font.recalcBBoxes = recalc_bboxes
        self._tt_font.recalcTimestamp = recalc_timestamp

    @property
    def tt_font(self) -> TTFont:
        """
        Get the TTFont object.

        :return: The TTFont object.
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

    def get_output_file(
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

        # In some cases we may need to add a suffix to the file name. If the suffix is already
        # present, we remove it before adding it again.

        if self.file_path is None:
            raise ValueError("Cannot get output file for a BytesIO object.")

        out_dir = output_dir or self.file_path.parent
        file_name = self.file_path.stem
        extension = self.real_extension
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

    @property
    def file_name(self) -> t.Optional[str]:
        """
        Get the file name of the font. If the font is a BytesIO object, return None.

        :return: The file name of the font.
        """
        if self.file_path is None:
            return None
        return self.file_path.name

    @property
    def real_extension(self) -> str:
        """
        Get the real extension of the font. If the font is a web font, the extension will be
        determined by the font flavor. If the font is a SFNT font, the extension will be determined
        by the sfntVersion attribute.

        Returns:
            The extension of the font.
        """
        if self.tt_font.flavor == WOFF_FLAVOR:  # type: ignore
            return WOFF_EXTENSION
        if self.tt_font.flavor == WOFF2_FLAVOR:  # type: ignore
            return WOFF2_EXTENSION
        if self.tt_font.sfntVersion == PS_SFNT_VERSION:
            return OTF_EXTENSION
        if self.tt_font.sfntVersion == TT_SFNT_VERSION:
            return TTF_EXTENSION
        return ".unknown"

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
            raise ValueError(f"units_per_em must be in the range {MAX_UPM} to {MAX_UPM}.")

        if self.tt_font["head"].unitsPerEm == units_per_em:
            logger.warning(f"Font already has {units_per_em} units per em. No need to scale upem.")
            return

        scale_upem(self.tt_font, new_upem=units_per_em)

    def ps_subroutinize(self) -> None:
        """
        Subroutinize a PostScript font.
        """

        if not self.is_ps:
            raise NotImplementedError("Subroutinization is only supported for PostScript fonts.")

        # Workaround to subroutinize WOFF and WOFF2 fonts
        flavor = self.tt_font.flavor
        self.tt_font.flavor = None

        subroutinize(otf=self.tt_font)

        # Restore the original flavor
        self.tt_font.flavor = flavor

    def ps_desubroutinize(self) -> None:
        """
        Desubroutinize a PostScript font.
        """

        if not self.is_ps:
            raise NotImplementedError("Desubroutinization is only supported for PostScript fonts.")

        # Workaround to desubroutinize WOFF and WOFF2 fonts
        flavor = self.tt_font.flavor
        self.tt_font.flavor = None

        desubroutinize(otf=self.tt_font)

        # Restore the original flavor
        self.tt_font.flavor = flavor
