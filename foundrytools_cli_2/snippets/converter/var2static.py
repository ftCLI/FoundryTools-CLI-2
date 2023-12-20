import typing as t
from pathlib import Path

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathvalidate import sanitize_filename

from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.logger import logger


def get_instance_file_name(font: Font, instance: NamedInstance) -> str:
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


def get_font_instances(font: Font, instances: t.List[NamedInstance]) -> t.List[NamedInstance]:
    return font.get_instances() if not instances else instances


def create_static_instance(
        font: Font, instance: NamedInstance, update_name_table: bool = True
) -> Font.ttfont.__class__:
    return instantiateVariableFont(
        varfont=font.ttfont,
        axisLimits=instance.coordinates,
        inplace=False,
        overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS,
        optimize=True,
        updateFontNames=update_name_table,
    )


def get_output_file(
        font: Font, instance: NamedInstance, output_dir: Path, overwrite: bool = True
) -> Path:
    instance_file_name = get_instance_file_name(font=font, instance=instance)
    output_dir = Path(output_dir) if output_dir else font.file.parent
    extension = font.get_real_extension()
    out_file = makeOutputFileName(instance_file_name, output_dir, extension, overwrite)
    return Path(out_file)


def save_static_instance(out_file: Path, static_instance: Font.ttfont.__class__):
    static_instance.save(file=out_file)


def log_success(out_file):
    logger.success(f"Static instance saved to {out_file}")


def main(
        font: Font,
        instances: t.Optional[t.List[NamedInstance]] = None,
        output_dir: t.Optional[Path] = None,
        update_name_table: bool = True,
        overwrite: bool = True,
) -> None:
    instances = get_font_instances(font, instances)
    for instance in instances:
        static_instance = create_static_instance(font, instance, update_name_table)
        out_file = get_output_file(font, instance, output_dir, overwrite)
        save_static_instance(out_file, static_instance)
        log_success(out_file)
