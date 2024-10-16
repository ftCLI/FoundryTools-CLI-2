import typing as t
from shutil import get_terminal_size

from fontTools.ttLib.tables._n_a_m_e import _MAC_LANGUAGES, _WINDOWS_LANGUAGES, NameRecord
from rich.console import Console
from rich.table import Table

from foundrytools_cli_2.lib.constants import (
    MAC_ENCODING_IDS,
    NAME_IDS_TO_DESCRIPTION,
    PLATFORMS,
    TERMINAL_WIDTH,
    WINDOWS_ENCODING_IDS,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import CFFTable, NameTable
from foundrytools_cli_2.lib.utils.string_tools import wrap_string

MINIMAL_NAME_IDS = {1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22, 25}
MINIMAL_CFF_NAMES = {"version", "FullName", "FamilyName", "Weight"}
IGNORED_CFF_NAMES = {
    "UnderlinePosition",
    "UnderlineThickness",
    "FontMatrix",
    "FontBBox",
    "charset",
    "Encoding",
    "Private",
    "CharStrings",
    "isFixedPitch",
    "ItalicAngle",
}


def _get_platform_row(platform: t.Tuple[int, int, int]) -> str:
    """
    Returns a string that describes the platform, encoding, and language.
    """
    platform_id = platform[0]
    plat_enc_id = platform[1]
    language_id = platform[2]
    platform_string = PLATFORMS.get(platform[0])
    if platform_id == 1:
        plat_enc_string = MAC_ENCODING_IDS.get(plat_enc_id)
        language_string = _MAC_LANGUAGES.get(language_id)
    elif platform_id == 3:
        plat_enc_string = WINDOWS_ENCODING_IDS.get(plat_enc_id)
        language_string = _WINDOWS_LANGUAGES.get(language_id)
    else:
        plat_enc_string = f"Unknown ({plat_enc_id})"
        language_string = f"Unknown ({language_id})"

    return (
        f"[bold green]PlatformID: {platform_id} ({platform_string}), PlatEncID: {plat_enc_id} "
        f"({plat_enc_string}), LangID: {language_id} ({language_string})[reset]"
    )


def _get_name_row(name: NameRecord) -> str:
    """
    Returns a string that describes a NameRecord.
    """
    name_description = NAME_IDS_TO_DESCRIPTION.get(name.nameID, f"{name.nameID}")
    return (
        f"[bold cyan]{str(name.nameID).rjust(5)}[reset] : "
        f"{name_description.ljust(22)} : {name.toUnicode()}"
    )


def main(font: Font, max_lines: t.Optional[int] = None, minimal: bool = False) -> None:
    """
    Prints the names of the font.
    """

    terminal_width = min(TERMINAL_WIDTH, get_terminal_size()[0] - 1)
    console = Console()
    table = Table(show_header=False, title_style="bold green")

    name_table = NameTable(font.ttfont)
    names = name_table.names

    table.add_row(f"[bold cyan]Font file: {font.file.name if font.file else font.bytesio}[reset]")
    table.add_section()

    table.add_row("[bold magenta]'name' table[reset]")
    platforms = {(name.platformID, name.platEncID, name.langID) for name in names}
    for platform in platforms:
        platform_row = _get_platform_row(platform)

        table.add_section()
        table.add_row(platform_row)
        table.add_section()

        for name in names:
            if (name.platformID, name.platEncID, name.langID) == platform:
                if minimal and name.nameID not in MINIMAL_NAME_IDS:
                    continue
                row_string = _get_name_row(name)
                row_string = wrap_string(
                    width=terminal_width,
                    initial_indent=0,
                    indent=33,
                    max_lines=max_lines,
                    string=row_string,
                )
                table.add_row(row_string)

    if font.is_ps:
        cff_table = CFFTable(font.ttfont)

        cff_names = [
            {k: v}
            for k, v in cff_table.top_dict.rawDict.items()
            if k not in IGNORED_CFF_NAMES and (not minimal or k in MINIMAL_CFF_NAMES)
        ]
        cff_names.insert(0, {"fontNames": cff_table.table.cff.fontNames})

        table.add_section()
        table.add_row("[bold magenta]'CFF ' table[reset]")
        table.add_section()
        for cff_name in cff_names:
            for key, value in cff_name.items():
                row_string = f"{key.ljust(22)} : {value}"
                row_string = wrap_string(
                    width=terminal_width,
                    initial_indent=8,
                    indent=33,
                    max_lines=max_lines,
                    string=row_string,
                )
                table.add_row(row_string)

    console.print(table)
