import typing as t

from foundrytools_cli_2.lib.font import Font


def _print_results(renamed_glyphs: t.List[t.Tuple[str, str]]) -> None:
    """
    Print the results of setting the production names of glyphs in a font.

    Args:
        renamed_glyphs (List[Tuple[str, str]]): A list of tuples containing the old and new
        production names of glyphs.
    """
    for old_name, new_name in renamed_glyphs:
        print(f"Renamed {old_name} to {new_name}.")


def main(font: Font) -> None:
    """
    Set the production names of glyphs in a font.

    Args:
        font (Font): The font to set the production names of.
    """
    renamed_glyphs = font.set_production_names()
    if renamed_glyphs:
        _print_results(renamed_glyphs)
        font.is_modified = True
