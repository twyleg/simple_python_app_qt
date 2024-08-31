import argparse
import sys
from pathlib import Path

from simple_python_app.generic_application import GenericApplication


FILE_DIR = Path(__name__).parent


class SimpleExampleApplication(GenericApplication):
    def __init__(self):
        super().__init__(
            application_name="simple_example_application",
            version="0.0.1",
            config_schema_filepath=FILE_DIR / "simple_example_application_config_schema.json"
        )

    def add_arguments(self, argparser: argparse.ArgumentParser):
        self.logm.info("init_argparse()")

        argparser.add_argument("--foo",
            type=str,
            default=None,
            help="Example")

    def run(self, args: argparse.Namespace):
        self.logm.info("run()")
        self.logm.debug("run()")
        self.logm.info("%s", args)


if __name__ == "__main__":
    simple_example_application = SimpleExampleApplication()
    simple_example_application.start(sys.argv[1:])