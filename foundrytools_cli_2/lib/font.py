from pathlib import Path
import typing as t

from dehinter.font import dehint
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.ttFont import TTFont

SFNT_POSTSCRIPT = "OTTO"
SFNT_TRUETYPE = "\0\1\0\0"
FLAVOR_WOFF = "woff"
FLAVOR_WOFF2 = "woff2"
FVAR_TABLE = "fvar"


class Font(TTFont):
    """
    The Font class is a subclass of TTFont and provides additional properties and methods.
    """

    def __init__(
        self,
        file: t.Optional[t.Union[str, Path]] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
        lazy: t.Optional[bool] = None,
    ) -> None:
        super().__init__(
            file=file,
            recalcBBoxes=recalc_bboxes,
            recalcTimestamp=recalc_timestamp,
            lazy=lazy,
        )

    @property
    def is_ps(self) -> bool:
        """
        Check if the font has PostScript outlines font.

        :return: True if the font is a PostScript font, False otherwise.
        """
        return self.sfntVersion == SFNT_POSTSCRIPT

    @property
    def is_tt(self):
        """
        Check if the font has TrueType outlines.

        :return: True if the font is a TrueType font, False otherwise.
        """
        return self.sfntVersion == SFNT_TRUETYPE

    @property
    def is_woff(self):
        """
        Check if the font is a WOFF font.

        :return: True if the font is a WOFF font, False otherwise.
        """
        return self.flavor == FLAVOR_WOFF

    @property
    def is_woff2(self):
        """
        Check if the font is a WOFF2 font.

        :return: True if the font is a WOFF2 font, False otherwise.
        """
        return self.flavor == FLAVOR_WOFF2

    def is_sfnt(self):
        """
        Check if the font is a SFNT font.

        :return: True if the font is a SFNT font, False otherwise.
        """
        return self.flavor is None

    @property
    def is_static(self):
        """
        Check if the font is a static font.

        :return: True if the font is a static font, False otherwise.
        """
        return self.get(FVAR_TABLE) is None

    @property
    def is_variable(self):
        """
        Check if the font is a variable font.

        :return: True if the font is a variable font, False otherwise.
        """
        return self.get(FVAR_TABLE) is not None

    def tt_decomponentize(self) -> None:
        """
        Decomponentize a TrueType font.
        """

        if not self.is_tt:
            raise NotImplementedError("Decomponentization is only supported for TrueType fonts.")

        glyph_set = self.getGlyphSet()
        glyf_table = self["glyf"]
        dr_pen = DecomposingRecordingPen(glyph_set)
        tt_pen = TTGlyphPen(None)

        for glyph_name in self.glyphOrder:
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

    def tt_scale_upm(self, units_per_em: int) -> None:
        """
        Scale the font's unitsPerEm value to the given value.

        Args:
            units_per_em (int): The new unitsPerEm value.
        """

        if not self.is_tt:
            raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

        if units_per_em not in range(16, 16385):
            raise ValueError("units_per_em must be in the range 16 to 16384.")

        if self["head"].unitsPerEm == units_per_em:
            raise ValueError(
                f"Font already has {units_per_em} units per em. No need to scale upem."
            )

        scale_upem(self, new_upem=units_per_em)

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
        file = Path(self.reader.file.name)
        out_dir = output_dir or file.parent
        file_name = file.stem
        extension = self.get_real_extension()
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

    def get_real_extension(self) -> str:
        """
        Get the real extension of the font. If the font is a web font, the extension will be
        determined by the font flavor. If the font is a SFNT font, the extension will be determined
        by the sfntVersion attribute.

        Returns:
            The extension of the font.
        """

        extension = ""
        if self.flavor is not None:
            extension = f".{self.flavor}"
        elif self.sfntVersion == SFNT_POSTSCRIPT:
            extension = ".otf"
        elif self.sfntVersion == SFNT_TRUETYPE:
            extension = ".ttf"
        return extension
