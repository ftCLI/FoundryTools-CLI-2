import contextlib
import typing as t

from fontTools.cffLib import PrivateDict, TopDict
from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.constants import T_CFF
from foundrytools_cli_2.lib.tables.default import DefaultTbl


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
            self._set_cff_font_names(font_name=font_name)
            del kwargs["fontNames"]

        top_dict_names: t.Dict[str, str] = {k: str(v) for k, v in kwargs.items() if v is not None}
        if top_dict_names:
            self._set_top_dict_names(top_dict_names)

    def _set_cff_font_names(self, font_name: str) -> None:
        """
        Sets the ``cff.fontNames`` value.

        Args:
            font_name: The font name to set.

        Returns:
            None
        """
        self.table.cff.fontNames = [font_name]

    def _set_top_dict_names(self, names: t.Dict[str, str]) -> None:
        """
        Sets the names of the 'CFF ' table.
        Args:
            names: The names to set.

        Returns:
            None
        """
        for attr_name, attr_value in names.items():
            setattr(self.top_dict, attr_name, attr_value)

    def del_names(self, **kwargs: t.Dict[str, str]) -> None:
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

    def find_replace(self, old_string: str, new_string: str) -> None:
        """
        Find and replace a string in the CFF table.

        Args:
            old_string: The string to find.
            new_string: The string to replace the old string with.

        Returns:
            None
        """
        self._find_replace_in_font_names(old_string=old_string, new_string=new_string)
        self._find_replace_in_top_dict(old_string=old_string, new_string=new_string)

    def _find_replace_in_font_names(self, old_string: str, new_string: str) -> None:
        """
        Find and replace a string in the fontNames field.

        Args:
            old_string: The string to find.
            new_string: The string to replace the old string with.

        Returns:
            None
        """
        cff_font_names = self.table.cff.fontNames[0]
        self.table.cff.fontNames = [
            cff_font_names.replace(old_string, new_string).replace("  ", " ").strip()
        ]

    def _find_replace_in_top_dict(self, old_string: str, new_string: str) -> None:
        """
        Find and replace a string in the topDictIndex[0] fields.
        Args:
            old_string: The string to find.
            new_string: The string to replace the old string with.

        Returns:
            None
        """
        top_dict = self.top_dict
        attr_list = [
            "version",
            "FullName",
            "FamilyName",
            "Weight",
            "Copyright",
            "Notice",
        ]

        for attr_name in attr_list:
            with contextlib.suppress(AttributeError):
                old_value = str(getattr(top_dict, attr_name))
                new_value = old_value.replace(old_string, new_string).replace("  ", " ").strip()
                setattr(top_dict, attr_name, new_value)
