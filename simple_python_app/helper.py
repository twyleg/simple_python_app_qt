# Copyright (C) 2024 twyleg
from pathlib import Path
from typing import List


def find_file(search_paths: List[Path], filenames: List[str]) -> Path | None:
    for search_path in search_paths:
        for filename in filenames:
            potential_logging_config_filepath = search_path / filename
            if potential_logging_config_filepath.exists():
                return potential_logging_config_filepath
    return None
