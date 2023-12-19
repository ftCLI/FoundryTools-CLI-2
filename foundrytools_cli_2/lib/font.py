import typing as t
from io import BytesIO
from pathlib import Path

from dehinter.font import dehint
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.tables._f_v_a_r import NamedInstance, Axis

from foundrytools_cli_2.lib.otf.hinting_stems import recalc_stems
from foundrytools_cli_2.lib.otf.hinting_zones import recalc_zones
from foundrytools_cli_2.lib.otf.t2_charstrings import fix_charstrings, quadratics_to_cubics
from foundrytools_cli_2.lib.otf.font_builder import build_otf
from foundrytools_cli_2.lib.otf.afdko_tools import cff_subr, cff_desubr
from foundrytools_cli_2.lib.ttf.from_otf import build_ttf

PS_SFNT_VERSION = "OTTO"
TT_SFNT_VERSION = "\0\1\0\0"
WOFF_FLAVOR = "woff"
WOFF2_FLAVOR = "woff2"
OTF_EXTENSION = ".otf"
TTF_EXTENSION = ".ttf"
WOFF_EXTENSION = ".woff"
WOFF2_EXTENSION = ".woff2"
FVAR_TABLE_TAG = "fvar"
GLYF_TABLE_TAG = "glyf"
MIN_UPM = 16
MAX_UPM = 16384


