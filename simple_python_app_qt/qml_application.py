# Copyright (C) 2024 twyleg
import logging
import argparse
import sys
from copy import copy
from pathlib import Path
from typing import List, Tuple

from PySide6 import QtCore
from PySide6.QtCore import QObject, QtMsgType, Slot, Signal, Property, QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from simple_python_app.generic_application import GenericApplication


logm = logging.getLogger(__name__)
qml_logm = logging.getLogger("qml")

FILE_DIR = Path(__file__).parent


class LogModel(QObject):

    logLineAdded = Signal(int, str, str, arguments=["levelno", "header", "msg"])

    def __init__(self) -> None:
        QObject.__init__(self)
        self.redirect_to_prebuffer = True
        self.prebuffer_entries: List[Tuple[int, str, str]] = []

    @Slot()
    def requestPrebuffer(self):
        for prebuffer_entry in self.prebuffer_entries:
            self.logLineAdded.emit(*prebuffer_entry)
        self.redirect_to_prebuffer = False

    def add_log_line(self, level: int, header: str, msg: str) -> None:
        if self.redirect_to_prebuffer:
            self.prebuffer_entries.append((level, header, msg))
        else:
            self.logLineAdded.emit(level, header, msg)

    @Slot(str)
    def setLogLevel(self, log_level):
        if logging.getLogger().level == logging.ERROR:
            logging.getLogger().setLevel(logging.WARNING)
        logging.warning("Changing log level to '%s'", log_level)
        logging.getLogger().setLevel(log_level)

    def log_level(self):
        return logging.getLevelName(logging.getLogger().level)

    @Signal  # type: ignore
    def log_level_changed(self):
        pass

    logLevel = Property(str, log_level, notify=log_level_changed)  # type: ignore


class UiLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.log_model = LogModel()

    def emit(self, record):
        try:
            msg = record.getMessage()
            header_record = copy(record)
            header_record.msg = ""
            header_record.args = None
            header = self.format(header_record)
            self.log_model.add_log_line(record.levelno, header, msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class QmlApplication(GenericApplication):
    # fmt: off
    def __init__(self,
                 application_name: str,
                 version: str,
                 frontend_qml_file_path: Path,
                 **kwargs
                 ):
        super().__init__(
            application_name=application_name,
            version=version,
            logging_default_config_filepath=FILE_DIR / "resources/default_logging_config.yaml",
            **kwargs
        )
    # fmt: on

        self.frontend_qml_file_path = frontend_qml_file_path

        self.app: QCoreApplication | QGuiApplication | None
        if not QGuiApplication.instance():
            self.app = QGuiApplication(sys.argv)
        else:
            self.app = QGuiApplication.instance()

        self.engine = QQmlApplicationEngine()

        QtCore.qInstallMessageHandler(self.qt_message_handler)

        super().add_custom_init_stage_two(self._init_stage_qml_logging)
        super().add_custom_init_stage_three(self._init_stage_qml_info)

    @staticmethod
    def find_dev_log_handler():
        for handler in logging.getLogger().handlers:
            if handler.get_name() == "ui":
                assert isinstance(handler, UiLogHandler)
                return handler.log_model

    @staticmethod
    def qt_message_handler(mode, context, message):
        match mode:
            case QtMsgType.QtDebugMsg:
                qml_logm.debug("%s:%d: %s", context.file, context.line, message)
            case QtMsgType.QtInfoMsg:
                qml_logm.info("%s", message)
            case QtMsgType.QtWarningMsg:
                qml_logm.warning("%s:%d: %s", context.file, context.line, message)
            case _:
                qml_logm.error("%s:%d: %s", context.file, context.line, message)

    def add_model(self, model: QObject, name: str) -> None:
        self.engine.rootContext().setContextProperty(name, model)

    def _init_stage_qml_logging(self) -> None:
        self.log_model = self.find_dev_log_handler()
        self.add_model(self.log_model, "log_model")

    def _init_stage_qml_info(self) -> None:
        logm.debug("qml details:")
        logm.debug("- qml frontend filepath = %s", self.frontend_qml_file_path.absolute())

    def open(self) -> int:
        if self.app is None:
            return -1

        self.engine.load(self.frontend_qml_file_path)
        if not self.engine.rootObjects():
            return -1

        ret = self.app.exec()

        # Engine needs to be destroyed manually at this point to avoid errors in QmlEngine
        # when for some reason self.app gets destroyed before self.engine
        del self.engine

        return ret

    def run(self, args: argparse.Namespace) -> int:
        return self.open()
