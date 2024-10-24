import typing as t
from pathlib import Path

from afdko.otfautohint.__main__ import ACOptions, _validate_path
from afdko.otfautohint.autohint import FontInstance, fontWrapper, openFont
from fontTools.ttLib.tables.C_F_F_ import table_C_F_F_


def hint_font(in_file: Path, **kwargs: t.Dict[str, t.Any]) -> table_C_F_F_:
    """
    Applies hinting to an OpenType-PS font file and returns the hinted TTFont object.

    Args:
        in_file: Path to the font file.
        **kwargs: Additional options to populate the ACOptions object.

    Returns:
        table_C_F_F_: The hinted TTFont object.
    """
    options = ACOptions()
    for key, value in kwargs.items():
        setattr(options, key, value)

    in_file = _validate_path(in_file)
    font = openFont(in_file, options=options)
    font_instance = FontInstance(font=font, inpath=in_file, outpath=None)
    fw = fontWrapper(options=options, fil=[font_instance])
    fw.hint()
    return fw.fontInstances[0].font.ttFont["CFF "]
