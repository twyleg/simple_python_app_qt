# Copyright (C) 2024 twyleg
import argparse
import importlib
import shutil
from os import listdir

import pytest


import logging
from pathlib import Path

import simple_python_app.logging
import simple_python_app.config
from simple_python_app.generic_application import GenericApplication
from simple_python_app.config import ConfigFileNotFoundError, ConfigInvalidError, ConfigSchemaFileNotFoundError, ConfigSchemaInvalidError


#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


@pytest.fixture(autouse=True)
def print_tmp_path(tmp_path):
    logging.info("tmp_path: %s", tmp_path)
    return None

@pytest.fixture
def project_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path

@pytest.fixture
def valid_logging_config(tmp_path):
    log_config_template_filepath = FILE_DIR / "resources/logging_configs/valid_logging_config.yaml"
    log_config_filepath = tmp_path / "logging.yaml"
    shutil.copy(log_config_template_filepath, log_config_filepath)
    return log_config_filepath

@pytest.fixture
def valid_application_config_in_cwd(tmp_path):
    application_config_template_filepath = FILE_DIR / "resources/application_configs/valid_test_application_config.json"
    application_config_filepath = tmp_path / "test_application_config.json"
    shutil.copy(application_config_template_filepath, application_config_filepath)
    return application_config_filepath

@pytest.fixture
def invalid_application_config_in_cwd(tmp_path):
    application_config_template_filepath = FILE_DIR / "resources/application_configs/invalid_test_application_config.json"
    application_config_filepath = tmp_path / "test_application_config.json"
    shutil.copy(application_config_template_filepath, application_config_filepath)
    return application_config_filepath


def reload_imports():
    importlib.reload(simple_python_app.logging)
    importlib.reload(simple_python_app.config)


class BaseTestApplication(GenericApplication):
    def __init__(self, **kwargs):
        super().__init__(
            application_name="test_application",
            version="0.0.1",
            **kwargs
        )

    def run(self, argparser: argparse.ArgumentParser):
        pass


class ConfigInitDisabledApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            config_init_enabled=False
        )

class ExplicitConfigApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            config_init_enabled=True,
            config_schema_filepath=FILE_DIR / "resources/application_configs/valid_test_application_config_schema.json",
            config_filepath=Path.cwd() / "test_application_config.json",
        )

class ExplicitConfigWithInvalidSchemaApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            config_init_enabled=True,
            config_schema_filepath=FILE_DIR / "resources/application_configs/invalid_test_application_config_schema.json",
            config_filepath=Path.cwd() / "test_application_config.json",
        )

class UnavailableConfigSchemaApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            config_init_enabled=True,
            config_schema_filepath=FILE_DIR / "resources/application_configs/not_existing.json",
            config_filepath=Path.cwd() / "test_application_config.json",
        )

class SearchConfigApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            config_init_enabled=True,
            config_schema_filepath=FILE_DIR / "resources/application_configs/valid_test_application_config_schema.json"
        )

class TestValidConfigProvided:

    def assert_valid_config(self, config):
        assert config is not None
        assert config["example_parameter_integer"] == 42
        assert config["example_parameter_string"] == "foo"
        assert config["example_parameter_float"] == 3.14

    def test_ExplicitConfigSpecified_StartApplication_ExplicitConfigLoaded(self, caplog, project_dir,
                                                                          valid_application_config_in_cwd):
        test_app = ExplicitConfigApplication()
        test_app.start([])

        self.assert_valid_config(test_app.config)

    def test_SearchConfig_StartApplication_ConfigFoundAndLoaded(self, caplog, project_dir,
                                                                valid_application_config_in_cwd):
        test_app = SearchConfigApplication()
        test_app.start([])

        assert test_app._config_filepath == valid_application_config_in_cwd
        self.assert_valid_config(test_app.config)


class TestInvalidConfigProvided:

    def test_ExplicitConfigSpecified_StartApplication_ConfigInvalidError(self, caplog, project_dir,
                                                                          invalid_application_config_in_cwd):
        test_app = ExplicitConfigApplication()
        with pytest.raises(ConfigInvalidError):
            test_app.start([])


class TestNoConfigProvided:

    def test_ConfigInitDisabled_StartApplication_NoConfigLoadedAsExpected(self, caplog, project_dir):
        test_app = ConfigInitDisabledApplication()
        test_app.start([])

        assert test_app.config is None

    def test_ExplicitConfigSpecified_StartApplication_ConfigFileNotFoundError(self, caplog, project_dir):
        test_app = ExplicitConfigApplication()
        with pytest.raises(ConfigFileNotFoundError):
            test_app.start([])


class TestNoConfigSchemaProvided:

    def test_ExplicitConfigSpecified_StartApplication_ConfigSchemaFileNotFoundError(self, caplog, project_dir,
                                                                                    valid_application_config_in_cwd):
        test_app = UnavailableConfigSchemaApplication()
        with pytest.raises(ConfigSchemaFileNotFoundError):
            test_app.start([])


class TestInvalidConfigSchemaProvided:

    def test_ExplicitConfigSpecified_StartApplication_ConfigSchemaFileInvalidError(self, caplog, project_dir,
                                                                                    valid_application_config_in_cwd):
        test_app = ExplicitConfigWithInvalidSchemaApplication()
        with pytest.raises(ConfigSchemaInvalidError):
            test_app.start([])