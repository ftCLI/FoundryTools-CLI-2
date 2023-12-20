import typing as t
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathvalidate import sanitize_filename

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def get_instance_file_name(font: Font, instance: NamedInstance) -> str:
    """
    Returns the file name of an instance of a font.

    Parameters:
        font (Font): The font object.
        instance (NamedInstance): The instance object.

    Returns:
        str: The file name of the instance.
    """
    if hasattr(instance, "postscriptNameID") and instance.postscriptNameID < 65535:
        instance_file_name = font.ttfont["name"].getDebugName(instance.postscriptNameID)

    else:
        if hasattr(instance, "subfamilyNameID") and instance.subfamilyNameID > 0:
            subfamily_name = font.ttfont["name"].getDebugName(instance.subfamilyNameID)
        else:
            subfamily_name = "_".join([f"{k}_{v}" for k, v in instance.coordinates.items()])

        if font.ttfont["name"].getBestFamilyName() is not None:
            family_name = font.ttfont["name"].getBestFamilyName()
        elif font.file is not None:
            family_name = font.file.stem
        else:
            family_name = "UnknownFamily"

        instance_file_name = f"{family_name}-{subfamily_name}".replace(" ", "")

    return sanitize_filename(instance_file_name)


def get_font_instances(
    font: Font, instances: t.Optional[t.List[NamedInstance]] = None
) -> t.List[NamedInstance]:
    """
    Get font instances.

    This method returns a list of font instances. If the `instances` parameter is not empty,
    it returns the provided instances as is. Otherwise, it calls the `get_instances()` method
    on the `font` object and returns the obtained instances.

    :param font: The font object to retrieve instances from.
    :type font: Font

    :param instances: The list of font instances. If provided, it will be returned as is.
        If not provided, the instances will be obtained from the `font` object.
    :type instances: List[NamedInstance]

    :return: The list of font instances.
    :rtype: List[NamedInstance]
    """
    return font.get_instances() if not instances else instances


def create_static_instance(
    font: Font, instance: NamedInstance, update_name_table: bool = True
) -> TTFont:
    """
    Creates a static instance of a variable font.

    Args:
        font (Font): The variable font.
        instance (NamedInstance): The instance definition.
        update_name_table (bool, optional): Specifies whether to update the font names table.
            Defaults to True.

    Returns:
        Font.ttfont.__class__: The static instance font.

    """
    return instantiateVariableFont(
        varfont=font.ttfont,
        axisLimits=instance.coordinates,
        inplace=False,
        overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS,
        optimize=True,
        updateFontNames=update_name_table,
    )


def get_output_dir(font: Font, output_dir: t.Optional[Path] = None) -> Path:
    """
    Get the output directory for the static font instances.

    :param font: The font object.
    :type font: Font
    :param output_dir: The directory where the static instances will be saved. Default is None.
    :type output_dir: Path
    :return: The output directory.
    :rtype: Path
    """
    if output_dir:
        return output_dir
    if font.file is None:
        raise ValueError("The font file path is not defined.")
    return font.file.parent


def get_output_file(
    font: Font, instance: NamedInstance, output_dir: Path, overwrite: bool = True
) -> Path:
    """
    Get the output file path for a given font instance.

    :param font: The font object.
    :type font: Font
    :param instance: The named instance object.
    :type instance: NamedInstance
    :param output_dir: The directory where the output file will be saved. Default is None.
    :type output_dir: Path
    :param overwrite: Whether to overwrite the output file if it already exists. Default is True.
    :type overwrite: bool
    :return: The output file path.
    :rtype: Path
    """
    instance_file_name = get_instance_file_name(font=font, instance=instance)
    extension = font.get_real_extension()
    out_file = makeOutputFileName(instance_file_name, output_dir, extension, overwrite)
    return Path(out_file)


def save_static_instance(out_file: Path, static_instance: TTFont) -> None:
    """
    Save Static Instance

    Saves a static instance of a Font.ttfont class to a file.

    Parameters:
    - out_file (Path): The path to the output file.
    - static_instance (Font.ttfont.__class__): The static instance of the Font.ttfont class to be
        saved.

    """
    static_instance.save(file=out_file)


def log_success(out_file: Path) -> None:
    """
    Log a success message indicating that a static instance has been saved to the specified output
        file.

    Parameters:
    out_file (str): The name of the output file where the static instance is saved.

    Returns:
    None

    Example:
    log_success("output.txt")
    """
    logger.success(f"Static instance saved to {out_file}")


def main(
    font: Font,
    instances: t.Optional[t.List[NamedInstance]] = None,
    output_dir: t.Optional[Path] = None,
    update_name_table: bool = True,
    overwrite: bool = True,
) -> None:
    """
    Generate static font instances based on given parameters.

    Args:
        font: The font object.
        instances: Optional. A list of NamedInstance objects representing the instances to process.
        output_dir: Optional. The directory where the static instances will be saved.
        update_name_table: Optional. Whether to update the name table of the font instances.
        overwrite: Optional. Whether to overwrite existing files in the output directory.

    Returns:
        None
    """
    instances = get_font_instances(font, instances)
    for instance in instances:
        static_instance = create_static_instance(font, instance, update_name_table)
        output_dir = get_output_dir(font, output_dir)
        out_file = get_output_file(font, instance, output_dir, overwrite)
        save_static_instance(out_file, static_instance)
        log_success(out_file)
