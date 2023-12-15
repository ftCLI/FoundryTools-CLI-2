import sys

from functools import partialmethod

from loguru import logger


class LoggerFilter(dict):  # pylint: disable=too-few-public-methods
    """
    A custom logger filter that filters out log records below the given level.
    """

    def __init__(self, level: str) -> None:
        super().__init__()
        self.level = level

    def __call__(self, record: dict) -> bool:
        level_no = logger.level(self.level).no
        return record["level"].no >= level_no


logger_filter = LoggerFilter("INFO")

# Remove the default logger
logger.remove()

# Add a sink to the logger to print to stdout
logger.add(
    sys.stderr,
    filter=logger_filter,
    backtrace=False,
    colorize=True,
    format="[ <level>{level: <8}</level> ] " "<level>{message}</level>",
)

# Add a custom level to the logger
logger.level("SKIP", no=27, color="<light-black><bold>", icon="⏭️")
logger.__class__.skip = partialmethod(logger.__class__.log, "SKIP")  # type: ignore
logger.opt(colors=True)


__all__ = ["logger", "logger_filter", "LoggerFilter"]
