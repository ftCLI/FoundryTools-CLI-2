from copy import deepcopy

from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.utils.misc import set_nth_bit, unset_nth_bit


class DefaultTbl:  # pylint: disable=too-few-public-methods
    """
    Base class for all table classes.
    """

    def __init__(self, font: TTFont, table_tag: str):
        """
        Initializes the table.
        """
        self.font = font
        self.table = font[table_tag]
        self.table_copy = deepcopy(self.table)

    @property
    def modified(self) -> bool:
        """
        Returns the modified status of the OS/2 table.
        """
        return self.table.compile(self.font) != self.table_copy.compile(self.font)

    def set_bit(self, field_name: str, value: bool, pos: int) -> None:
        """
        Set the bit at the given position in the given field of the table.
        """
        field_value = getattr(self.table, field_name)

        if value:
            new_field_value = set_nth_bit(field_value, pos)
        else:
            new_field_value = unset_nth_bit(field_value, pos)

        setattr(self.table, field_name, new_field_value)
