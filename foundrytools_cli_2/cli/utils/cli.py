# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import (
    base_options,
    input_path_argument,
    output_dir_option,
    overwrite_flag,
    recalc_timestamp_flag,
)
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Miscellaneous utilities.")


@cli.command("rebuild-cmap")
@base_options()
@click.option(
    "--remap-all",
    is_flag=True,
    help="Remap all characters in the cmap table.",
)
def rebuild_cmap_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rebuild the cmap table of a font. Optionally remap all characters, including those already in
    the cmap table.
    """
    from foundrytools_cli_2.cli.utils.snippets.rebuild_cmap import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("rename-glyph")
@base_options()
@click.option("-old", "--old-name", required=True, help="The old name of the glyph.")
@click.option("-new", "--new-name", required=True, help="The new name of the glyph.")
def rename_glyph_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename a glyph in a font file.
    """
    from foundrytools_cli_2.cli.utils.snippets.rename_glyph import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.force_modified = True
    runner.run()


@cli.command("rename-glyphs")
@base_options()
@click.option(
    "-s",
    "--source-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="The source font file to get the glyph order from.",
)
def rename_glyphs_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename glyphs in a font file based on the glyph order of another font file.
    """
    from foundrytools_cli_2.cli.utils.snippets.rename_glyphs import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-production-names")
@base_options()
def set_production_names_command(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the production names of glyphs in a font file.
    """
    from foundrytools_cli_2.cli.utils.snippets.set_production_names import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("remove-unused-glyphs")
@input_path_argument()
@output_dir_option()
@overwrite_flag()
@recalc_timestamp_flag()
def remove_unused_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Subsets a font file by removing unreachable glyphs.
    """
    from foundrytools_cli_2.cli.utils.snippets.remove_unused_glyphs import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.save_if_modified = False
    runner.run()
