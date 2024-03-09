import typing as t


def add_options(options: t.List[t.Callable]) -> t.Callable:
    """
    Add options to a click command.

    :param options: a list of click options
    :return: a decorator that adds the options to a click command
    """

    def _add_options(func: t.Callable) -> t.Callable:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options
