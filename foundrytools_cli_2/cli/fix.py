# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.options import common_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Fix font errors.")


@cli.command("notdef-empty")
@common_options()
def fix_empty_notdef(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the empty .notdef glyph by drawing a simple rectangle.

    Glyph 0 must be assigned to a .notdef glyph. The .notdef glyph is very important for providing
    the user feedback that a glyph is not found in the font. This glyph should not be left without
    an outline as the user will only see what looks like a space if a glyph is missing and not be
    aware of the active font’s limitation.
    """
    from foundrytools_cli_2.snippets.fix.empty_notdef import fix_notdef_empty as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
