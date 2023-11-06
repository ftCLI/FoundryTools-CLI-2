import click

from foundrytools_cli_2.cli.converter import cli as converter_cli

cli = click.Group("ft-cli", commands={"converter": converter_cli})
