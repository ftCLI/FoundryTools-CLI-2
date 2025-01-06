import click

from foundrytools_cli_2.cli.commands.cff import cli as cff
from foundrytools_cli_2.cli.commands.cmap import cli as cmap
from foundrytools_cli_2.cli.commands.converter import cli as converter
from foundrytools_cli_2.cli.commands.font import cli as font
from foundrytools_cli_2.cli.commands.gsub import cli as gsub
from foundrytools_cli_2.cli.commands.name import cli as name
from foundrytools_cli_2.cli.commands.otf import cli as otf
from foundrytools_cli_2.cli.commands.post import cli as post
from foundrytools_cli_2.cli.commands.print import cli as print_
from foundrytools_cli_2.cli.commands.ttf import cli as ttf
from foundrytools_cli_2.cli.commands.utils import cli as utils
from foundrytools_cli_2.cli.fix import cli as fix
from foundrytools_cli_2.cli.os_2 import cli as os_2


@click.group(
    help="A collection of command line tools for working with font files.",
    commands={
        "cff": cff,
        "cmap": cmap,
        "converter": converter,
        "fix": fix,
        "font": font,
        "gsub": gsub,
        "name": name,
        "os2": os_2,
        "otf": otf,
        "post": post,
        "print": print_,
        "ttf": ttf,
        "utils": utils,
    },
)
@click.version_option()
def cli() -> None:  # pylint: disable=missing-function-docstring
    pass
