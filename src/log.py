import sys
import logging
from typing import Optional, Dict

from colorama import Fore, Back, Style


class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    def __init__(
        self, *args, colors: Optional[Dict[str, str]] = None, **kwargs
    ) -> None:
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, "")
        record.reset = Style.RESET_ALL

        return super().format(record)


formatter = ColoredFormatter(
    "{asctime} |{color} {levelname:8} {reset}| {name} | {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    colors={
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
    },
)


formatter_simple = ColoredFormatter(
    "{color}{message}{reset}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    colors={
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
    },
)

formatter_module = ColoredFormatter(
    "{asctime} |{color} {levelname:8} {reset}| {name} | {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    colors={
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
    },
)


def get_handler(log_type="default"):
    if log_type == "default":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    elif log_type == "simple":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter_simple)
    elif log_type == "module":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter_module)
    else:
        raise ValueError("Invalid log_type, must be either `default` or `simple`.")

    return handler
