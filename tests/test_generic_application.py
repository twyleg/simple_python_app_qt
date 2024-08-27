# Copyright (C) 2024 twyleg
import argparse

import pytest

import logging
from pathlib import Path

from simple_python_app.generic_application import GenericApplication


#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


class SimpleGenericTestApplication(GenericApplication):

    def __init__(self):
        super().__init__(
            application_name=type(self).__name__,
            version="0.0.1",
            init_config=False
        )

    def run(self, argparser: argparse.ArgumentParser):
        self.logm.info("run()")



class TestExample:
    def test_ValidreferenceLightMatrix_Read_Success(self, caplog, tmp_path):
        logging.info("Tmp path: %s", tmp_path)

        simple_test_application = SimpleGenericTestApplication()
        simple_test_application.start([])

        assert 1 == 1
