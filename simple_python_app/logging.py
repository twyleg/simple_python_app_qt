# Copyright (C) 2024 twyleg
from pathlib import Path

import sys
import os
import logging
import logging.config
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

LOGGING_DEFAULT_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"

logm = logging.getLogger("init_logging")


def init_logging(config_filepath: Path = None, verbose=False) -> None:

    if not config_filepath:
        logm.info("No explicit logging config location provided. Searching...")
        config_filepath = find_file(LOGGING_DEFAULT_CONFIG_SEARCH_PATHS, LOGGING_DEFAULT_CONFIG_FILENAMES, logm)

    if config_filepath:
        try:
            with open(config_filepath, 'r') as f:
                d = yaml.safe_load(f)
                logging.config.dictConfig(d)
            logm.info("Logging config loaded from file: %s", config_filepath)
        except FileNotFoundError as e:
            logm.error("Unable to find logging config (%s):", config_filepath)
            logm.error(e)
            logm.error("Exiting...")
            sys.exit(os.EX_CONFIG)
        except (ValueError, TypeError, AttributeError, ImportError) as e:
            logm.error("Error reading logging config (%s):", config_filepath)
            logm.error(e)
            logm.error("Exiting...")
            sys.exit(os.EX_CONFIG)
    else:
        logging.basicConfig(stream=sys.stdout, format=LOGGING_DEFAULT_FORMAT, level=logging.INFO, force=True)
        logm.info("No logging config file provided. Using default settings!")

    if verbose:
        pass
