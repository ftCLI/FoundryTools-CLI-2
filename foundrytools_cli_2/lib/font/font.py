import math
import typing as t
from io import BytesIO
from pathlib import Path

from cffsubr import desubroutinize, subroutinize
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance
from fontTools.ttLib.ttGlyphSet import _TTGlyphSet
from pathvalidate import sanitize_filename
from ufo2ft.postProcessor import PostProcessor

from foundrytools_cli_2.lib.constants import (
    MAX_UPM,
    MIN_UPM,
    OTF_EXTENSION,
    PS_SFNT_VERSION,
    T_CMAP,
    T_FVAR,
    T_GLYF,
    T_HEAD,
    TT_SFNT_VERSION,
    TTF_EXTENSION,
    WOFF2_EXTENSION,
    WOFF2_FLAVOR,
    WOFF_EXTENSION,
    WOFF_FLAVOR,
)
from foundrytools_cli_2.lib.font.tables import CFFTable, HeadTable, NameTable, OS2Table
from foundrytools_cli_2.lib.otf.otf_builder import build_otf
from foundrytools_cli_2.lib.otf.t2_charstrings import quadratics_to_cubics
from foundrytools_cli_2.lib.skia.skia_tools import correct_contours_cff, correct_contours_glyf
from foundrytools_cli_2.lib.ttf.ttf_builder import build_ttf
from foundrytools_cli_2.lib.utils.misc import restore_flavor
from foundrytools_cli_2.lib.utils.path_tools import get_temp_file_path
from foundrytools_cli_2.lib.utils.unicode_tools import (
    _cmap_from_glyph_names,
    _prod_name_from_uni_str,
    _ReversedCmap,
    get_mapped_and_unmapped_glyphs,
    get_uni_str,
    setup_character_map,
    update_character_map,
)

__all__ = ["Font"]


