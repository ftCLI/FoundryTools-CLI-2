# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.lib.click.options import common_options
from foundrytools_cli_2.lib.font_runner import FontRunner

cli = click.Group(help="Fix font errors.")


@cli.command("empty-notdef")
@common_options()
def fix_empty_notdef(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the empty .notdef glyph by adding a simple rectangle.
    """
    from foundrytools_cli_2.snippets.fix_empty_notdef import fix_empty_notdef as main

    runner = FontRunner(input_path=input_path, task=main, **options)
    runner.run()
