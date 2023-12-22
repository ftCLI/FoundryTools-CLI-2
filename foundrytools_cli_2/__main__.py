import click

from foundrytools_cli_2.cli.converter import cli as converter_cli
from foundrytools_cli_2.cli.otf import cli as otf_cli
from foundrytools_cli_2.cli.name import cli as name_cli


@click.group(
    commands={
        "converter": converter_cli,
        "name": name_cli,
        "otf": otf_cli,
    }
)
@click.version_option()
def cli() -> None:  # pylint: disable=missing-function-docstring
    pass
