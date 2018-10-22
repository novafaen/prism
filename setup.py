#!/usr/bin/env python

from setuptools import setup

setup(
    name='prism',
    version='0.0.1',
    description='Let there be light!',
    author='Kristoffer Nilsson',
    author_email='smrt@novafaen.se',
    url='http://smrt.novafaen.se/',
    packages=[],
    requires=[
        'smrt',
        'jsonschema',
        'requests',
        'lifxlan',
        'yeelight'
    ],
    dependency_links=[
        'git+https://github.com/novafaen/smrt.git'
    ],
    test_suite='tests',
    tests_require=[

    ])
