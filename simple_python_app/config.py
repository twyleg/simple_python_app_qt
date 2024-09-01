# Copyright (C) 2024 twyleg
import json
import logging
import jsonschema
from pathlib import Path
from typing import Dict, Any, List

from simple_python_app.helper import find_file

Config = Dict[str, Any]


logm = logging.getLogger(__name__)


def search_config_filepath(search_paths: List[Path], filenames: List[str]) -> Path | None:
    return find_file(search_paths, filenames, logm)

def init_config(config_filepath: Path, config_schema_filepath: Path | None = None) -> Config:

    logm.debug("Reading config from file: %s", config_filepath)

    with open(config_filepath) as config_file:
        config = json.load(config_file)

        if config_schema_filepath:
            with open(config_schema_filepath) as json_schema_file:
                config_schema = json.load(json_schema_file)
                jsonschema.validate(instance=config, schema=config_schema)

        return config


