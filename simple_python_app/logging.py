# Copyright (C) 2024 twyleg
from pathlib import Path

import logging
import logging.config
from typing import Any, Dict

import yaml


def init_logging(config_filepath: Path, logfile_filepath: Path | None = None, force_log_level: None | int = None) -> None:
    with open(config_filepath, "r") as f:
        d = yaml.safe_load(f)

        if force_log_level:
            __set_log_level(d, force_log_level)

        if logfile_filepath:
            __set_file_handler_filename(d, logfile_filepath)

        logging.config.dictConfig(d)


def __set_log_level(config_dict: Dict[str, Any], log_level: int) -> None:
    level_name = logging.getLevelName(log_level)
    if "handlers" in config_dict:
        for handler in config_dict["handlers"].values():
            handler["level"] = level_name
    if "loggers" in config_dict:
        for logger in config_dict["loggers"].values():
            logger["level"] = level_name
    if "root" in config_dict:
        config_dict["root"]["level"] = level_name


def __set_file_handler_filename(config_dict: Dict[str, Any], logfile_filepath: Path) -> None:
    if "handlers" in config_dict:
        for handler in config_dict["handlers"].values():
            if "class" in handler and handler["class"] == "logging.FileHandler":
                handler["filename"] = logfile_filepath
