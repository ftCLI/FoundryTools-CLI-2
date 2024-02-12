import click

from foundrytools_cli_2.cli.converter import cli as converter_cli
from foundrytools_cli_2.cli.name import cli as name_cli
from foundrytools_cli_2.cli.os_2 import cli as os_2_cli
from foundrytools_cli_2.cli.otf import cli as otf_cli


@click.group(
    commands={
        "converter": converter_cli,
        "name": name_cli,
        "os2": os_2_cli,
        "otf": otf_cli,
    }
)
@click.version_option()
def cli() -> None:  # pylint: disable=missing-function-docstring
    pass
