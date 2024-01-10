import typing as t

from fontTools.ttLib import TTFont, registerCustomTableClass
from fontTools.ttLib.tables._n_a_m_e import (
    _MAC_LANGUAGE_CODES,
    _WINDOWS_LANGUAGE_CODES,
    NameRecord,
    table__n_a_m_e,
)

registerCustomTableClass("name", "foundrytools_cli_2.lib.tables.name", "TableName")


class TableName(table__n_a_m_e):
    """
    This class extends the fontTools `name` table to add some useful methods.
    """

    def set_name(
        self,
        font: TTFont,
        name_id: int,
        name_string: str,
        platform_id: t.Optional[int] = None,
        language_string: str = "en",
    ) -> None:
        """
        Set the string of the specified NameRecord in the name table of a given font.

        Parameters:
            font (TTFont): The TrueType font object.
            name_id (int): The ID of the name to be set.
            name_string (str): The string value of the name to be set.
            platform_id (Optional[int]): The platform ID of the name record. Defaults to None.
            language_string (str): The language code of the name record. Defaults to "en".
        """

        # Remove the NameRecord before writing it to avoid duplicates
        self.remove_names(
            name_ids=(name_id,), platform_id=platform_id, language_string=language_string
        )

        if platform_id == 1:
            mac, windows = True, False
        elif platform_id == 3:
            mac, windows = False, True
        else:
            mac, windows = True, True

        names = {language_string: name_string}
        self.addMultilingualName(names, ttFont=font, nameID=name_id, windows=windows, mac=mac)

    def remove_names(
        self,
        name_ids: t.Iterable[int],
        platform_id: t.Optional[int] = None,
        language_string: t.Optional[str] = None,
    ) -> None:
        """
        Deletes all name records that match the given name_ids, optionally filtering by platform_id
        and/or language_string.

        :param name_ids: A list of name IDs to delete
        :param platform_id: The platform ID of the name records to delete
        :param language_string: The language of the name records to delete
        """

        names = self.filter_names(
            name_ids=set(name_ids), platform_id=platform_id, lang_string=language_string
        )
        for name in names:
            self.removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

    def find_replace(
        self,
        old_string: str,
        new_string: str,
        name_ids_to_process: t.Optional[t.Tuple[int]] = None,
        name_ids_to_skip: t.Optional[t.Tuple[int]] = None,
        platform_id: t.Optional[int] = None,
    ) -> None:
        """
        This function will find and replace a string in the specified namerecords.

        :param old_string: The string to be replaced
        :type old_string: str
        :param new_string: The string to replace the old string with
        :type new_string: str
        :param name_ids_to_process: A tuple of nameIDs to include in the search. If left blank, all
            nameIDs will be included
        :type name_ids_to_process: tuple
        :param name_ids_to_skip: A tuple of nameIDs to skip in the search. If left blank, no nameID
            will be skipped
        :type name_ids_to_skip: tuple
        :param platform_id: The platform ID of the name record to be changed
        :type platform_id: int
        """

        name_ids = self._get_name_ids_for_filter(
            name_ids_to_process=name_ids_to_process, name_ids_to_skip=name_ids_to_skip
        )
        names = self.filter_names(name_ids=name_ids, platform_id=platform_id)
        for name in names:
            if old_string in str(name):
                string = str(name).replace(old_string, new_string).replace("  ", " ").strip()
                self.setName(
                    string,
                    name.nameID,
                    name.platformID,
                    name.platEncID,
                    name.langID,
                )

    def append_prefix_suffix(
        self,
        name_ids: t.Tuple[int],
        platform_id: t.Optional[int] = None,
        language_string: t.Optional[str] = None,
        prefix: t.Optional[str] = None,
        suffix: t.Optional[str] = None,
    ) -> None:
        """
        Appends a prefix, a suffix, or both to the namerecords that match the name IDs, platform ID,
        and language string.

        :param name_ids: A list of name IDs to filter by
        :param platform_id: The platform ID of the namerecords where to append/prepend the string
        :param language_string: The language string to filter by
        :param prefix: The string to be added to the beginning of the namerecords
        :param suffix: The string to append to the end of the namerecords
        """

        names = self.filter_names(
            name_ids=set(name_ids), platform_id=platform_id, lang_string=language_string
        )

        for name in names:
            string = name.toUnicode()
            if prefix is not None:
                string = f"{prefix}{string}"
            if suffix is not None:
                string = f"{string}{suffix}"

            self.setName(
                string=string,
                nameID=name.nameID,
                platformID=name.platformID,
                platEncID=name.platEncID,
                langID=name.langID,
            )

    def strip_names(self) -> None:
        """
        Removes leading and trailing spaces from the names in the name table.
        """
        for name in self.names:
            self.setName(
                str(name).strip(),
                name.nameID,
                name.platformID,
                name.platEncID,
                name.langID,
            )

    def remove_empty_names(self) -> None:
        """
        Removes empty names from the name table.
        """
        for name in self.names:
            if str(name).strip() == "":
                self.removeNames(
                    nameID=name.nameID,
                    platformID=name.platformID,
                    platEncID=name.platEncID,
                    langID=name.langID,
                )

    def _get_name_ids_for_filter(
        self,
        name_ids_to_process: t.Optional[t.Iterable] = None,
        name_ids_to_skip: t.Optional[t.Iterable] = None,
    ) -> t.Set[int]:
        """
        Returns a set of name IDs to be used for filtering.
        """
        all_name_ids = {name.nameID for name in self.names}
        if name_ids_to_process:
            all_name_ids.intersection_update(name_ids_to_process)
        if name_ids_to_skip:
            all_name_ids.difference(name_ids_to_skip)
        return all_name_ids

    def filter_names(
        self,
        name_ids: t.Optional[t.Set[int]] = None,
        platform_id: t.Optional[int] = None,
        plat_enc_id: t.Optional[int] = None,
        lang_id: t.Optional[int] = None,
        lang_string: t.Optional[str] = None,
    ) -> t.List[NameRecord]:
        """
        Filters name records based on given parameters.

        Parameters:
            name_ids (Optional[List[int]]): A list of name IDs to filter the name records. If None,
                all name records are considered.
            platform_id (Optional[int]): A platform ID to filter the name records. If None, all
                platform IDs are considered.
            plat_enc_id (Optional[int]): A platform encoding ID to filter the name records. If None,
                all platform encoding IDs are considered.
            lang_id (Optional[int]): A language ID to filter the name records. If None, all language
                IDs are considered.
            lang_string (Optional[str]): A language string to filter the name records. If None, all
                language strings are considered.

        Returns:
            List[NameRecord]: A list of filtered name records.
        """

        return [
            name
            for name in self.names
            if (name_ids is None or name.nameID in name_ids)
            and (platform_id is None or name.platformID == platform_id)
            and (plat_enc_id is None or name.platEncID == plat_enc_id)
            and (lang_id is None or name.langID == lang_id)
            and (
                lang_string is None
                or name.langID
                in (
                    _MAC_LANGUAGE_CODES.get(lang_string.lower()),
                    _WINDOWS_LANGUAGE_CODES.get(lang_string.lower()),
                )
            )
        ]
