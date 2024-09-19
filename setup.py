# Copyright (C) 2024 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(relative_filepath):
    return open(Path(__file__).parent / relative_filepath).read()


def read_long_description() -> str:
    return read("README.md")


# fmt: off
setup(
    name="simple_python_app_qt",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="Small framework based on simple_python_app that simplifies Python Qt app creation.",
    license="GPL 3.0",
    keywords="framework boilerplate logging argparse config qt qml pyside",
    url="https://github.com/twyleg/simple_python_app_qt",
    packages=find_packages(),
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "simple_python_app==0.1.1",
        "pyside6~=6.7.2"
    ],
    entry_points={},
)
# fmt: on
