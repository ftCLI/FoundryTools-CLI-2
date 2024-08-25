import contextlib
import typing as t

from fontTools.cffLib import CharStrings, PrivateDict, TopDict
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CFF
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class CFFTable(DefaultTbl):
    """
    This class extends the fontTools ``CFF `` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont) -> None:
        """
        Initializes the ``CFF `` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_CFF)

    @property
    def top_dict(self) -> TopDict:
        """
        Returns the topDictIndex field of the 'CFF ' table.
        """
        return self.table.cff.topDictIndex[0]

    @property
    def private_dict(self) -> PrivateDict:
        """
        Returns the private field of the 'CFF ' table.
        """
        return self.top_dict.Private

    @property
    def charstrings(self) -> CharStrings:
        """
        Returns the charStrings field of the 'CFF ' table.
        """
        return self.top_dict.CharStrings

    def set_names(self, **kwargs: t.Dict[str, str]) -> None:
        """
        Sets the cff.fontNames[0] and topDictIndex[0] values.

        Args:
            **kwargs: The names to set.

        Returns:
            None
        """
        font_name = str(kwargs.get("fontNames"))
        if font_name:
            self.set_cff_font_names(font_name=font_name)
            del kwargs["fontNames"]

        top_dict_names: t.Dict[str, str] = {k: str(v) for k, v in kwargs.items() if v is not None}
        if top_dict_names:
            self.set_top_dict_names(top_dict_names)

    def set_cff_font_names(self, font_name: str) -> None:
        """
        Sets the ``cff.fontNames`` value.

        Args:
            font_name: The font name to set.

        Returns:
            None
        """
        self.table.cff.fontNames = [font_name]

    def set_top_dict_names(self, names: t.Dict[str, str]) -> None:
        """
        Sets the names of the 'CFF ' table.
        Args:
            names: The names to set.

        Returns:
            None
        """
        for attr_name, attr_value in names.items():
            setattr(self.top_dict, attr_name, attr_value)

    def del_top_dict_names(self, **kwargs: t.Dict[str, str]) -> None:
        """
        Deletes names from topDictIndex[0]
        Args:
            kwargs: The names to delete.

        Returns:
            None
        """
        for k, v in kwargs.items():
            if v is not None:
                with contextlib.suppress(KeyError):
                    del self.top_dict.rawDict[k]