class Font:  # pylint: disable=too-many-public-methods
    """
    The ``Font`` class adds additional properties and methods to the ``fontTools.ttLib.TTFont``
    class.
    """

    def __init__(
        self,
        source: t.Union[str, Path, BytesIO, TTFont],
        lazy: t.Optional[bool] = None,
        recalc_bboxes: bool = True,
        recalc_timestamp: bool = False,
    ) -> None:
        """
        Initialize a Font object.

        Args:
            source: A path to a font file, a BytesIO object or a TTFont object.
            lazy (bool): If lazy is set to True, many data structures are loaded lazily, upon access
                only. If it is set to False, many data structures are loaded immediately. The
                default is ``lazy=None`` which is somewhere in between.
            recalc_bboxes (bool): If true (the default), recalculates ``glyf``, ``CFF ``, ``head``
                bounding box values and ``hhea``/``vhea`` min/max values on save. Also compiles the
                glyphs on importing, which saves memory consumption and time.
            recalc_timestamp (bool): If true, sets the ``modified`` timestamp in the ``head`` table
                on save. Default is False.
        """

        self._file: t.Optional[Path] = None
        self._bytesio: t.Optional[BytesIO] = None
        self._ttfont: t.Optional[TTFont] = None

        if isinstance(source, (str, Path)):
            self._init_from_file(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, BytesIO):
            self._init_from_bytesio(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, TTFont):
            self._init_from_tt_font(source, lazy, recalc_bboxes, recalc_timestamp)
        else:
            raise ValueError(
                f"Invalid source type {type(source)}. Expected str, Path, BytesIO, or TTFont."
            )

    def _init_from_file(
        self,
        path: t.Union[str, Path],
        lazy: t.Optional[bool],
        recalc_bboxes: bool,
        recalc_timestamp: bool,
    ) -> None:
        self._file = Path(path).resolve()
        self._ttfont = TTFont(
            path, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )

    def _init_from_bytesio(
        self, bytesio: BytesIO, lazy: t.Optional[bool], recalc_bboxes: bool, recalc_timestamp: bool
    ) -> None:
        self._bytesio = bytesio
        self._ttfont = TTFont(
            bytesio, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )
        bytesio.close()

    def _init_from_tt_font(
        self, ttfont: TTFont, lazy: t.Optional[bool], recalc_bboxes: bool, recalc_timestamp: bool
    ) -> None:
        self._bytesio = BytesIO()
        ttfont.save(self._bytesio, reorderTables=False)
        self._bytesio.seek(0)
        self._ttfont = TTFont(
            self._bytesio, lazy=lazy, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp
        )

    def __enter__(self) -> "Font":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self.close()

    def __repr__(self) -> str:
        return f"<Font file={self.file}, bytesio={self.bytesio}, ttfont={self.ttfont}>"

    @property
    def file(self) -> t.Optional[Path]:
        """
        Get the file path of the font.

        :return: The file path of the font.
        """
        return self._file

    @property
    def bytesio(self) -> t.Optional[BytesIO]:
        """
        Get the BytesIO object of the font.

        :return: The BytesIO object of the font.
        """
        return self._bytesio

    @property
    def ttfont(self) -> TTFont:
        """
        Get the underlying TTFont object.
        """
        return self._ttfont

    @property
    def is_ps(self) -> bool:
        """
        Check if the font has PostScript outlines font.

        :return: True if the font is a PostScript font, False otherwise.
        """
        return self.ttfont.sfntVersion == PS_SFNT_VERSION

    @property
    def is_tt(self) -> bool:
        """
        Check if the font has TrueType outlines.

        :return: True if the font is a TrueType font, False otherwise.
        """
        return self.ttfont.sfntVersion == TT_SFNT_VERSION

    @property
    def is_woff(self) -> bool:
        """
        Check if the font is a WOFF font.

        :return: True if the font is a WOFF font, False otherwise.
        """
        return self.ttfont.flavor == WOFF_FLAVOR

    @property
    def is_woff2(self) -> bool:
        """
        Check if the font is a WOFF2 font.

        :return: True if the font is a WOFF2 font, False otherwise.
        """
        return self.ttfont.flavor == WOFF2_FLAVOR

    @property
    def is_sfnt(self) -> bool:
        """
        Check if the font is a SFNT font.

        :return: True if the font is a SFNT font, False otherwise.
        """
        return self.ttfont.flavor is None

    @property
    def is_static(self) -> bool:
        """
        Check if the font is a static font.

        :return: True if the font is a static font, False otherwise.
        """
        return self.ttfont.get(FVAR_TABLE_TAG) is None

    @property
    def is_variable(self) -> bool:
        """
        Check if the font is a variable font.

        :return: True if the font is a variable font, False otherwise.
        """
        return self.ttfont.get(FVAR_TABLE_TAG) is not None

    def save(
        self,
        file: t.Union[str, Path, BytesIO],
        reorder_tables: t.Optional[bool] = True,
    ) -> None:
        """
        Save the font to a file.

        Args:
            file: The file path to save the font to.
            reorder_tables: If true (the default), reorder the tables, sorting them by tag
                (recommended by the OpenType specification). If false, retain the original font
                order. If None, reorder by table dependency (fastest).
        """
        self.ttfont.save(file, reorderTables=reorder_tables)

    def close(self) -> None:
        """
        Close the underlying TTFont object.
        """
        self.ttfont.close()

    def get_real_extension(self) -> str:
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
        return self.ttfont.sfntVersion

    def make_out_file_name(
        self,
        output_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        extension: t.Optional[str] = None,
        suffix: str = "",
    ) -> Path:
        """
        Get output file for a Font object. If ``output_dir`` is not specified, the output file will
        be saved in the same directory as the input file. It the output file already exists and
        ``overwrite`` is False, file name will be incremented by adding a number preceded by '#'
        before the extension until a non-existing file name is found. If ``suffix`` is specified,
        it will be appended to the file name. If the suffix is already present, it will be removed
        before adding it again.

        Args:
            output_dir: Path to the output directory.
            overwrite: A boolean indicating whether to overwrite existing files.
            extension: An optional extension to use for the output file. If not specified, the
                extension will be determined by the font type.
            suffix: An optional suffix to append to the file name.

        Returns:
            A Path object pointing to the output file.
        """

        if self.file is None:
            raise ValueError("Cannot get output file for a BytesIO object.")

        # We check elsewhere if the output directory is writable, no need to check it here.
        out_dir = output_dir or self.file.parent
        extension = extension or self.get_real_extension()
        file_name = self.file.stem

        # Clean up the file name by removing the extensions used as file name suffix as added by
        # possible previous conversions.
        if suffix != "":
            for ext in [OTF_EXTENSION, TTF_EXTENSION, WOFF2_EXTENSION, WOFF_EXTENSION]:
                file_name = file_name.replace(ext, "")

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

    def get_axes(self) -> t.List[Axis]:
        """
        Get axes from a variable font.

        :return: Axes.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        return [axis for axis in self.ttfont[FVAR_TABLE_TAG].axes if axis.flags == 0]

    def get_instances(self) -> t.List[NamedInstance]:
        """
        Get named instances from a variable font.

        :return: Named instances.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        return self.ttfont[FVAR_TABLE_TAG].instances

    def get_glyph_bounds(self, glyph_name: str) -> t.Dict[str, float]:
        """
        Get the bounds of a glyph.

        :param glyph_name: The name of the glyph.
        :return: The bounds of the glyph.
        """
        glyph_set = self.ttfont.getGlyphSet()
        if glyph_name not in glyph_set:
            raise ValueError(f"Glyph '{glyph_name}' does not exist in the font.")

        bounds_pen = BoundsPen(glyphSet=glyph_set)

        glyph_set[glyph_name].draw(bounds_pen)
        bounds = {
            "xMin": bounds_pen.bounds[0],
            "yMin": bounds_pen.bounds[1],
            "xMax": bounds_pen.bounds[2],
            "yMax": bounds_pen.bounds[3],
        }

        return bounds

    def recalc_x_height(self) -> float:
        """
        Recalculate the x-height of the font.
        """
        return self.get_glyph_bounds("x")["yMax"]

    def recalc_cap_height(self) -> float:
        """
        Recalculate the cap height of the font.
        """
        return self.get_glyph_bounds("H")["yMax"]

    def get_x_height(self) -> int:
        """
        Get the x-height of the font.

        :return: The x-height of the font.
        """
        os2 = self.ttfont["OS/2"]
        if os2.version < 2:
            raise ValueError(
                f"sxHeight is defined only in OS/2 version 2 and up. "
                f"Current version is {os2.version}."
            )

        return self.ttfont["OS/2"].sxHeight

    def get_cap_height(self) -> int:
        """
        Get the cap height of the font.

        :return: The cap height of the font.
        """
        os2 = self.ttfont["OS/2"]
        if os2.version < 2:
            raise ValueError(
                f"sCapHeight is defined only in OS/2 version 2 and up. "
                f"Current version is {os2.version}."
            )

        return self.ttfont["OS/2"].sCapHeight

    def set_x_height(self, x_height: float) -> None:
        """
        Set the x-height of the font.

        :param x_height: The x-height of the font.
        """
        os2 = self.ttfont["OS/2"]
        if os2.version < 2:
            raise ValueError(
                f"sxHeight is defined only in OS/2 version 2 and up. "
                f"Current version is {os2.version}."
            )

        setattr(os2, "sxHeight", x_height)

    def set_cap_height(self, cap_height: float) -> None:
        """
        Set the cap height of the font.

        :param cap_height: The cap height of the font.
        """
        os2 = self.ttfont["OS/2"]
        if os2.version < 2:
            raise ValueError(
                f"sCapHeight is defined only in OS/2 version 2 and up. "
                f"Current version is {os2.version}."
            )

        setattr(os2, "sCapHeight", cap_height)

    def to_woff(self) -> None:
        """
        Convert a font to WOFF.
        """
        if self.is_woff:
            raise ValueError("Font is already a WOFF font.")

        self.ttfont.flavor = WOFF_FLAVOR

    def to_woff2(self) -> None:
        """
        Convert a font to WOFF2.
        """
        if self.is_woff2:
            raise ValueError("Font is already a WOFF2 font.")

        self.ttfont.flavor = WOFF2_FLAVOR

    def to_ttf(self, max_err: float = 1.0, reverse_direction: bool = True) -> None:
        """
        Convert a font to TrueType.
        """
        if self.is_tt:
            raise ValueError("Font is already a TrueType font.")
        if self.is_variable:
            raise NotImplementedError("Conversion to TrueType is not supported for variable fonts.")

        build_ttf(font=self.ttfont, max_err=max_err, reverse_direction=reverse_direction)

    def to_otf(self, tolerance: float = 1.0) -> None:
        """
        Convert a font to PostScript.
        """
        if self.is_ps:
            raise ValueError("Font is already a PostScript font.")
        if self.is_variable:
            raise NotImplementedError(
                "Conversion to PostScript is not supported for variable fonts."
            )

        charstrings = quadratics_to_cubics(font=self.ttfont, tolerance=tolerance)
        build_otf(font=self.ttfont, charstrings_dict=charstrings)

    def to_sfnt(self) -> None:
        """
        Convert a font to SFNT.
        """
        if self.is_sfnt:
            raise ValueError("Font is already a SFNT font.")

        self.ttfont.flavor = None

    def tt_decomponentize(self) -> None:
        """
        Decomponentize a TrueType font.
        """

        if not self.is_tt:
            raise NotImplementedError("Decomponentization is only supported for TrueType fonts.")

        glyph_set = self.ttfont.getGlyphSet()
        glyf_table = self.ttfont[GLYF_TABLE_TAG]
        dr_pen = DecomposingRecordingPen(glyph_set)
        tt_pen = TTGlyphPen(None)

        for glyph_name in self.ttfont.glyphOrder:
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

        dehint(self.ttfont)

    def tt_scale_upem(self, new_upem: int) -> None:
        """
        Scale the font's unitsPerEm value to the given value.

        Args:
            new_upem (int): The new unitsPerEm value.
        """

        if not self.is_tt:
            raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

        if new_upem not in range(MIN_UPM, MAX_UPM + 1):
            raise ValueError(f"units_per_em must be in the range {MAX_UPM} to {MAX_UPM}.")

        if self.ttfont["head"].unitsPerEm == new_upem:
            raise ValueError(f"Font already has {new_upem} units per em. No need to scale upem.")

        scale_upem(self.ttfont, new_upem=new_upem)

    def ps_correct_contours(self, min_area: int = 25) -> t.List[str]:
        """
        Correct the contours of a PostScript font by removing tiny paths and correcting the
        direction of paths.

        :param min_area: The minimum area of a path to be retained.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "PS Contour correction is only supported for PostScript flavored fonts."
            )

        charstrings, modified = fix_charstrings(font=self.ttfont, min_area=min_area)
        build_otf(font=self.ttfont, charstrings_dict=charstrings)

        return modified

    def ps_recalc_zones(self) -> t.Tuple[t.List[int], t.List[int]]:
        """
        Recalculates vertical alignment zones.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "Recalculation of zones is only supported for PostScript fonts."
            )

        return recalc_zones(self.ttfont)

    def ps_recalc_stems(self) -> t.Tuple[int, int]:
        """
        Returns a tuple containing two integer values representing the hinting (StdHW and StdVW)
        stems for the font.

        Returns:
            (tuple[int, int]): A tuple containing two integer values representing the hinting stems
                for the font.
        """
        if not self.file:
            raise NotImplementedError("Stem hints can only be extracted from a font file.")

        if not self.is_ps:
            raise NotImplementedError(
                "Recalculation of stems is only supported for PostScript fonts."
            )

        return recalc_stems(self.file)

    def ps_get_zones(self) -> t.Tuple[t.List[int], t.List[int]]:
        """
        Get zones from a font.

        :return: Zones.
        """
        if not self.is_ps:
            raise NotImplementedError("Getting zones is only supported for PostScript fonts.")

        try:
            return (
                getattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "OtherBlues"),
                getattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "BlueValues"),
            )
        except AttributeError:
            return [], []

    def ps_get_stems(self) -> t.Tuple[int, int]:
        """
        Get stems from a font.

        :return: Stems.
        """
        if not self.is_ps:
            raise NotImplementedError("Getting stems is only supported for PostScript fonts.")

        try:
            return (
                getattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "StdHW"),
                getattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "StdVW"),
            )
        except AttributeError:
            return 0, 0

    def ps_set_zones(self, other_blues: t.List[int], blue_values: t.List[int]) -> None:
        """
        Set zones for a font.

        :param other_blues: Other blues.
        :param blue_values: Blue values.
        """
        if not self.is_ps:
            raise NotImplementedError("Setting zones is only supported for PostScript fonts.")

        setattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "BlueValues", blue_values)
        setattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "OtherBlues", other_blues)

    def ps_set_stems(self, std_h_w: int, std_v_w: int) -> None:
        """
        Set stems for a font.

        :param std_h_w: StdHW.
        :param std_v_w: StdVW.
        """
        if not self.is_ps:
            raise NotImplementedError("Setting stems is only supported for PostScript fonts.")

        setattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "StdHW", std_h_w)
        setattr(self.ttfont["CFF "].cff.topDictIndex[0].Private, "StdVW", std_v_w)

    def ps_subroutinize(self) -> None:
        """
        Subroutinize a PostScript font.
        """

        cff_subr(font=self.ttfont)

    def ps_desubroutinize(self) -> None:
        """
        Desubroutinize a PostScript font.
        """

        cff_desubr(font=self.ttfont)
