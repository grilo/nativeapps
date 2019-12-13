#!/usr/bin/env python

"""
    nativeapps web application.

    Stores mobile applications and generates a list to be downloaded,
    mainly for testing purposes.
"""

from setuptools import setup, find_packages

setup(
    name="nativeapps",
    version="0.1",
    description="Mobile applications index for testing.",
    url="https://github.com/grilo/nativeapps",
    classifiers=[
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "nativeapps": ["static/*"],
    },
    install_requires=[
        "flask",
        "biplist",
        "AxmlParserPY",
    ],
    entry_points={
        "console_scripts": [
            "nativeapps=nativeapps.cli:cli",
        ],

    },
    tests_require=[
        "pytest-runner",
        "pylint",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist"
    ],
)
