# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("sort-glyphs")
@base_options()
def sort_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Reorder the glyphs based on their Unicode values.
    """
    from foundrytools_cli_2.cli.utils.snippets.sort_glyphs import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("unicodes-from-names")
@base_options()
def unicodes_from_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename glyphs based on a mapping file.
    """
    from foundrytools_cli_2.cli.utils.snippets.unicodes_from_glyph_names import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("names-from-unicodes")
@base_options()
def glyph_names_from_unicodes(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename glyphs in the font to their Unicode values.
    """
    from foundrytools_cli_2.cli.utils.snippets.names_from_unicodes import rename_glyphs as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
