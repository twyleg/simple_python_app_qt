import logging
import argparse
import sys
from pathlib import Path
from typing import Callable, Any, Dict, List

import simple_python_app.config
from simple_python_app.logging import init_logging
from simple_python_app.config import init_config

logm = logging.getLogger(__name__)


class GenericApplication:

    Config = simple_python_app.config.Config

    def __init__(self,
                 application_name: str,
                 version: str,
                 init_logging=True,
                 init_config=True,
                 config_schema_filepath: None | Path = None):
        self._application_name = application_name
        self._version = version
        self._init_logging = init_logging
        self._init_config = init_config
        self._config_schema_filepath = config_schema_filepath
        self._config: None | Dict[Any, Any] = None
        self._arg_parser = argparse.ArgumentParser(usage=f"{application_name} [<args>] <command>")
        self._args: None | argparse.Namespace = None
        self._subparser = None
        self.logm = logging.getLogger(application_name)

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
            "-c",
            "--config",
            help=f"Config file to use.",
            type=str,
            default=None
        )

        try:
            self.add_arguments(self._arg_parser)
        except AttributeError:
            logm.warning("No \"add_arguments()\" method provided. Skipping!")

        self._args = self._arg_parser.parse_args(argv[1:2])

    def __init_logging(self):
        verbose = self._args.verbose
        init_logging(verbose=verbose)

    def __init_config(self):
        config_filepath = self._args.config if self._args.config else None
        self.config = init_config(config_filepath, self._config_schema_filepath)

    def start(self, argv: List[str]):

        self.__init_argparse(argv)

        if self._init_logging:
            self.__init_logging()
        if self._init_config:
            self.__init_config()

        logm.info("%s started!", self._application_name)
        try:
            self.run(self._args)
        except AttributeError:
            logm.error("No \"run()\" method provided. Exiting!")
