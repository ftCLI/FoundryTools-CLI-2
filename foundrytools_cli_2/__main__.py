import click

from foundrytools_cli_2.cli.cff import cli as cff
from foundrytools_cli_2.cli.converter import cli as converter
from foundrytools_cli_2.cli.experimental import cli as experimental
from foundrytools_cli_2.cli.fix import cli as fix
from foundrytools_cli_2.cli.glyphs import cli as glyphs
from foundrytools_cli_2.cli.gsub import cli as gsub
from foundrytools_cli_2.cli.name import cli as name
from foundrytools_cli_2.cli.os_2 import cli as os_2
from foundrytools_cli_2.cli.otf import cli as otf
from foundrytools_cli_2.cli.post import cli as post
from foundrytools_cli_2.cli.print import cli as print_
from foundrytools_cli_2.cli.ttf import cli as ttf
from foundrytools_cli_2.cli.utils import cli as utils


@click.group(
    help="A collection of command line tools for working with font files.",
    commands={
        "cff": cff,
        "converter": converter,
        "experimental": experimental,
        "fix": fix,
        "glyphs": glyphs,
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
