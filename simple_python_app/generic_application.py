# Copyright (C) 2024 twyleg
import logging
import argparse
import sys
from pathlib import Path
from typing import Callable, Any, Dict, List

import simple_python_app.config
from simple_python_app import __version__
from simple_python_app.logging import init_logging, init_default_logging
from simple_python_app.config import init_config, search_config_filepath


logm = logging.getLogger(__name__)


class GenericApplication:

    Config = simple_python_app.config.Config

    CONFIG_DEFAULT_SEARCH_PATHS = [
        Path.cwd(),
        Path.home()
    ]

    def __init__(self,
                 application_name: str,
                 version: str,
                 logging_init_default_logging_enabled=True,
                 logging_init_custom_logging_enabled=True,
                 logging_config_filepath: None | Path = None,
                 logging_default_format: None | str = None,
                 logging_default_date_format: None | str = None,
                 config_init_enabled=True,
                 config_schema_filepath: None | Path = None,
                 config_filepath: Path | None = None,
                 config_search_paths: List[Path] | None = None,
                 config_search_filenames: List[str] | None = None):
        self._application_name = application_name
        self._version = version
        self._logging_init_default_logging_enabled = logging_init_default_logging_enabled
        self._logging_init_custom_logging_enabled = logging_init_custom_logging_enabled
        self._logging_config_filepath = logging_config_filepath
        self._logging_default_format = logging_default_format
        self._logging_default_date_format = logging_default_date_format
        self._config_init_enabled = config_init_enabled
        self._config_schema_filepath = config_schema_filepath
        self._config_filepath = config_filepath
        self._config_search_paths = config_search_paths
        self._config_search_filenames = config_search_filenames

        self._arg_parser = argparse.ArgumentParser(usage=f"{application_name} [<args>] <command>")
        self._args: None | argparse.Namespace = None
        self._add_arguments_method_available = hasattr(self, "add_arguments") and callable(self.add_arguments)
        self._subparser = None

        self.logm = logging.getLogger(application_name)
        self.config: None | Dict[str, Any] = None

    def __init_argparse(self, argv: List[str]):

        self._arg_parser.add_argument(
            "-v",
            "--version",
            help="Show version and exit",
            action="version",
            version=self._version,
        )

        self._arg_parser.add_argument(
            "-vv",
            "--verbose",
            help="Run with verbose logging (debug).",
            action='store_true',
        )

        self._arg_parser.add_argument(
            "--logging-config",
            help="Logging config file to use.",
            type=str,
            default=None
        )

        self._arg_parser.add_argument(
            "-c",
            "--config",
            help="Config file to use.",
            type=str,
            default=None
        )

        if self._add_arguments_method_available:
            self.add_arguments(self._arg_parser)

        self._args = self._arg_parser.parse_args(argv)

    def __init_default_logging(self):
        verbose = self._args.verbose
        init_default_logging(format=self._logging_default_format, date_format=self._logging_default_date_format, verbose=verbose)

    def __init_custom_logging(self):
        verbose = self._args.verbose
        if self._args.logging_config:
            self._logging_config_filepath = Path(self._args.logging_config)
        init_logging(self._logging_config_filepath, verbose=verbose)

    def __init_config(self):
        if self._args.config:
            self._config_filepath = self._args.config
        elif not self._config_filepath:
            default_config_search_paths = [
                Path.cwd(),
                Path.home()
            ]
            default_config_search_filenames = [
                f"{self._application_name}_config.json",
                f".{self._application_name}_config.json",
            ]

            config_search_paths = self._config_search_paths if self._config_search_paths else default_config_search_paths
            config_search_filenames = self._config_search_filenames if self._config_search_filenames else default_config_search_filenames

            self._config_filepath = search_config_filepath(config_search_paths, config_search_filenames)

        self.config = init_config(self._config_filepath, self._config_schema_filepath)

    def __init_stage_one(self, argv: List[str] | None) -> None:
        if argv is None:
            argv = sys.argv
        self.__init_argparse(argv)
        if self._logging_init_default_logging_enabled:
            self.__init_default_logging()

        logm.debug("Init argparse")
        if self._logging_init_default_logging_enabled:
            logm.debug("Init default logging")
        else:
            logm.debug("Init default logging disabled!")

    def __init_stage_two(self) -> None:
        if self._logging_init_custom_logging_enabled:
            logm.debug("Init custom logging")
            self.__init_custom_logging()

        logm.debug("simple_python_application framework started!")
        logm.debug("Framework version: %s", __version__)

        if self._config_init_enabled:
            logm.debug("Init config")
            self.__init_config()

    def __init_stage_three(self) -> None:
        if self._logging_init_custom_logging_enabled:
            if self._logging_config_filepath:
                logm.debug("Init custom logging. Using config file: %s", self._logging_config_filepath)
            else:
                logm.debug("Init custom logging. No config provided or found, keeping default logging config!")
        else:
            logm.debug("Init custom logging disabled! Keeping default logging config!")

        if self._config_init_enabled:
            logm.debug("Config filepath: %s", self._config_filepath)
        else:
            logm.debug("Config init disabled! No project config available!")

        if self._add_arguments_method_available:
            logm.debug("User \"add_arguments()\" method provided. Custom command line arguments added to argparser!")
        else:
            logm.debug("No \"add_arguments()\" method provided. No custom command line arguments added to argparser!")
        logm.debug("Parsed command line arguments: %s", self._args)


        self.logm.info("%s (version=%s) started!", self._application_name, self._version)

    def start(self, argv: List[str] | None = None):

        try:
            self.__init_stage_one(argv)
            self.__init_stage_two()
            self.__init_stage_three()

            if hasattr(self, "run") and callable(self.run):
                    ret = self.run(self._args)
                    return ret if ret else 0
            else:
                logm.error("No \"run(args)\" method provided. Exiting!")
        except Exception as e:
            logm.exception(e)
        return -1
