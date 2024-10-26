from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font
from foundrytools_cli_2.lib.font.tables import GsubTable


def main(font: Font, old_feature_name: str, new_feature_name: str) -> None:
    """
    Remap GSUB features.

    Args:
        font (Font): The Font object representing the font file.
        old_feature_name (str): The old feature name.
        new_feature_name (str): The new feature name.
    """
    if "GSUB" not in font.ttfont:
        logger.error("GSUB table not found")
        return

    gsub = GsubTable(font.ttfont)
    if hasattr(gsub.table.table, "FeatureList"):
        for feature_record in gsub.table.table.FeatureList.FeatureRecord:
            if feature_record.FeatureTag == old_feature_name:
                feature_record.FeatureTag = new_feature_name
                font.modified = True
        return

    logger.info(f"GSUB feature '{old_feature_name}' not found")
