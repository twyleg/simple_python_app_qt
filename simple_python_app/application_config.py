# Copyright (C) 2024 twyleg
import json
import logging
import jsonschema
from pathlib import Path
from typing import Dict, Any


ApplicationConfig = Dict[str, Any]


logm = logging.getLogger(__name__)


def init_application_config(config_filepath: Path, config_schema_filepath: Path | None = None) -> ApplicationConfig:
    with open(config_filepath) as config_file:
        config = json.load(config_file)

        if config_schema_filepath:
            with open(config_schema_filepath) as json_schema_file:
                config_schema = json.load(json_schema_file)
                jsonschema.validate(instance=config, schema=config_schema)

        return config
