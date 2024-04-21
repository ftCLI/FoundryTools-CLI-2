import typing as t

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import _MAC_LANGUAGE_CODES, _WINDOWS_LANGUAGE_CODES, NameRecord

from foundrytools_cli_2.lib.constants import T_NAME
from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class NameTable(DefaultTbl):
    """
    This class extends the fontTools ``name`` table to add some useful methods.
    """

    def __init__(self, ttfont: TTFont):
        """
        Initializes the ``name`` table handler.
        """
        super().__init__(ttfont=ttfont, table_tag=T_NAME)

    def get_debug_name(self, name_id: int):
        """
        Returns the name of the NameID for debugging purposes.
        """
        return self.table.getDebugName(nameID=name_id)

    def set_name(
        self,
        name_id: int,
        name_string: str,
        platform_id: t.Optional[int] = None,
        language_string: str = "en",
    ) -> None:
        """
        Adds a NameRecord to the ``name`` table of a font.

        Args:
            name_id (int): The NameID of the NameRecord to be set.
            name_string (str): The string to write to the NameRecord.
            platform_id (Optional[int]): The platformID of the NameRecord to be added. Defaults to
                None, which means that the NameRecord will be set for both platformIDs (1 and 3).
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
        self.table.addMultilingualName(
            names, ttFont=self.ttfont, nameID=name_id, windows=windows, mac=mac
        )

    def remove_names(
        self,
        name_ids: t.Iterable[int],
        platform_id: t.Optional[int] = None,
        language_string: t.Optional[str] = None,
    ) -> None:
        """
        Deletes the specified NameRecords from the ``name`` table of a font.

        Args:
            name_ids (Iterable[int]): A list of name IDs to delete.
            platform_id (Optional[int]): The platform ID of the name records to delete. Defaults to
                None. If None, both NameRecords with platformID 1 (Macintosh) and 3 (Windows) are
                deleted. If 1, only NameRecords with platformID 1 (Macintosh) are deleted. If 3,
                only NameRecords with platformID 3 (Windows) are deleted.
            language_string (Optional[str]): The language of the name records to delete. Defaults to
                None, which means that NameRecords in all languages are deleted.
        """

        names = self.filter_names(
            name_ids=set(name_ids), platform_id=platform_id, lang_string=language_string
        )
        for name in names:
            self.table.removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

    def remove_unused_names(self) -> None:
        """
        Removes unused NameRecords from the ``name`` table.
        """
        self.table.removeUnusedNames(self.ttfont)

    def find_replace(
        self,
        old_string: str,
        new_string: str,
        name_ids_to_process: t.Optional[t.Tuple[int]] = None,
        name_ids_to_skip: t.Optional[t.Tuple[int]] = None,
        platform_id: t.Optional[int] = None,
    ) -> None:
        """
        Finds and replaces occurrences of a string in the specified NameRecords of the ``name``
        table of a font.

        Args:
            old_string (str): The string to be replaced.
            new_string (str): The string to replace the ``old_string`` with.
            name_ids_to_process (tuple[int], optional): A tuple of name IDs to process. Default is
                an empty tuple, which means all nameIDs are processed.
            name_ids_to_skip (tuple[int], optional): A tuple of name IDs to skip. Default is an
                empty tuple, which means no nameIDs are skipped.
            platform_id (Optional[int]): The platform ID of the name records to process. Defaults to
                None, which means that NameRecords from all platforms are processed. If 1, only
                NameRecords with platformID 1 (Macintosh) are processed. If 3, only NameRecords with
                platformID 3 (Windows) are processed.
        """

        name_ids = self._get_name_ids_for_filter(
            name_ids_to_process=name_ids_to_process, name_ids_to_skip=name_ids_to_skip
        )
        names = self.filter_names(name_ids=name_ids, platform_id=platform_id)
        for name in names:
            if old_string in str(name):
                string = str(name).replace(old_string, new_string).replace("  ", " ").strip()
                self.table.setName(
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
        Appends a prefix, a suffix, or both to the NameRecords that match the nameID, platformID,
        and language string.

        Args:
            name_ids (Tuple[int]): A tuple of name IDs to process.
            platform_id (Optional[int]): The platform ID of the name records to process. Defaults to
                None, which means that NameRecords from all platforms are processed. If 1, only
                NameRecords with platformID 1 (Macintosh) are processed. If 3, only NameRecords with
                platformID 3 (Windows) are processed.
            language_string (Optional[str]): The language of the name records to process. Defaults
                to None, which means that NameRecords in all languages are processed.
            prefix (Optional[str]): The prefix to append to the NameRecords. Defaults to None.
            suffix (Optional[str]): The suffix to append to the NameRecords. Defaults to None.
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

            self.table.setName(
                string=string,
                nameID=name.nameID,
                platformID=name.platformID,
                platEncID=name.platEncID,
                langID=name.langID,
            )

    def strip_names(self) -> None:
        """
        Removes leading and trailing spaces from NameRecords in the ``name`` table.
        """
        for name in self.table.names:
            self.table.setName(
                str(name).strip(),
                name.nameID,
                name.platformID,
                name.platEncID,
                name.langID,
            )

    def remove_empty_names(self) -> None:
        """
        Removes empty NameRecords from the ``name`` table.
        """
        for name in self.table.names:
            if str(name).strip() == "":
                self.table.removeNames(
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
        all_name_ids = {name.nameID for name in self.table.names}
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
        Filters NameRecords based on the given parameters.

        Args:
            name_ids (Optional[List[int]]): A list of nameIDs to filter the name records. If None,
                all name records are considered.
            platform_id (Optional[int]): A platformID to filter the name records. If None, all
                platform IDs are considered.
            plat_enc_id (Optional[int]): A platEncID to filter the name records. If None, all
                platform encoding IDs are considered.
            lang_id (Optional[int]): A langID to filter the name records. If None, all language
                IDs are considered.
            lang_string (Optional[str]): A language string to filter the name records. If None, all
                language strings are considered.

        Returns:
            List[NameRecord]: A list of filtered NameRecords.
        """

        return [
            name
            for name in self.table.names
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
