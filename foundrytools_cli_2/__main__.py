import click

from foundrytools_cli_2.cli.converter import cli as converter_cli

cli = click.Group("foundrytools-cli-2", commands={"converter": converter_cli})