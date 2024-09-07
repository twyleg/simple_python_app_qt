# Copyright (C) 2024 twyleg
# fmt: off
import argparse
from pathlib import Path

from simple_python_app.generic_application import GenericApplication

from fixtures import (
    valid_custom_logging_config,
    project_dir,
    print_tmp_path,
    valid_application_config_in_cwd,
    invalid_application_config_in_cwd,
)


#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


FILE_DIR = Path(__file__).parent


class BaseTestApplication(GenericApplication):
    def __init__(self, **kwargs):
        super().__init__(
            application_name="test_application",
            version="0.0.1", **kwargs
        )

    def run(self, argparser: argparse.ArgumentParser):
        pass


class ConfigInitDisabledApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            application_config_init_enabled=False
        )


class ExplicitConfigApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            application_config_init_enabled=True,
            application_config_schema_filepath=FILE_DIR / "resources/application_configs/valid_test_application_config_schema.json",
            application_config_filepath=Path.cwd() / "test_application_config.json",
        )


class ExplicitConfigWithInvalidSchemaApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            application_config_init_enabled=True,
            application_config_schema_filepath=FILE_DIR / "resources/application_configs/invalid_test_application_config_schema.json",
            application_config_filepath=Path.cwd() / "test_application_config.json",
        )


class UnavailableConfigSchemaApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            application_config_init_enabled=True,
            application_config_schema_filepath=FILE_DIR / "resources/application_configs/not_existing.json",
            application_config_filepath=Path.cwd() / "test_application_config.json",
        )


class SearchConfigApplication(BaseTestApplication):
    def __init__(self):
        super().__init__(
            application_config_init_enabled=True,
            application_config_schema_filepath=FILE_DIR / "resources/application_configs/valid_test_application_config_schema.json",
        )


class TestValidConfigProvided:
    def assert_valid_config(self, config):
        assert config is not None
        assert config["example_parameter_integer"] == 42
        assert config["example_parameter_string"] == "foo"
        assert config["example_parameter_float"] == 3.14

    def test_ExplicitConfigSpecified_StartApplication_ExplicitConfigLoaded(
            self,
            caplog,
            project_dir,
            valid_application_config_in_cwd
    ):
        test_app = ExplicitConfigApplication()
        test_app.start([])

        self.assert_valid_config(test_app.application_config)

    def test_SearchConfig_StartApplication_ConfigFoundAndLoaded(
            self,
            caplog,
            project_dir,
            valid_application_config_in_cwd
    ):
        test_app = SearchConfigApplication()
        test_app.start([])

        assert test_app.application_config_filepath == valid_application_config_in_cwd
        self.assert_valid_config(test_app.application_config)


class TestInvalidConfigProvided:
    def test_ExplicitConfigSpecified_StartApplication_ConfigInvalidError(
            self,
            caplog,
            project_dir,
            invalid_application_config_in_cwd
    ):
        test_app = ExplicitConfigApplication()
        assert test_app.start([]) == -1


class TestNoConfigProvided:
    def test_ConfigInitDisabled_StartApplication_NoConfigLoadedAsExpected(
            self,
            caplog,
            project_dir
    ):
        test_app = ConfigInitDisabledApplication()
        test_app.start([])

        assert test_app.application_config is None

    def test_ExplicitConfigSpecified_StartApplication_ConfigFileNotFoundError(
            self,
            caplog,
            project_dir
    ):
        test_app = ExplicitConfigApplication()
        assert test_app.start([]) == -1


class TestNoConfigSchemaProvided:
    def test_ExplicitConfigSpecified_StartApplication_ConfigSchemaFileNotFoundError(
            self,
            caplog,
            project_dir,
            valid_application_config_in_cwd
    ):
        test_app = UnavailableConfigSchemaApplication()
        assert test_app.start([]) == -1


class TestInvalidConfigSchemaProvided:
    def test_ExplicitConfigSpecified_StartApplication_ConfigSchemaFileInvalidError(
            self,
            caplog,
            project_dir,
            valid_application_config_in_cwd
    ):
        test_app = ExplicitConfigWithInvalidSchemaApplication()
        assert test_app.start([]) == -1
