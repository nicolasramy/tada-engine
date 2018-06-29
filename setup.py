#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
from setuptools import setup, find_packages

with io.open("tada_engine/__init__.py", "rt", encoding="utf8") as file_resource:
    version = re.search(r"__version__ = \'(.*?)\'", file_resource.read()).group(1)


setup(
    name="tada-engine",
    version=version,
    description="Tada! Engine...",
    author="Nicolas RAMY",
    author_email="nicolas.ramy@darkelda.com",
    url="https://github.com/nicolasramy/tada-engine",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "tada-engine-master=tada_engine.__main__:master_command",
            "tada-engine-minion=tada_engine.__main__:minion_command"
        ],
    },
    install_requires=[
        "pyzmq",
        "setproctitle>=1.1.0",
        "termcolor",
        "uvloop"
    ],
    tests_require=[
        "coverage>=4.5.1",
    ],
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
)
