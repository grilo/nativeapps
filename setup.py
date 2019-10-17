#!/usr/bin/env python

"""
    ing.nativeapps web application.

    Stores mobile applications and generates a list to be downloaded,
    mainly for testing purposes.
"""

from setuptools import setup, find_packages

# ING local packages should always start with 'ing.'
setup(
    name='ing.nativeapps',
    version='0.1',
    description='Mobile applications index for testing.',
    url='https://gitlab.ing.net/ContinuousDeliverySpain/nativeapps',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    package_data={
        'nativeapps': ['static/*', 'templates/*', 'service/*'],
    },
    install_requires=[
        'flask',
        'biplist',
        'AxmlParserPY',
    ],
    entry_points={
        'console_scripts': [
            'nativeapps=nativeapps.cli:cli',
        ],

    },
    tests_require=[
        'pytest-runner',
        'pylint',
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pytest-xdist'
    ],
)
