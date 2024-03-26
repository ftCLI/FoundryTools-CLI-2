# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Fix font errors.")


@cli.command("italic-angle")
@click.option(
    "--min-slant",
    type=float,
    default=2.0,
    show_default=True,
    help="The minimum slant to consider a font italic.",
)
@click.option(
    "--mode",
    type=click.IntRange(1, 3),
    default=1,
    show_default=True,
    help="""Which attributes to set when the calculated italic angle is not 0.

\b
1: Only set the italic bits.
2: Only set the oblique bit.
3: Set the italic and oblique bits.
\n
""",
)
@base_options()
def fix_italic_angle(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the italic angle and related attributes in the font.

    The italic angle is recalculated as first step.

    The italic and oblique bits are then set based
    on the calculated italic angle and the provided mode.
    """
    from foundrytools_cli_2.cli.fix.snippets.italic_angle import main as task

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("notdef-empty")
@base_options()
def fix_empty_notdef(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the empty .notdef glyph by drawing a simple rectangle.

    Glyph 0 must be assigned to a .notdef glyph. The .notdef glyph is very important for providing
    the user feedback that a glyph is not found in the font. This glyph should not be left without
    an outline as the user will only see what looks like a space if a glyph is missing and not be
    aware of the active font’s limitation.
    """
    from foundrytools_cli_2.cli.fix.snippets.empty_notdef import fix_notdef_empty as task

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.run()
