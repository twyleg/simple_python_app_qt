# Copyright (C) 2024 twyleg
import pytest
import shutil
import logging
from pathlib import Path


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