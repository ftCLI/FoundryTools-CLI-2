import typing as t
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont
from pathvalidate import sanitize_filename

from foundrytools_cli_2.lib.constants import (
    CVAR_TABLE_TAG,
    GSUB_TABLE_TAG,
    NAME_TABLE_TAG,
    STAT_TABLE_TAG,
)
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import NameTable
from foundrytools_cli_2.lib.logger import logger


def get_instance_file_name(font: Font, instance: NamedInstance) -> str:
    """
    Returns the file name of an instance of a font.

    Args:
        font (Font): The Font object.
        instance (NamedInstance): The instance object.

    Returns:
        str: The file name of the instance.
    """

    name_table = font.ttfont[NAME_TABLE_TAG]

    if hasattr(instance, "postscriptNameID") and instance.postscriptNameID < 65535:
        instance_file_name = name_table.getDebugName(instance.postscriptNameID)
        return sanitize_filename(instance_file_name)

    if hasattr(instance, "subfamilyNameID") and instance.subfamilyNameID > 0:
        subfamily_name = name_table.getDebugName(instance.subfamilyNameID)
    else:
        subfamily_name = "_".join([f"{k}_{v}" for k, v in instance.coordinates.items()])

    if name_table.getBestFamilyName() is not None:
        family_name = name_table.getBestFamilyName()
    elif font.file is not None:
        family_name = font.file.stem
    else:
        family_name = "UnknownFamily"

    instance_file_name = f"{family_name}-{subfamily_name}".replace(" ", "")

    return sanitize_filename(instance_file_name)