class Font:  # pylint: disable=too-many-public-methods
    """
    The ``Font`` class is a wrapper around the ``TTFont`` class from ``fontTools``.

    It provides a high-level interface for working with the underlying TTFont object.
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
            source: A path to a font file (``str`` or ``Path`` object), a ``BytesIO`` object or
                a ``TTFont`` object.
            lazy: If ``True``, many data structures are loaded lazily, upon access only. If
                ``False``, many data structures are loaded immediately. The default is ``None``
                which is somewhere in between.
            recalc_bboxes: If ``True`` (the default), recalculates ``glyf``, ``CFF ``, ``head``
                bounding box values and ``hhea``/``vhea`` min/max values on save. Also compiles the
                glyphs on importing, which saves memory consumption and time.
            recalc_timestamp: If ``True``, sets the ``modified`` timestamp in the ``head`` table
                on save. Defaults to ``False``.
        """

        self._file: t.Optional[Path] = None
        self._bytesio: t.Optional[BytesIO] = None
        self._ttfont: t.Optional[TTFont] = None
        self._temp_file: Path = get_temp_file_path()
        self._modified = False

        if isinstance(source, (str, Path)):
            self._init_from_file(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, BytesIO):
            self._init_from_bytesio(source, lazy, recalc_bboxes, recalc_timestamp)
        elif isinstance(source, TTFont):
            self._init_from_ttfont(source, lazy, recalc_bboxes, recalc_timestamp)
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

    def _init_from_ttfont(
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
        Get the file path (if any) of the font.

        Returns:
            The file path of the font.
        """
        return self._file

    @file.setter
    def file(self, value: Path) -> None:
        """
        Set the file path of the font.

        Args:
            value: The file path of the font.
        """
        self._file = value

    @property
    def bytesio(self) -> t.Optional[BytesIO]:
        """
        Get the ``BytesIO`` object (if any) of the font.

        Returns:
            The ``BytesIO`` object of the font.
        """
        return self._bytesio

    @bytesio.setter
    def bytesio(self, value: BytesIO) -> None:
        """
        Set the ``BytesIO`` object of the font.

        Args:
            value: The ``BytesIO`` object of the font.
        """
        self._bytesio = value

    @property
    def ttfont(self) -> TTFont:
        """
        Get the underlying ``TTFont`` object of the font.

        Returns:
            The ``TTFont`` object of the font.
        """
        return self._ttfont

    @ttfont.setter
    def ttfont(self, value: TTFont) -> None:
        """
        Set the underlying ``TTFont`` object of the font.

        Args:
            value: The ``TTFont`` object of the font.
        """
        self._ttfont = value

    @property
    def temp_file(self) -> Path:
        """
        Get the temporary file path of the font.

        Returns:
            The temporary file path of the font.
        """
        return self._temp_file

    @property
    def modified(self) -> bool:
        """
        Check if the font has been modified.

        Returns:
            ``True`` if the font has been modified, ``False`` otherwise.
        """
        return self._modified

    @modified.setter
    def modified(self, value: bool) -> None:
        """
        Set the modified flag of the font.

        Args:
            value: A boolean indicating whether the font has been modified.
        """
        self._modified = value

    @property
    def glyph_set(self) -> _TTGlyphSet:
        """
        Get the glyph set of the font.

        Returns:
            The glyph set of the font.
        """
        return self.ttfont.getGlyphSet()

    @property
    def units_per_em(self) -> int:
        """
        Get the units per em of the font.

        Returns:
            The units per em of the font.
        """
        return self.ttfont[T_HEAD].unitsPerEm

    @property
    def is_ps(self) -> bool:
        """
        Check if the font has PostScript outlines.

        Returns:
            ``True`` if the font is a PostScript font, ``False`` otherwise.
        """
        return self.ttfont.sfntVersion == PS_SFNT_VERSION

    @property
    def is_tt(self) -> bool:
        """
        Check if the font has TrueType outlines.

        Returns:
            ``True`` if the font is a TrueType font, ``False`` otherwise.
        """
        return self.ttfont.sfntVersion == TT_SFNT_VERSION

    @property
    def is_woff(self) -> bool:
        """
        Check if the font is a WOFF font.

        Returns:
            ``True`` if the font is a WOFF font, ``False`` otherwise.
        """
        return self.ttfont.flavor == WOFF_FLAVOR

    @property
    def is_woff2(self) -> bool:
        """
        Check if the font is a WOFF2 font.

        Returns:
            ``True`` if the font is a WOFF2 font, ``False`` otherwise.
        """
        return self.ttfont.flavor == WOFF2_FLAVOR

    @property
    def is_sfnt(self) -> bool:
        """
        Check if the font is a SFNT font (i.e. not a WOFF or WOFF2 font).

        Returns:
            ``True`` if the font is a SFNT font, ``False`` otherwise.
        """
        return self.ttfont.flavor is None

    @property
    def is_static(self) -> bool:
        """
        Check if the font is a static font.

        Returns:
            ``True`` if the font is a static font, ``False`` otherwise.
        """
        return self.ttfont.get(T_FVAR) is None

    @property
    def is_variable(self) -> bool:
        """
        Check if the font is a variable font.

        Returns:
            ``True`` if the font is a variable font, ``False`` otherwise.
        """
        return self.ttfont.get(T_FVAR) is not None

    @property
    def is_italic(self) -> bool:
        """
        Check if the font is italic.

        Returns:
            ``True`` if the font is italic, ``False`` otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)
        return os_2.fs_selection.italic and head.mac_style.italic

    @is_italic.setter
    def is_italic(self, value: bool) -> None:
        """
        Set the italic bit in the ``macStyle`` field of the ``head`` table anf in the
        ``fsSelection`` field of the ``OS/2`` table.

        Args:
            value: A boolean indicating whether to set the italic bits or to clear them.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.fs_selection.italic = True
            head.mac_style.italic = True
            os_2.fs_selection.regular = False
        else:
            os_2.fs_selection.italic = False
            head.mac_style.italic = False
            if not os_2.fs_selection.bold:
                os_2.fs_selection.regular = True

    @property
    def is_oblique(self) -> bool:
        """
        Check if the font is oblique.

        Returns:
            ``True`` if the font is oblique, ``False`` otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        return os_2.fs_selection.oblique

    @is_oblique.setter
    def is_oblique(self, value: bool) -> None:
        """
        Set the oblique bit in the ``macStyle`` field of the ``head`` table.

        Args:
            value: A boolean indicating whether to set the oblique bit or to clear it.
        """
        os_2 = OS2Table(self.ttfont)
        os_2.fs_selection.oblique = value

    @property
    def is_bold(self) -> bool:
        """
        Check if the font is bold.

        Returns:
            ``True`` if the font is bold, ``False`` otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)
        return os_2.fs_selection.bold and head.mac_style.bold

    @is_bold.setter
    def is_bold(self, value: bool) -> None:
        """
        Set the bold bit in the ``macStyle`` field of the ``head`` table and in the ``fsSelection``
        field of the ``OS/2`` table.

        Args:
            value: A boolean indicating whether to set the bold bits or to clear them.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.fs_selection.bold = True
            head.mac_style.bold = True
            os_2.fs_selection.regular = False
        else:
            os_2.fs_selection.bold = False
            head.mac_style.bold = False
            if not os_2.fs_selection.italic:
                os_2.fs_selection.regular = True

    @property
    def is_regular(self) -> bool:
        """
        Check if the font is regular.

        Returns:
            ``True`` if the font is regular, ``False`` otherwise.
        """
        os_2 = OS2Table(self.ttfont)
        return os_2.fs_selection.regular

    @is_regular.setter
    def is_regular(self, value: bool) -> None:
        """
        Set the regular bit in the ``macStyle`` field of the ``head`` table and clear the bold and
        italic bits in the ``fsSelection`` field of the ``OS/2`` table and ind the ``macStyle``
        field of the ``head`` table.

        Args:
            value: A boolean indicating whether to set the regular bit or to clear it.
        """
        os_2 = OS2Table(self.ttfont)
        head = HeadTable(self.ttfont)

        if value:
            os_2.fs_selection.bold = False
            os_2.fs_selection.italic = False
            head.mac_style.bold = False
            head.mac_style.italic = False
            os_2.fs_selection.regular = True
        else:
            if self.is_bold or self.is_italic:
                os_2.fs_selection.regular = False

    def save(
        self,
        file: t.Union[str, Path, BytesIO],
        reorder_tables: t.Optional[bool] = True,
    ) -> None:
        """
        Save the font to a file.

        Args:
            file: The file name to use for the output file.
            reorder_tables: If ``True`` (the default), reorder the tables, sorting them by tag
                (recommended by the OpenType specification). If ``False``, retain the original
                order. If ``None``, reorder by table dependency (fastest).
        """
        self.ttfont.save(file, reorderTables=reorder_tables)

    def save_to_temp_file(self, reorder_tables: t.Optional[bool] = True) -> None:
        """
        Save the font to a temporary file.

        Args:
            reorder_tables: If ``True`` (the default), reorder the tables, sorting them by tag
                (recommended by the OpenType specification). If ``False``, retain the original
                order. If ``None``, reorder by table dependency (fastest).
        """
        self.save(self._temp_file, reorder_tables=reorder_tables)

    def close(self) -> None:
        """
        Close the font and delete the temporary file.
        """
        self.ttfont.close()
        self._temp_file.unlink(missing_ok=True)
        if self.bytesio:
            self.bytesio.close()

    def reload(self) -> None:
        """
        Reload the font by saving it to a temporary stream and then loading it back.
        """
        recalc_bboxes = self.ttfont.recalcBBoxes
        recalc_timestamp = self.ttfont.recalcTimestamp
        buf = BytesIO()
        self.ttfont.save(buf)
        buf.seek(0)
        self.ttfont = TTFont(buf, recalcBBoxes=recalc_bboxes, recalcTimestamp=recalc_timestamp)
        buf.close()

    def make_out_file_name(
        self,
        file: t.Optional[Path] = None,
        output_dir: t.Optional[Path] = None,
        overwrite: bool = True,
        extension: t.Optional[str] = None,
        suffix: str = "",
    ) -> Path:
        """
        Get output file for a ``Font`` object. If ``output_dir`` is not specified, the output file
        will be saved in the same directory as the input file. It the output file already exists and
        ``overwrite`` is ``False``, file name will be incremented by adding a number preceded by '#'
        before the extension until a non-existing file name is found. If ``suffix`` is specified,
        it will be appended to the file name. If the suffix is already present, it will be removed
        before adding it again.

        Args:
            file: The input file.
            output_dir: The output directory.
            overwrite: If ``True``, overwrite the output file if it already exists. If ``False``,
                increment the file name until a non-existing file name is found.
            extension: The extension of the output file. If not specified, the extension will be
                determined by the font type.
            suffix: A suffix to append to the file name.

        Returns:
            A ``Path`` object pointing to the output file.
        """

        if file is None and self.file is None:
            raise ValueError(
                "Cannot get output file for a BytesIO object without providing a file name."
            )

        file = file or self.file
        if not isinstance(file, Path):
            raise ValueError("File must be a Path object.")

        out_dir = output_dir or file.parent
        extension = extension or self.get_real_extension()
        file_name = file.stem + extension

        # Clean up the file name by removing the extensions used as file name suffix as added by
        # possible previous conversions. This is necessary to avoid adding the suffix multiple
        # times, like in the case of a file name like 'font.woff2.ttf.woff2'. It may happen when
        # converting a WOFF2 font to TTF and then to WOFF2 again.
        if suffix != "":
            for ext in [OTF_EXTENSION, TTF_EXTENSION, WOFF2_EXTENSION, WOFF_EXTENSION]:
                file_name = file_name.replace(ext, "")

        out_file = Path(
            makeOutputFileName(
                input=file_name,
                outputDir=out_dir,
                extension=extension,
                overWrite=overwrite,
                suffix=suffix,
            )
        )
        return out_file

    def get_real_extension(self) -> str:
        """
        Get the real extension of the font. If the font is a web font, the extension will be
        determined by the font flavor. If the font is a SFNT font, the extension will be determined
        by the sfntVersion attribute.

        Returns:
            The real extension of the font (e.g. '.woff', '.woff2', '.otf', '.ttf').
        """

        # Order of the if statements is important. WOFF and WOFF2 must be checked before OTF and
        # TTF.
        if self.is_woff:
            return WOFF_EXTENSION
        if self.is_woff2:
            return WOFF2_EXTENSION
        if self.is_ps:
            return OTF_EXTENSION
        if self.is_tt:
            return TTF_EXTENSION
        raise ValueError("Unknown font type.")

    def get_best_file_name(self, source: int = 1) -> str:
        """
        Get the best file name for a font.

        Args:
            source (int, optional): The source string(s) from which to extract the new file name.
                Default is 1 (FamilyName-StyleName), used also as fallback name when 4 or 5 are
                passed but the font is TrueType.

                1: FamilyName-StyleName
                2: PostScript Name
                3: Full Font Name
                4: CFF fontNames (CFF fonts only)
                5: CFF TopDict FullName (CFF fonts only)

        Returns:
            A ``Path`` object pointing to the best file name for the font.
        """
        name_table = NameTable(self.ttfont)
        cff_table = CFFTable(self.ttfont) if self.is_ps else None

        if self.is_variable:
            family_name = name_table.get_best_family_name().replace(" ", "").strip()
            if self.is_italic:
                family_name += "-Italic"
            axes = self.get_axes()
            file_name = f"{family_name}[{','.join([axis.axisTag for axis in axes])}]"
            return sanitize_filename(file_name, platform="auto")

        if self.is_tt and source in (4, 5):
            source = 1
        if source == 1:
            family_name = name_table.get_best_family_name()
            subfamily_name = name_table.get_best_subfamily_name()
            file_name = f"{family_name}-{subfamily_name}".replace(" ", "").replace(".", "")
        elif source == 2:
            file_name = name_table.get_debug_name(name_id=6)
        elif source == 3:
            file_name = name_table.get_best_full_name()
        elif source == 4 and cff_table is not None:
            file_name = cff_table.table.cff.fontNames[0]
        elif source == 5 and cff_table is not None:
            file_name = cff_table.table.cff.topDictIndex[0].FullName
        else:
            raise ValueError("Invalid source value.")
        return sanitize_filename(file_name, platform="auto")

    def get_best_family_name(self) -> str:
        """
        Get the best family name for a font.

        Returns:
            The best family name for the font.
        """
        name_table = NameTable(self.ttfont)
        return name_table.get_best_family_name()

    def get_best_subfamily_name(self) -> str:
        """
        Get the best subfamily name for a font.

        Returns:
            The best subfamily name for the font.
        """
        name_table = NameTable(self.ttfont)
        return name_table.get_best_subfamily_name()

    def get_manufacturer(self) -> str:
        """
        Get the manufacturer of the font.

        Returns:
            The manufacturer of the font.
        """
        name_table = NameTable(self.ttfont)
        return name_table.get_manufacturer_name()

    def get_font_revision(self) -> str:
        """
        Get the font revision.

        Returns:
            The font revision.
        """
        head = HeadTable(self.ttfont)
        return f"{head.font_revision:.3f}"

    def get_axes(self) -> t.List[Axis]:
        """
        Get axes from a variable font.

        Returns:
            A list of ``Axis`` objects.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        # Filter out the 'hidden' axes (flags != 0)
        return [axis for axis in self.ttfont[T_FVAR].axes if axis.flags == 0]

    def get_instances(self) -> t.List[NamedInstance]:
        """
        Get named instances from a variable font.

        Returns:
            A list of ``NamedInstance`` objects.
        """
        if not self.is_variable:
            raise NotImplementedError("Not a variable font.")

        return self.ttfont[T_FVAR].instances

    def to_woff(self) -> None:
        """
        Convert a font to WOFF.
        """
        if self.is_woff:
            raise NotImplementedError("Font is already a WOFF font.")

        self.ttfont.flavor = WOFF_FLAVOR

    def to_woff2(self) -> None:
        """
        Convert a font to WOFF2.
        """
        if self.is_woff2:
            raise NotImplementedError("Font is already a WOFF2 font.")

        self.ttfont.flavor = WOFF2_FLAVOR

    def to_ttf(self, max_err: float = 1.0, reverse_direction: bool = True) -> None:
        """
        Convert a font to TrueType.
        """
        if self.is_tt:
            raise NotImplementedError("Font is already a TrueType font.")
        if self.is_variable:
            raise NotImplementedError("Conversion to TrueType is not supported for variable fonts.")

        build_ttf(font=self.ttfont, max_err=max_err, reverse_direction=reverse_direction)

    def to_otf(self, tolerance: float = 1.0, correct_contours: bool = True) -> None:
        """
        Convert a font to PostScript.
        """
        if self.is_ps:
            raise NotImplementedError("Font is already a PostScript font.")
        if self.is_variable:
            raise NotImplementedError(
                "Conversion to PostScript is not supported for variable fonts."
            )

        charstrings = quadratics_to_cubics(
            font=self.ttfont, tolerance=tolerance, correct_contours=correct_contours
        )
        build_otf(font=self.ttfont, charstrings_dict=charstrings)

    def to_sfnt(self) -> None:
        """
        Convert a font to SFNT.
        """
        if self.is_sfnt:
            raise NotImplementedError("Font is already a SFNT font.")

        self.ttfont.flavor = None

    def calculate_italic_angle(self, min_slant: float = 2.0) -> float:
        """
        Calculates the italic angle of a font by measuring the slant of the glyph 'H' or 'uni0048'.

        Args:
            min_slant (float, optional): The minimum slant value to consider a font italic. If the
                slant is less than the minimum slant, the method will return 0.0. Defaults to 2.0.

        Returns:
            The italic angle of the font in degrees, rounded to three decimal places.

        Raises:
            ValueError: If the font does not contain the glyph 'H' or 'uni0048'.
        """
        glyph_set = self.ttfont.getGlyphSet()
        pen = StatisticsPen(glyphset=glyph_set)
        for g in ("H", "uni0048"):
            try:
                glyph_set[g].draw(pen)
                italic_angle = -1 * math.degrees(math.atan(pen.slant))
                if abs(italic_angle) >= abs(min_slant):
                    return italic_angle
                return 0.0
            except KeyError:
                continue
        raise ValueError("The font does not contain the glyph 'H' or 'uni0048'.")

    def tt_decomponentize(self) -> None:
        """
        Decomposes all composite glyphs of a TrueType font.
        """
        if not self.is_tt:
            raise NotImplementedError("Decomponentization is only supported for TrueType fonts.")

        glyph_set = self.ttfont.getGlyphSet()
        glyf_table = self.ttfont[T_GLYF]
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

    def tt_scale_upem(self, target_upm: int) -> None:
        """
        Scale the font's Units Per Em (UPM).

        Args:
            target_upm (int): The new units per em value. Must be in the range 16 to 16384.
        """
        if not self.is_tt:
            raise NotImplementedError("Scaling upem is only supported for TrueType fonts.")

        if target_upm < MIN_UPM or target_upm > MAX_UPM:
            raise ValueError(f"units_per_em must be in the range {MAX_UPM} to {MAX_UPM}.")

        if self.ttfont[T_HEAD].unitsPerEm == target_upm:
            raise ValueError(f"Font already has {target_upm} units per em. No need to scale upem.")

        scale_upem(self.ttfont, new_upem=target_upm)

    def tt_correct_contours(self, min_area: int = 25) -> t.List[str]:
        """
        Correct the contours of a TrueType font by removing overlaps and tiny paths and correcting
        the direction of paths.
        If one or more contours are modified, the glyf table will be rebuilt.
        If no contours are modified, the font will remain unchanged and the method will return an
        empty list.

        Args:
            min_area (int, optional): The minimum area of a contour to be considered. Defaults to
            25.

        Returns:
            A list of modified glyphs.
        """
        if not self.is_tt:
            raise NotImplementedError(
                "TTF Contour correction is only supported for TrueType fonts."
            )

        if self.is_variable:
            raise NotImplementedError("Contour correction is not supported for variable fonts.")

        modified_glyphs = correct_contours_glyf(font=self.ttfont, min_area=min_area)
        return modified_glyphs

    def ps_correct_contours(self, min_area: int = 25) -> t.List[str]:
        """
        Correct the contours of a PostScript font by removing overlaps and tiny paths and correcting
        the direction of paths.
        If one or more contours are modified, the CFF table will be rebuilt.
        If no contours are modified, the font will remain unchanged and the method will return an
        empty list.

        Args:
            min_area (int, optional): The minimum area of a contour to be considered. Defaults to
            25.

        Returns:
            A list of modified glyphs.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "PS Contour correction is only supported for PostScript flavored fonts."
            )

        if self.is_variable:
            raise NotImplementedError("PS Contour correction is not supported for variable fonts.")

        charstrings, modified_glyphs = correct_contours_cff(font=self.ttfont, min_area=min_area)
        if not modified_glyphs:
            return []
        build_otf(font=self.ttfont, charstrings_dict=charstrings)
        return modified_glyphs

    def ps_subroutinize(self) -> None:
        """
        Subroutinize a PostScript font.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "Subroutinization is only supported for PostScript flavored fonts."
            )
        with restore_flavor(self.ttfont):
            subroutinize(self.ttfont)

    def ps_desubroutinize(self) -> None:
        """
        Desubroutinize a PostScript font.
        """
        if not self.is_ps:
            raise NotImplementedError(
                "Desubroutinization is only supported for PostScript flavored fonts."
            )
        with restore_flavor(self.ttfont):
            desubroutinize(self.ttfont)

    def rebuild_cmap(self, remap_all: bool = False) -> t.Dict[str, int]:
        """
        Rebuild the character map of a font.

        Args:
            remap_all: Whether to remap all glyphs.
        """
        # rebuild_character_map(font=self.ttfont, remap_all=remap_all)

        glyph_order = self.ttfont.getGlyphOrder()
        mapped, unmapped = get_mapped_and_unmapped_glyphs(ttfont=self.ttfont)
        if not remap_all:
            target_cmap = self.ttfont.getBestCmap()  # We can also use cmap_from_reversed_cmap
            source_cmap = _cmap_from_glyph_names(glyphs_list=unmapped)
        else:
            target_cmap = {}
            source_cmap = _cmap_from_glyph_names(glyphs_list=glyph_order)

        updated_cmap, remapped, duplicates = update_character_map(
            source_cmap=source_cmap, target_cmap=target_cmap
        )
        setup_character_map(ttfont=self.ttfont, mapping=updated_cmap)

        result = {
            "total_glyphs": len(glyph_order),
            "mapped_glyphs": len(mapped),
            "unmapped_glyphs": len(unmapped),
            "remapped_glyphs": len(remapped),
            "skipped_glyphs": len(duplicates),
            "mapped_glyphs_after": len(get_mapped_and_unmapped_glyphs(ttfont=self.ttfont)[0]),
            "unmapped_glyphs_after": len(get_mapped_and_unmapped_glyphs(ttfont=self.ttfont)[1]),
        }

        return result

    def set_production_names(self) -> t.List[t.Tuple[str, str]]:
        """

        Set the production names for the glyphs in the TrueType font.

        Returns a list of tuples containing the original glyph name and its corresponding
        production name.

        - `old_glyph_order`: A list of strings representing the original glyph order in the
        underlying TTFont object.
        - `reversed_cmap`: An instance of `_ReversedCmap` representing  the reversed cmap table of
        the TrueType font.

        Returns:
            A list of tuples, where each tuple contains the original glyph name and its production
            name.

        The method iterates through each glyph in the old glyph order and determines its production
        name based on its assigned or calculated Unicode value. If the production name is already
        assigned, the glyph is skipped. If the production name is different from the original glyph
        name and is not already assigned, the glyph is renamed and added to the new glyph order
        list. Finally, the font is updated with the new glyph order, the cmap table is rebuilt, and
        the list of renamed glyphs is returned.
        """
        old_glyph_order: t.List[str] = self.ttfont.getGlyphOrder()
        reversed_cmap: _ReversedCmap = self.ttfont[T_CMAP].buildReversed()
        new_glyph_order: t.List[str] = []
        renamed_glyphs: t.List[t.Tuple[str, str]] = []

        for glyph_name in old_glyph_order:
            uni_str = get_uni_str(glyph_name, reversed_cmap)
            # If still no uni_str, the glyph name is unmodified.
            if not uni_str:
                new_glyph_order.append(glyph_name)
                continue

            # In case the production name could not be found, the glyph is already named with the
            # production name, or the production name is already assigned, we skip the renaming
            # process.
            production_name = _prod_name_from_uni_str(uni_str)
            if (
                not production_name
                or production_name == glyph_name
                or production_name in old_glyph_order
            ):
                new_glyph_order.append(glyph_name)
                continue

            new_glyph_order.append(production_name)
            renamed_glyphs.append((glyph_name, production_name))

        if not renamed_glyphs:
            return []

        rename_map = dict(zip(old_glyph_order, new_glyph_order))
        PostProcessor.rename_glyphs(otf=self.ttfont, rename_map=rename_map)
        self.rebuild_cmap(remap_all=True)
        return renamed_glyphs

    def rename_glyph(self, old_name: str, new_name: str) -> bool:
        """
        Rename a single glyph in the font.

        Args:
            old_name (str): The old name of the glyph.
            new_name (str): The new name of the glyph.
        """
        old_glyph_order = self.ttfont.getGlyphOrder()
        new_glyph_order = []

        if old_name not in old_glyph_order:
            raise ValueError(f"Glyph '{old_name}' not found in the font.")

        if new_name in old_glyph_order:
            raise ValueError(f"Glyph '{new_name}' already exists in the font.")

        for glyph_name in old_glyph_order:
            if glyph_name == old_name:
                new_glyph_order.append(new_name)
            else:
                new_glyph_order.append(glyph_name)

        rename_map = dict(zip(old_glyph_order, new_glyph_order))
        PostProcessor.rename_glyphs(otf=self.ttfont, rename_map=rename_map)
        self.rebuild_cmap(remap_all=True)

        return new_glyph_order != old_glyph_order

    def rename_glyphs(self, new_glyph_order: t.List[str]) -> bool:
        """
        Rename the glyphs in the font based on the new glyph order.

        Args:
            new_glyph_order (list): The new glyph order.
        """
        old_glyph_order = self.ttfont.getGlyphOrder()
        if new_glyph_order == old_glyph_order:
            return False

        rename_map = dict(zip(old_glyph_order, new_glyph_order))
        PostProcessor.rename_glyphs(otf=self.ttfont, rename_map=rename_map)
        self.rebuild_cmap(remap_all=True)

        return True

    def sort_glyphs(self, new_glyph_order: t.List[str]) -> None:
        """
        Reorder the glyphs based on the Unicode values.

        Args:
            new_glyph_order (list): The new glyph order.
        """
        self.ttfont.reorderGlyphs(new_glyph_order=new_glyph_order)
        if self.is_ps:
            cff_table = CFFTable(self.ttfont)
            charstrings = cff_table.charstrings.charStrings
            cff_table.top_dict.charset = new_glyph_order
            cff_table.charstrings.charStrings = {k: charstrings.get(k) for k in new_glyph_order}
