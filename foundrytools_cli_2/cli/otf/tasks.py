import typing as t

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.lib.font import Font


def add_extremes(font: Font, drop_hinting_data: bool = False, subroutinize: bool = True) -> None:
    """
    Adds extreme points to the outlines of an OpenType-PS font.

    Args:
        font (Font): The font to add extreme points to.
        drop_hinting_data: Whether to drop hinting data.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Adding extremes")
    font.ps_add_extremes(drop_hinting_data=drop_hinting_data)
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True


def autohint(font: Font, subroutinize: bool = True, **kwargs: t.Dict[str, t.Any]) -> None:
    """
    Autohint an OpenType-PS font with ``afdko.autohint``.

    Args:
        font (Font): The font to autohint.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Autohinting")
    font.ps_autohint(**kwargs)
    if subroutinize:
        font.reload()  # DO NOT REMOVE
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True


def dehint(font: Font, drop_hinting_data: bool = False, subroutinize: bool = True) -> None:
    """
    Dehint an OpenType-PS font.

    Args:
        font (Font): The font to dehint.
        drop_hinting_data (bool): Whether to drop hinting data.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Dehinting")
    font.ps_dehint(drop_hinting_data=drop_hinting_data)
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True


def check_outlines(font: Font, subroutinize: bool = True) -> None:
    """
    Check the outlines of an OpenType-PS font with ``afdko.checkoutlinesufo``.

    Args:
        font (Font): The font to check the outlines of.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Checking outlines")
    font.ps_check_outlines()
    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
    font.modified = True


def round_coordinates(font: Font, subroutinize: bool = True) -> None:
    """
    Round the coordinates of the glyphs in an OpenType-PS font.

    Args:
        font (Font): The font to round the coordinates of.
        subroutinize (bool): Whether to subroutinize the font.
    """
    logger.info("Rounding coordinates")
    result = font.ps_round_coordinates()
    if not result:
        return

    font.modified = True
    logger.info(f"{len(result)} glyphs were modified")

    if subroutinize:
        logger.info("Subroutinizing")
        font.ps_subroutinize()
