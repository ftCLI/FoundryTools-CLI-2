from pathlib import Path
from typing import Optional

import click
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance
from foundrytools import Font
from foundrytools.app.var2static import (
    BadInstanceError,
    UpdateNameTableError,
    Var2StaticError,
    check_update_name_table,
)
from foundrytools.app.var2static import (
    run as var2static,
)
from pathvalidate import sanitize_filename

from foundrytools_cli_2.cli.logger import logger


def _select_instance_coordinates(axes: list[Axis]) -> NamedInstance:
    click.secho("\nSelect coordinates:")
    selected_coordinates = {}
    selected_instance = NamedInstance()
    for a in axes:
        axis_tag = a.axisTag
        min_value = a.minValue
        max_value = a.maxValue
        coordinates = click.prompt(
            f"{axis_tag} ({min_value} - {max_value})",
            type=click.FloatRange(min_value, max_value),
        )
        selected_coordinates[axis_tag] = coordinates

    selected_instance.coordinates = selected_coordinates

    return selected_instance


def main(
    var_font: Font,
    select_instance: bool = False,
    overlap: int = 1,
    output_dir: Optional[Path] = None,
    overwrite: bool = True,
) -> None:
    """
    Generate static font instances based on given parameters.

    Args:
        var_font (Font): The variable ``Font`` object.
        select_instance (bool, optional): Whether to select a single instance with custom axis
            values.
        overlap (int, optional): The overlap mode. Defaults to 1 (KEEP_AND_SET_FLAGS).
        output_dir (Optional[Path], optional): The output directory. Defaults to ``None``.
        overwrite (bool, optional): Whether to overwrite existing files in the output directory.
            Defaults to ``True``.
    """
    if select_instance:
        axes = var_font.t_fvar.table.axes
        selected_instance = _select_instance_coordinates(axes)
        requested_instances = [selected_instance]
    else:
        requested_instances = var_font.t_fvar.table.instances

    if not requested_instances:
        raise ValueError("No instances found in the variable font.")

    if output_dir is None:
        if var_font.file is None:
            raise ValueError("Cannot determine the output directory.")
        output_dir = var_font.file.parent

    try:
        check_update_name_table(var_font)
        update_font_names = True
    except UpdateNameTableError as e:
        logger.warning(f"The name table cannot be updated: {e}")
        update_font_names = False

    for i, instance in enumerate(requested_instances, start=1):
        logger.info(f"Exporting instance {i} of {len(requested_instances)}")
        try:
            static_font, file_name = var2static(var_font, instance, update_font_names, overlap)
        except (BadInstanceError, Var2StaticError) as e:
            logger.opt(colors=True).error(f"<lr>{e.__module__}.{type(e).__name__}</lr>: {e}")
            continue

        out_file = makeOutputFileName(sanitize_filename(file_name), output_dir, overWrite=overwrite)
        static_font.save(out_file)
        static_font.close()
        logger.success(f"Static instance saved to {out_file}\n")
