# Copyright (C) 2024 twyleg
import logging
from pathlib import Path
from typing import List


def find_file(search_paths: List[Path], filenames: List[str], logm=None | logging.Logger) -> Path | None:
    for search_path in search_paths:
        for filename in filenames:
            potential_logging_config_filepath = search_path / filename
            if logm:
                logm.debug("Checking file: %s", potential_logging_config_filepath)
            if potential_logging_config_filepath.exists():
                logm.debug("Success, found file: %s", potential_logging_config_filepath)
                return potential_logging_config_filepath
    return None