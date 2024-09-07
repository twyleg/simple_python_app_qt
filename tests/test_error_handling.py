# Copyright (C) 2024 twyleg
# fmt: off
import argparse
from pathlib import Path

from simple_python_app.generic_application import GenericApplication

from fixtures import print_tmp_path, valid_custom_logging_config, project_dir

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


class BaseTestApplication(GenericApplication):
    def __init__(self, **kwargs):
        super().__init__(
            application_name="test_application",
            version="0.0.1",
            logging_init_default_logging_enabled=False,  # Caution: This is necessary because otherwise log init will
            logging_init_custom_logging_enabled=False,   # remove pytest handler and caplog won't work.
            application_config_init_enabled=False,
            **kwargs
        )


class ExplicitlySuccessfulApplication(BaseTestApplication):
    def run(self, argparser: argparse.ArgumentParser):
        return 0


class ImplicitlySuccessfulApplication(BaseTestApplication):
    def run(self, argparser: argparse.ArgumentParser):
        pass


class ErrorAtAddArgumentMethodApplication(BaseTestApplication):
    def add_arguments(self, argparser: argparse.ArgumentParser):
        raise RuntimeError("foo")

    def run(self, argparser: argparse.ArgumentParser):
        pass


class ErrorAtRunMethodApplication(BaseTestApplication):
    def run(self, argparser: argparse.ArgumentParser):
        raise RuntimeError("foo")


class TestErrorHandling:
    def test_GenericApplicationStarted_ExitExplicitlySuccessfull_SuccessfullReturnCode(self, caplog, project_dir):
        test_app = ExplicitlySuccessfulApplication()
        assert test_app.start([]) == 0

    def test_GenericApplicationStarted_ExitImplicitlySuccessfull_SuccessfullReturnCode(self, caplog, project_dir):
        test_app = ImplicitlySuccessfulApplication()
        assert test_app.start([]) == 0

    def test_GenericApplicationStarted_ErrorAtAddArgumentUsercodeThrown_ErrorLoggedAndExitedCleanly(self, caplog, project_dir):
        test_app = ErrorAtAddArgumentMethodApplication()
        assert test_app.start([]) == -1
        assert "RuntimeError: foo" in caplog.text

    def test_GenericApplicationStarted_ErrorAtRunUsercodeThrown_ErrorLoggedAndExitedCleanly(self, caplog, project_dir):
        test_app = ErrorAtRunMethodApplication()
        assert test_app.start([]) == -1
        assert "RuntimeError: foo" in caplog.text
