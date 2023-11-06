import click

from foundrytools_cli_2.cli.converter import cli as converter_cli


@click.group(
    commands={
        "converter": converter_cli,
    }
)
@click.version_option()
def cli() -> None:  # pylint: disable=missing-function-docstring
    pass
