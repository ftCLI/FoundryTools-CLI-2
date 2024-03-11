import typing as t
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont
from pathvalidate import sanitize_filename

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def get_instance_file_name(font: Font, instance: NamedInstance) -> str:
    """
    Returns the file name of an instance of a font.

    Parameters:
        font (Font): The Font object.
        instance (NamedInstance): The instance object.

    Returns:
        str: The file name of the instance.
    """
    name_table = font.ttfont["name"]

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


def get_instances(
    font: Font, instances: t.Optional[t.List[NamedInstance]] = None
) -> t.List[NamedInstance]:
    """
    Returns a list of font instances. If the `instances` parameter is not empty, it returns the
    provided instances as is. Otherwise, it calls the `get_instances()` method on the `font` object
    and returns the obtained instances.

    Parameters:
        font (Font): The Font object.
        instances (Optional[List[NamedInstance]]): Optional. A list of font instances.
            Defaults to None.

    Returns:
        List[NamedInstance]: A list of font instances.
    """
    return instances if instances else font.get_instances()


def create_static_instance(
    font: Font, instance: NamedInstance, update_name_table: bool = True
) -> TTFont:
    """
    Creates a static instance of a variable font.

    Parameters:
        font (Font): The variable Font object.
        instance (NamedInstance): The instance definition.
        update_name_table (bool, optional): Specifies whether to update the font names table.
            Defaults to True.

    Returns:
        TTFont: The static instance.
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

    Parameters:
        font (Font): The Font object.
        output_dir (Optional[Path], optional): The output directory. Defaults to None.

    Returns:
        Path: The output directory.
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

    Parameters:
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

    Parameters:
        out_file (Path): The output file path.
        static_instance (TTFont): The static instance.

    Returns:
        None
    """
    static_instance.save(file=out_file)


def log_success(out_file: Path) -> None:
    """
    Log a success message indicating that a static instance has been saved to the specified output
    file.

    Parameters:
        out_file (Path): The output file path.

    Returns:
        None
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

    Parameters:
        font (Font): The Font object.
        instances (Optional[List[NamedInstance]], optional): A list of font instances.
            Defaults to None.
        output_dir (Optional[Path], optional): The output directory. Defaults to None.
        update_name_table (bool, optional): Specifies whether to update the font names table.
            Defaults to True.
        overwrite (bool, optional): Whether to overwrite existing files in the output directory.
            Defaults to True.

    Returns:
        None
    """
    instances = get_instances(font, instances)
    for instance in instances:
        static_instance = create_static_instance(font, instance, update_name_table)
        del static_instance["STAT"]
        static_instance["name"].removeUnusedNames(static_instance)
        output_dir = get_output_dir(font, output_dir)
        out_file = get_output_file(font, instance, output_dir, overwrite)
        save_static_instance(out_file, static_instance)
        log_success(out_file)
