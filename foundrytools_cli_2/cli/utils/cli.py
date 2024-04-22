# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.lib import FontRunner

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("reorder-glyphs")
@base_options()
def reorder_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Reorder the glyphs.
    """
    from foundrytools_cli_2.cli.utils.snippets.reorder_glyphs import main as task

    runner = FontRunner(input_path=input_path, task=task, **options)
    runner.run()
