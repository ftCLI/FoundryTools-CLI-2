import typing as t
from pathlib import Path

import click
from foundrytools import Font

from foundrytools_cli_2.cli.logger import logger
from foundrytools_cli_2.cli.shared_callbacks import ensure_at_least_one_param
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner


@click.command(no_args_is_help=True)
@click.option(
    "--italic-angle",
    "italic_angle",
    type=float,
    help="""Sets the `italicAngle` value.""",
)
@click.option(
    "--ul-position",
    "underline_position",
    type=int,
    help="""Sets the `underlinePosition` value.""",
)
@click.option(
    "--ul-thickness",
    "underline_thickness",
    type=click.IntRange(min=0),
    help="""Sets the `underlineThickness` value.""",
)
@click.option(
    "--fixed-pitch/--no-fixed-pitch",
    "fixed_pitch",
    is_flag=True,
    default=None,
    help="""Sets or clears the `isFixedPitch` value.""",
)
@base_options()
def cli(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Utilities for editing the ``post`` table.
    """
    ensure_at_least_one_param(click.get_current_context())

    def task(
        font: Font,
        italic_angle: t.Optional[float] = None,
        underline_position: t.Optional[int] = None,
        underline_thickness: t.Optional[int] = None,
        fixed_pitch: t.Optional[bool] = None,
    ) -> bool:
        attrs = {
            "italic_angle": italic_angle,
            "underline_position": underline_position,
            "underline_thickness": underline_thickness,
            "fixed_pitch": fixed_pitch,
        }

        if all(value is None for value in attrs.values()):
            logger.error("No parameter provided")
            return False

        for attr, value in attrs.items():
            if value is not None:
                old_value = getattr(font.t_post, attr)
                logger.info(f"{attr}: {old_value} -> {value}")
                setattr(font.t_post, attr, value)

        return font.t_post.is_modified

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
