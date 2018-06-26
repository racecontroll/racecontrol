# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import logging
import codecs
from os import path, getcwd


# Get logger for setup
logger = logging.getLogger(__name__)


def parse_requirements(filename):
    """
    Helper which parses requirement_?.*.txt files
    :param filename: relative path, e.g. `./requirements.txt`
    :returns: List of requirements
    """

    # Get absolute filepath
    filepath = path.join(getcwd(), filename)

    # Check if file exists
    if not path.exists(path.join(getcwd(), filename)):
        logger.warning("[!] File {} not found".format(filename))
        return []

    # Parse install requirements
    with codecs.open(filepath, encoding="utf-8") as f:
        return [requires.strip() for requires in f.readlines()]


def parse_long_description():
    """
    Helper function which parses the readme
    :returns: Content of the Readme
    """
    with codecs.open(path.join(getcwd(), "README.rst"), encoding="utf-8") as f:
        return f.read()


setup(
    name="racecontrol",
    version="0.0.1a",
    description="Racecontrol",
    long_description=parse_long_description(),
    url="https://github.com/racecontroll/racecontrol",
    author="Matthias Riegler",
    author_email="matthias@xvzf.tech",

    classifiers=[
        "Programming Language :: Python :: 3",
    ],

    packages=["racecontrol"],
    include_package_data=True,  # Needed for the webui
    install_requires=parse_requirements("requirements.txt"),

    # project_urls={
    #     "Bug Reports": "@TODO",
    #     "Source": "@TODO",
    # },

)
