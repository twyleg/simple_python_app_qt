import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import jsonschema
from jsonschema.exceptions import ValidationError, SchemaError

from simple_python_app.helper import find_file

Config = Dict[str, Any]

class ConfigFileNotFoundError(FileNotFoundError):
    pass
class ConfigSchemaFileNotFoundError(FileNotFoundError):
    pass
class ConfigInvalidError(ValidationError):
    pass
class ConfigSchemaInvalidError(SchemaError):
    pass


logm = logging.getLogger(__name__)


def search_config_filepath(search_paths: List[Path], filenames: List[str]) -> Path | None:
    return find_file(search_paths, filenames, logm)

def init_config(config_filepath: Path, config_schema_filepath: Path | None = None) -> Config:

    logm.debug("Reading config from file: %s", config_filepath)

    config: Config | None = None
    config_schema: Dict[Any, Any] | None = None

    try:
        with open(config_filepath) as config_file:
            config = json.load(config_file)
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError(e)

    if config_schema_filepath:
        try:
            with open(config_schema_filepath) as json_schema_file:
                config_schema = json.load(json_schema_file)
        except FileNotFoundError as e:
            raise ConfigSchemaFileNotFoundError(e)

    try:
        jsonschema.validate(instance=config, schema=config_schema)
    except ValidationError as e:
        raise ConfigInvalidError(e)
    except SchemaError as e:
        raise ConfigSchemaInvalidError(e)

    return config


