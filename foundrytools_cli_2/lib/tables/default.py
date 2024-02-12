from copy import deepcopy

from fontTools.ttLib import TTFont


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
