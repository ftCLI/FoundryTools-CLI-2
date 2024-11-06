import typing as t

from foundrytools_cli_2.lib.font import Font


def main(
    font: Font,
    sort_by: t.Literal["unicode", "alphabetical", "cannedDesign"] = "unicode",
) -> None:
    """
    Reorders the glyphs based on the Unicode values.
    """
    if font.sort_glyphs(sort_by=sort_by):
        font.is_modified = True
