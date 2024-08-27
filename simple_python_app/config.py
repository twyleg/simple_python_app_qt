import json
import logging
from pathlib import Path
from typing import Dict, Any

import jsonschema

from simple_python_app.helper import find_file

Config = Dict[str, Any]

CONFIG_DEFAULT_FILENAMES = [
    "config.json"
]

CONFIG_DEFAULT_SEARCH_PATHS = [
    Path.cwd(),
    Path.home()
]

logm = logging.getLogger(__name__)


def init_config(config_filepath: Path | None = None, config_schema_filepath: Path | None = None) -> Config:

    if not config_filepath:
        logm.info("No explicit config location provided. Searching...")
        config_filepath = find_file(CONFIG_DEFAULT_SEARCH_PATHS, CONFIG_DEFAULT_FILENAMES, logm)

    if config_filepath:
        logm.info("Reading config from file: %s", config_filepath)

        with open(config_filepath) as config_file:
            config_dict = json.load(config_file)

            if config_schema_filepath:
                with open(config_schema_filepath) as json_schema_file:
                    config_json_schema = json.load(json_schema_file)
                    jsonschema.validate(instance=config_dict, schema=config_json_schema)
            return config_dict
    else:
        logm.error("Unable to find config file.")


        raise RuntimeError
