import typing as t

from foundrytools_cli_2.lib.font import Font


def print_results(**kwargs: t.Any) -> None:
    """
    Print the results of rebuilding the cmap table of a font.
    """

    if kwargs.get("remap_all"):
        print("\nRemapping all glyphs")
    else:
        print("\nUpdating existing cmap")
    print("-" * 40)

    print("\nAnalysis")
    print("-" * 40)
    print(f"Total glyphs     : {kwargs.get('total_glyphs')}")
    print(f"Mapped glyphs    : {kwargs.get('mapped_glyphs')}")
    print(f"Unmapped glyphs  : {kwargs.get('unmapped_glyphs')}")
    print("\nRemapping results")
    print("-" * 40)
    print(f"Remapped glyphs  : {kwargs.get('remapped_glyphs')}")
    print(f"Skipped glyphs   : {kwargs.get('skipped_glyphs')}")
    print("-" * 40)
    print(f"Mapped glyphs after remapping   : {kwargs.get('mapped_glyphs_after')}")
    print(f"Unmapped glyphs after remapping : {kwargs.get('unmapped_glyphs_after')}")


def main(font: Font, remap_all: bool = False) -> None:
    """
    Rebuild the cmap table of a font.

    Args:
        font (Font): The font to rebuild the cmap table of.
        remap_all (bool, optional): Whether to remap all characters. Defaults to False.
    """
    cmap_table = font.ttfont["cmap"]
    result = font.rebuild_cmap(remap_all=remap_all)
    print_results(**result)
    font.modified = font.ttfont["cmap"].compile(font.ttfont) != cmap_table.compile(font.ttfont)
