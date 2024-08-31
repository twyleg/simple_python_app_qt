# Copyright (C) 2024 twyleg
from pathlib import Path

import sys
import logging
import logging.config
from typing import Any, Dict

import yaml

from simple_python_app.helper import find_file

LOGGING_DEFAULT_CONFIG_FILENAMES = [
    "logging.yaml",
    "logging.yml",
]

LOGGING_DEFAULT_CONFIG_SEARCH_PATHS = [
    Path.cwd(),
    Path.home()
]

LOGGING_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s]: %(message)s"
LOGGING_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logm = logging.getLogger(__name__)


def init_default_logging(format: None | str = None, date_format: None | str = None, verbose=False) -> None:
    if not format:
        format = LOGGING_DEFAULT_FORMAT
    if not date_format:
        date_format = LOGGING_DEFAULT_DATE_FORMAT
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, format=format, datefmt=date_format, level=level,
                        force=True)
    logm.debug("Initial default logging configured: Level=%s", logging.getLevelName(level))


def __set_level_to_debug(config_dict: Dict[str, Any]) -> None:
    if "handlers" in config_dict:
        for handler in config_dict["handlers"].values():
            handler["level"] = "DEBUG"
    if "loggers" in config_dict:
        for logger in config_dict["loggers"].values():
            logger["level"] = "DEBUG"
    if "root" in  config_dict:
        config_dict["root"]["level"] = "DEBUG"


def init_logging(config_filepath: Path = None, verbose=False) -> None:

    if not config_filepath:
        logm.debug("No explicit logging config location provided. Searching...")
        config_filepath = find_file(LOGGING_DEFAULT_CONFIG_SEARCH_PATHS, LOGGING_DEFAULT_CONFIG_FILENAMES, logm)

    if config_filepath:
        try:
            with open(config_filepath, 'r') as f:
                d = yaml.safe_load(f)

                if verbose:
                    __set_level_to_debug(d)

                logging.config.dictConfig(d)
            logm.debug("Logging config loaded from file: %s", config_filepath)
        except FileNotFoundError as e:
            logm.error("Unable to find logging config (%s):", config_filepath)
            logm.error(e)
            logm.error("Exiting...")
            sys.exit(-1)
        except (ValueError, TypeError, AttributeError, ImportError) as e:
            logm.error("Error reading logging config (%s):", config_filepath)
            logm.error(e)
            logm.error("Exiting...")
            sys.exit(-1)
    else:
        logm.debug("No logging config file provided. Keeping default settings!")

