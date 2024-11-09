# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_callbacks import tuple_to_set_callback
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="A collection of utilities to remap, rename and sort glyphs.")


@cli.command("remap")
@click.option(
    "--remap-all",
    is_flag=True,
    help="Remap all glyphs, including the ones already in the cmap table.",
)
@base_options()
def rebuild_cmap(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rebuild the cmap table of a font. Optionally remap all characters, including those already in
    the cmap table.
    """
    from foundrytools_cli_2.cli.glyphs.tasks import rebuild_cmap as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("remove-glyphs")
@click.option(
    "-gn",
    "--glyph-name",
    "glyph_names_to_remove",
    type=str,
    multiple=True,
    help="The names of the glyphs to remove.",
    callback=tuple_to_set_callback,
)
@click.option(
    "-gid",
    "--glyph-id",
    "glyph_ids_to_remove",
    type=int,
    multiple=True,
    help="The glyph IDs to remove.",
    callback=tuple_to_set_callback,
)
@base_options()
def remove_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Remove glyphs from a font file.
    """
    if not options.get("glyph_names_to_remove") and not options.get("glyph_ids_to_remove"):
        raise click.UsageError("You must provide at least one glyph name or ID to remove.")

    from foundrytools_cli_2.cli.glyphs.tasks import remove_glyphs as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("rename-glyph")
@click.option("-old", "--old-name", required=True, help="The old name of the glyph.")
@click.option("-new", "--new-name", required=True, help="The new name of the glyph.")
@base_options()
def rename_glyph(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename a glyph in a font file.
    """
    from foundrytools_cli_2.cli.glyphs.tasks import rename_glyph as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.force_modified = True
    runner.run()


@cli.command("rename-glyphs")
@click.option(
    "-s",
    "--source-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="The source font file to get the glyph order from.",
)
@base_options()
def rename_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Rename glyphs in a font file based on the glyph order of another font file.
    """
    from foundrytools_cli_2.cli.glyphs.tasks import rename_glyphs as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("set-production-names")
@base_options()
def set_production_names(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Set the production names of glyphs in a font file.
    """
    from foundrytools_cli_2.cli.glyphs.tasks import set_production_names as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("sort")
@click.option(
    "-by",
    "--sort-by",
    type=click.Choice(["unicode", "alphabetical", "cannedDesign"]),
    default="unicode",
    show_default=True,
    help="""
    The method to sort the glyphs.

    \b
    - unicode: Sort the glyphs based on their Unicode values.
    - alphabetical: Sort the glyphs alphabetically.
    - cannedDesign: Sort glyphs into a design process friendly order.
    """,
)
@base_options()
def sort_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Sort the glyphs in a font file.
    """
    from foundrytools_cli_2.cli.glyphs.tasks import sort_glyphs as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