def check_update_name_table(variable_font: Font) -> bool:
    """
    Checks whether the name table can be updated.

    Args:
        variable_font (Font): The ``Font`` object representing the variable font.

    Returns:
        bool: ``True`` if the name table can be updated, otherwise ``False``.
    """

    if STAT_TABLE_TAG not in variable_font.ttfont:
        logger.warning("The name table cannot be updated: There is no STAT table.")
        return False

    stat_table = variable_font.ttfont[STAT_TABLE_TAG].table
    if not stat_table.AxisValueArray:
        logger.warning("The name table cannot be updated: There are no STAT Axis Values.")
        return False

    try:
        create_static_instance(
            variable_font=variable_font,
            instance=variable_font.get_instances()[0],
            update_name_table=True,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.warning(f"The name table cannot be updated: {e}")
        return False

    return True


def create_static_instance(
    variable_font: Font, instance: NamedInstance, update_name_table: bool = True
) -> TTFont:
    """
    Creates a static instance of a variable font.

    Args:
        variable_font (Font): The variable ``Font`` object.
        instance (NamedInstance): The instance definition.
        update_name_table (bool, optional): Specifies whether to update the font names table.
            Defaults to True.

    Returns:
        TTFont: The static instance.
    """

    return instantiateVariableFont(
        varfont=variable_font.ttfont,
        axisLimits=instance.coordinates,
        inplace=False,
        overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS,
        optimize=True,
        updateFontNames=update_name_table,
    )


def get_ui_name_ids(font: TTFont) -> list:
    """
    Returns a list of all the UI name IDs in the font's GSUB table

    Args:
        font (TTFont): The font object.

    Returns:
        list: A list of UI name IDs.
    """

    if GSUB_TABLE_TAG not in font:
        return []
    ui_name_ids = []
    for record in font[GSUB_TABLE_TAG].table.FeatureList.FeatureRecord:
        if record.Feature.FeatureParams:
            ui_name_ids.append(record.Feature.FeatureParams.UINameID)
    return sorted(set(ui_name_ids))


def reorder_ui_name_ids(font: TTFont) -> None:
    """
    Takes the IDs of the UI names in the name table and reorders them to start at 256

    Args:
        font (TTFont): The font object.
    """

    if GSUB_TABLE_TAG not in font:
        return

    ui_name_ids = get_ui_name_ids(font=font)
    if not ui_name_ids:
        return

    name_table = font[NAME_TABLE_TAG]
    for count, value in enumerate(ui_name_ids, start=256):
        for n in name_table.names:
            if n.nameID == value:
                n.nameID = count
        for record in font[GSUB_TABLE_TAG].table.FeatureList.FeatureRecord:
            if record.Feature.FeatureParams and record.Feature.FeatureParams.UINameID == value:
                record.Feature.FeatureParams.UINameID = count


def post_process_static_instance(static_instance: TTFont) -> None:
    """
    Post-processes a static instance. Removes the ``STAT`` and ``CVAR`` tables, deletes unused
    names from the ``name`` table and reorders the UI name IDs.

    Args:
        static_instance (TTFont): The static instance.
    """

    if STAT_TABLE_TAG in static_instance:
        del static_instance[STAT_TABLE_TAG]
    if CVAR_TABLE_TAG in static_instance:
        del static_instance[CVAR_TABLE_TAG]

    name_table = NameTable(font=static_instance)
    name_table.remove_unused_names()
    name_table.remove_names(name_ids=[25])

    reorder_ui_name_ids(static_instance)


def get_output_dir(variable_font: Font, output_dir: t.Optional[Path] = None) -> Path:
    """
    Get the output directory for the static font instances.

    Args:
        variable_font (Font): The Font object.
        output_dir (Optional[Path], optional): The output directory. Defaults to None.

    Returns:
        Path: The output directory.
    """

    if output_dir:
        return output_dir
    if variable_font.file is None:
        raise ValueError("The font file path is not defined.")
    return variable_font.file.parent


def get_output_file(
    font: Font, instance: NamedInstance, output_dir: Path, overwrite: bool = True
) -> Path:
    """
    Get the output file path for a given font instance.

    Args:
        font (Font): The Font object.
        instance (NamedInstance): The instance object.
        output_dir (Path): The output directory.
        overwrite (bool, optional): Whether to overwrite existing files in the output directory.
            Defaults to True.

    Returns:
        Path: The output file path.
    """

    instance_file_name = get_instance_file_name(font=font, instance=instance)
    extension = font.get_real_extension()
    out_file = makeOutputFileName(instance_file_name, output_dir, extension, overwrite)
    return Path(out_file)


def save_static_instance(out_file: Path, static_instance: TTFont) -> None:
    """
    Save the static instance to the specified output file.

    Args:
        out_file (Path): The output file path.
        static_instance (TTFont): The static instance.
    """

    static_instance.save(file=out_file)


def log_success(out_file: Path) -> None:
    """
    Log a success message indicating that a static instance has been saved to the specified output
    file.

    Args:
        out_file (Path): The output file path.
    """

    logger.success(f"Static instance saved to {out_file}")


def main(
    variable_font: Font,
    requested_instances: t.Optional[t.List[NamedInstance]] = None,
    update_name_table: bool = True,
    output_dir: t.Optional[Path] = None,
    overwrite: bool = True,
) -> None:
    """
    Generate static font instances based on given parameters.

    Args:
        variable_font (Font): The variable ``Font`` object.
        requested_instances (Optional[List[NamedInstance]], optional): A list of font instances.
            Defaults to ``None``.
        output_dir (Optional[Path], optional): The output directory. Defaults to ``None``.
        update_name_table (bool, optional): Specifies whether to update the font names table.
            Defaults to ``True``.
        overwrite (bool, optional): Whether to overwrite existing files in the output directory.
            Defaults to ``True``.
    """

    if not requested_instances:
        requested_instances = variable_font.get_instances()

    output_dir = get_output_dir(variable_font, output_dir)

    if update_name_table:
        update_name_table = check_update_name_table(variable_font)

    for i, instance in enumerate(requested_instances, start=1):
        logger.info(f"Exporting instance {i} of {len(requested_instances)}")
        static_instance = create_static_instance(variable_font, instance, update_name_table)
        post_process_static_instance(static_instance)

        out_file = get_output_file(variable_font, instance, output_dir, overwrite)
        save_static_instance(out_file, static_instance)
        log_success(out_file)
