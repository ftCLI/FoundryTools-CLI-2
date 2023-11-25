from pathlib import Path
import typing as t

from afdko.otfautohint.__main__ import stemhist

STRAIGHT = "A,E,F,H,I,K,L,M,N,T,V,W,X,Y,Z"
CURVED = "O,Q,S"


def parse_stemhist_file(file_path: Path) -> int:
    """
    Parses the stemhist file and returns the stem width by reading the third line of the file.

    Parameters:
        file_path (Path): The path to the stemhist file.

    Returns:
        int: The value found in the stemhist file.

    """
    with open(file_path, "r", encoding="utf-8") as stem_file:
        line = stem_file.readlines()[2]
        return int(line[6:14].strip())


def get_stems_width(
    font_file: Path, glyph_names: str, include_curved: bool = False
) -> t.Tuple[int, int]:
    """

    Method: get_stems_width

    Retrieves the stem width for horizontal and vertical stems in a font file based on the specified
    letters.

    Parameters:
        font_file: Path object representing the path to the font file.
        glyph_names: String containing the letters for which to calculate the stem width.
        include_curved: Optional boolean indicating whether to include curved stems in the
            calculation. Default is False.

    Returns:
    A tuple of two integers representing the horizontal and vertical stem widths, respectively.

    """
    stemhist_base_path = font_file.parent / "stems"
    stemhist_args = [font_file.as_posix(), "-g", glyph_names, "-o", stemhist_base_path.as_posix()]
    if include_curved:
        stemhist_args.append("--all")

    stemhist(args=stemhist_args)

    h_stems_path = stemhist_base_path.with_suffix(".hstm.txt")
    v_stems_path = stemhist_base_path.with_suffix(".vstm.txt")
    h_stem = parse_stemhist_file(h_stems_path)
    v_stem = parse_stemhist_file(v_stems_path)
    return h_stem, v_stem


def recalc_stems(font_file: Path, include_curved: bool = False) -> t.Tuple[int, int]:
    """
    Get the standard horizontal and vertical stem widths for a given font file.

    :param font_file: The path to the font file.
    :type font_file: :class:`pathlib.Path`
    :param include_curved: Whether to include curved stems in the calculation.
    :type include_curved: bool, optional
    :return: A tuple containing the maximum horizontal and vertical stem widths.
    :rtype: :class:`tuple` of :class:`int`
    """

    straight_std_h_stem, straight_std_v_stem = get_stems_width(
        font_file=font_file, glyph_names=STRAIGHT, include_curved=False
    )

    if not include_curved:
        return straight_std_h_stem, straight_std_v_stem

    curved_std_h_stem, curved_std_v_stem = get_stems_width(
        font_file=font_file, glyph_names=CURVED, include_curved=True
    )

    return max(straight_std_h_stem, curved_std_h_stem), max(straight_std_v_stem, curved_std_v_stem)
