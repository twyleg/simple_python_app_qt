# Copyright (C) 2024 twyleg
import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Callable, Any, Dict, List

import simple_python_app.config
from simple_python_app import __version__
from simple_python_app.helper import find_file
from simple_python_app.logging import init_logging
from simple_python_app.config import init_config


logm = logging.getLogger(__name__)

FILE_DIR = Path(__file__).parent


class GenericApplication:

    Config = simple_python_app.config.Config

    class LoggingType(Enum):
        DEFAULT_LOGGING = 1
        CUSTOM_LOGGING = 2

    def __init__(self,
                 application_name: str,
                 version: str,
                 logging_force_log_level: None | int = None,
                 logging_init_custom_logging_enabled=True,
                 logging_config_filepath: None | Path = None,
                 logging_config_search_paths: None | List[Path] = None,
                 logging_config_search_filenames: None | List[str] = None,
                 logging_default_format: None | str = None,
                 logging_default_date_format: None | str = None,
                 logging_logfile_output_dir: None | Path = None,
                 logging_logfile_filename: None | str = None,
                 application_config_init_enabled=True,
                 application_config_schema_filepath: None | Path = None,
                 application_config_filepath: Path | None = None,
                 application_config_search_paths: List[Path] | None = None,
                 application_config_search_filenames: List[str] | None = None):
        self._application_name = application_name
        self._version = version
        self._logging_force_log_level = logging_force_log_level
        self._logging_init_custom_logging_enabled = logging_init_custom_logging_enabled
        self._logging_config_filepath = logging_config_filepath
        self._logging_config_search_paths = logging_config_search_paths
        self._logging_config_search_filenames = logging_config_search_filenames
        self._logging_default_format = logging_default_format
        self._logging_default_date_format = logging_default_date_format
        self._logging_logfile_output_dir = logging_logfile_output_dir
        self._logging_logfile_filename = logging_logfile_filename
        self._application_config_init_enabled = application_config_init_enabled
        self._application_config_schema_filepath = application_config_schema_filepath
        self._application_config_filepath = application_config_filepath
        self._application_config_search_paths = application_config_search_paths
        self._application_config_search_filenames = application_config_search_filenames

        self._arg_parser = argparse.ArgumentParser(usage=f"{application_name} [<args>] <command>")
        self._args: None | argparse.Namespace = None
        self._add_arguments_method_available = hasattr(self, "add_arguments") and callable(self.add_arguments)
        self._subparser = None

        self._run_method_available = hasattr(self, "run") and callable(self.run)

        self.logm = logging.getLogger(application_name)
        self.config: None | Dict[str, Any] = None
        self.logging_type: None | GenericApplication.LoggingType = None
        self.logging_logfile_filepath: None | Path = None
        self.logging_config_filepath: None | Path = None

    def __exit(self, error=False) -> None:
        exit_code = -1 if error else 0
        logm.error("Exiting! (exit_code=%d)", exit_code)
        sys.exit(exit_code)

    def __init_argparse(self, argv: List[str]) -> None:

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
            help="Run with verbose logging (debug level).",
            action='store_true',
        )

        self._arg_parser.add_argument(
            "--logging-config",
            help="Logging config file to use.",
            type=str,
            default=None
        )

        self._arg_parser.add_argument(
            "--logging-dir",
            help="Application config file to use.",
            type=str,
            default=None
        )

        self._arg_parser.add_argument(
            "-c",
            "--config",
            help="Application config file to use.",
            type=str,
            default=None
        )

        try:
            if self._add_arguments_method_available:
                self.add_arguments(self._arg_parser)

            self._args = self._arg_parser.parse_args(argv)
        except BaseException as e:
            self.__init_default_logging()
            logm.exception(e)

    def __get_log_level(self) -> int:
        if self._args.verbose:
            return logging.DEBUG
        elif self._logging_force_log_level:
            return self._logging_force_log_level
        else:
            return None

    def __get_logfile_filepath(self) -> Path:
        def get_logfile_filename() -> str:
            if self._logging_logfile_filename:
                return self._logging_logfile_filename
            else:
                return "{:%Y%m%d%H%M%S}_{}.log".format(datetime.now(), self._application_name)

        def get_logfile_output_dir() -> Path:
            if self._args.logging_dir:
                return Path(self._args.logging_dir)
            elif self._logging_logfile_output_dir:
                return self._logging_logfile_output_dir
            else:
                return Path.cwd()

        logfile_output_dir = get_logfile_output_dir()
        logfile_filename = get_logfile_filename()
        return logfile_output_dir / logfile_filename

    def __init_custom_logging(self) -> None:

        def find_logging_config_filepath() -> Path | None:
            if self._args.logging_config:
                return self._args.logging_config
            elif self._logging_config_filepath:
                return self._logging_config_filepath
            else:
                search_paths = self._logging_config_search_paths if self._logging_config_search_paths else ([
                    Path.cwd(),
                    Path.home()
                ])
                search_filenames = self._logging_config_search_filenames if self._logging_config_search_filenames else ([
                    "logging.yaml",
                    "logging.yml",
                    f"{self._application_name}_logging.yaml",
                    f"{self._application_name}_logging.yml",
                ])
                return find_file(search_paths, search_filenames)

        forced_log_level = self.__get_log_level()
        logfile_filepath = self.__get_logfile_filepath()
        logging_custom_config_filepath = find_logging_config_filepath()

        if logging_custom_config_filepath:
            try:
                init_logging(logging_custom_config_filepath, logfile_filepath=logfile_filepath, force_log_level=forced_log_level)
                self.logging_type = GenericApplication.LoggingType.CUSTOM_LOGGING
                self.logging_logfile_filepath = logfile_filepath
                self.logging_config_filepath = logging_custom_config_filepath
            except (ValueError, TypeError, AttributeError, ImportError) as e:
                self.__init_default_logging()
                logm.error("Error reading logging config (%s):", self._logging_config_filepath)
                logm.error(e)
                self.__exit(error=True)
        else:
            self.__init_default_logging()

    def __init_default_logging(self) -> None:
        forced_log_level = self.__get_log_level()
        logfile_filepath = self.__get_logfile_filepath()
        default_logging_config_filepath = FILE_DIR / "resources/default_logging_config.yaml"

        init_logging(default_logging_config_filepath, logfile_filepath=logfile_filepath, force_log_level=forced_log_level)
        self.logging_type = GenericApplication.LoggingType.DEFAULT_LOGGING
        self.logging_logfile_filepath = logfile_filepath
        self.logging_config_filepath = default_logging_config_filepath

    def __init_application_config(self) -> None:

        def find_application_config_filepath() -> Path | None:
            if self._args.config:
                return self._args.config
            elif self._application_config_filepath:
                return self._application_config_filepath
            else:
                search_paths = self._application_config_search_paths if self._application_config_search_paths else ([
                    Path.cwd(),
                    Path.home()
                ])
                search_filenames = self._application_config_search_filenames if self._application_config_search_filenames else (
                [
                    f"{self._application_name}_config.json",
                    f".{self._application_name}_config.json",
                ])
                return find_file(search_paths, search_filenames)

        self._application_config_filepath = find_application_config_filepath()
        self.config = init_config(self._application_config_filepath, self._application_config_schema_filepath)

    def __init_stage_one(self, argv: List[str] | None) -> None:
        """"
        Init Stage One:

            First init stage doesn't depend on any user input, configs or anything else that needs be loaded
            at runtime.

            Init components:
            - argparse
        """

        if argv is None:
            argv = sys.argv
        self.__init_argparse(argv)

    def __init_stage_two(self) -> None:
        """"
        Init Stage Two:

            Second init stage takes runtime configs etc. into account
            at runtime.

            Init components:
            - custom logging OR default logging
        """

        if self._logging_init_custom_logging_enabled:
            self.__init_custom_logging()
        else:
            self.__init_default_logging()

    def __init_stage_three(self) -> None:
        """"
        Init Stage Three:

            Third init stage prints information and loads the application config. From this point on, log lines are
            provided.
        """

        logm.debug("simple_python_application framework started!")
        logm.debug("Framework version: %s", __version__)

        if self._logging_init_custom_logging_enabled:
            if self._logging_config_filepath:
                logm.debug("Init custom logging. Using config file: %s", self._logging_config_filepath)
            else:
                logm.debug("Init custom logging. No config provided or found, keeping default logging config!")
        else:
            logm.debug("Init custom logging disabled! Keeping default logging config!")

        if self._application_config_init_enabled:
            logm.debug("Config filepath: %s", self._application_config_filepath)
        else:
            logm.debug("Config init disabled! No project config available!")

        if self._add_arguments_method_available:
            logm.debug("User \"add_arguments()\" method provided. Custom command line arguments added to argparser!")
        else:
            logm.debug("No \"add_arguments()\" method provided. No custom command line arguments added to argparser!")
        logm.debug("Parsed command line arguments: %s", self._args)


        self.logm.info("%s (version=%s) started!", self._application_name, self._version)

        if self._application_config_init_enabled:
            self.__init_application_config()

    def start(self, argv: List[str] | None = None) -> int:

        try:
            self.__init_stage_one(argv)
            self.__init_stage_two()
            self.__init_stage_three()

            if self._run_method_available:
                    ret = self.run(self._args)
                    return ret if ret else 0
            else:
                logm.error("No \"run(args)\" method provided. Exiting!")
        except BaseException as e:
            logm.exception(e)
        return -1
