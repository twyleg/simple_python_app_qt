# Copyright (C) 2024 twyleg
# fmt: off
import argparse
import sys
from pathlib import Path

from simple_python_app.generic_application import GenericApplication

from fixtures import (
    valid_custom_logging_config,
    project_dir
)
from simple_python_app_qt.qml_application import QmlApplication

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


class BaseQmlTestApplication(QmlApplication):
    def __init__(self, **kwargs):
        sys.argv.extend(["-platform", "offscreen"])
        super().__init__(
            application_name="test_qml_application",
            version="0.0.1",
            application_config_init_enabled=False,
            **kwargs
        )

    def run(self, argparser: argparse.Namespace):
        return self.open()


class ValidFrontendApplication(BaseQmlTestApplication):
    def __init__(self):
        super().__init__(
            frontend_qml_file_path=FILE_DIR / "resources/frontends/valid_frontend.qml"
        )


class InvalidFrontendApplication(BaseQmlTestApplication):
    def __init__(self):
        super().__init__(
            frontend_qml_file_path=FILE_DIR / "resources/frontends/invalid_frontend_with_syntax_error.qml"
        )


class NonExistingFrontendApplication(BaseQmlTestApplication):
    def __init__(self):
        super().__init__(
            frontend_qml_file_path=FILE_DIR / "resources/frontends/this_file_does_not_exist.qml"
        )


class TestQmlApplication:

    def test_QmlApplicationWithValidFrontend_StartApplication_ApplicationStartedAndClosedCleanly(
            self,
            caplog,
            project_dir
    ):
        test_app = ValidFrontendApplication()
        assert test_app.start() == 0

    def test_QmlApplicationWithInvalidFrontend_StartApplication_ErrorThrownAndExit(
            self,
            caplog,
            project_dir
    ):
        test_app = InvalidFrontendApplication()
        assert test_app.start() == -1

    def test_QmlApplicationWithNonExistingFrontend_StartApplication_ErrorThrownAndExit(
            self,
            caplog,
            project_dir
    ):
        test_app = NonExistingFrontendApplication()
        assert test_app.start() == -1
