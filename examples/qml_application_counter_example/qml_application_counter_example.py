# Copyright (C) 2024 twyleg
import argparse
from pathlib import Path

from PySide6.QtCore import QObject, QTimer

from simple_python_app_qt.property import PropertyMeta, Property
from simple_python_app_qt.qml_application import QmlApplication


FILE_DIR = Path(__file__).parent


class ExampleModel(QObject, metaclass=PropertyMeta):
    headline = Property(str)
    counter = Property(int)

    def __init__(self, headline: str, parent: QObject | None = None):
        QObject.__init__(self, parent)
        self.headline = headline  # type: ignore
        self.counter = 0  # type: ignore


class QmlApplicationCounterExample(QmlApplication):
    def __init__(self):
        super().__init__(
            application_name="simple_counter_app_qml_example",
            version="0.0.1",
            application_config_schema_filepath=FILE_DIR / "resources/config/simple_counter_app_qml_example_config_schema.json",
            application_config_filepath=FILE_DIR / "resources/config/simple_counter_app_qml_example_config.json",
            logging_logfile_output_dir=FILE_DIR / "log/",
            frontend_qml_file_path=FILE_DIR / "resources/frontend/frontend.qml",
        )

        self.example_model = ExampleModel(self.application_name)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_callback)

        self.add_model(self.example_model, "example_model")

    def timer_callback(self) -> None:
        self.example_model.counter += 1
        self.logm.info("Counter: %s", self.example_model.counter)

    def add_arguments(self, argparser: argparse.ArgumentParser):
        argparser.add_argument("--name", type=str, default=None, help="Application name")
        argparser.add_argument("--delay", type=int, default=1000, help="Delay (millis) for counter")

    def run(self, args: argparse.Namespace) -> int:
        if args.name:
            self.example_model.headline = args.name
        self.timer.start(args.delay)
        return self.open()


if __name__ == "__main__":
    qml_application_counter_example = QmlApplicationCounterExample()
    qml_application_counter_example.start()
