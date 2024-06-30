from foundrytools_cli_2.lib.font import Font


def main(font: Font, remap_all: bool = False) -> None:
    """
    Rebuild the cmap table of a font.

    Args:
        font (Font): The font to rebuild the cmap table of.
        remap_all (bool, optional): Whether to remap all characters. Defaults to False.
    """
    cmap_table = font.ttfont["cmap"]
    font.rebuild_cmap(remap_all=remap_all)
    font.modified = font.ttfont["cmap"].compile(font.ttfont) != cmap_table.compile(font.ttfont)
