from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class GsubTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    def __init__(self, ttfont: TTFont):
        super().__init__(ttfont, "GSUB")

    @property
    def features_list(self):
        """
        Get the list of GSUB features.
        """
        if hasattr(self.table, "FeatureList"):
            return [feature_record.FeatureTag for feature_record in self.table.FeatureList.FeatureRecord]
        return []

    @features_list.setter
    def features_list(self, value):
        """
        Set the list of GSUB features.
        """
        if hasattr(self.table, "FeatureList"):
            self.table.FeatureList.FeatureRecord = value

    def rename_feature(self, feature_tag: str, new_feature_tag: str) -> None:
        """
        Rename a GSUB feature.
        """

        if hasattr(self.table, "FeatureList"):
            for feature_record in self.table.FeatureList.FeatureRecord:
                if feature_record.FeatureTag == feature_tag:
                    feature_record.FeatureTag = new_feature_tag
