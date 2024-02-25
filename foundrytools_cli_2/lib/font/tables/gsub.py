from fontTools.ttLib import TTFont

from foundrytools_cli_2.lib.font.tables.default import DefaultTbl


class GsubTable(DefaultTbl):  # pylint: disable=too-few-public-methods
    """
    This class extends the fontTools `GSUB` table to add some useful methods.
    """
    def __init__(self, ttfont: TTFont) -> None:
        super().__init__(ttfont, "GSUB")

    def rename_feature(self, feature_tag: str, new_feature_tag: str) -> None:
        """
        Rename a GSUB feature.
        """

        if hasattr(self.table, "FeatureList"):
            for feature_record in self.table.FeatureList.FeatureRecord:
                if feature_record.FeatureTag == feature_tag:
                    feature_record.FeatureTag = new_feature_tag
