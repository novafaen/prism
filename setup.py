#!/usr/bin/env python

from setuptools import setup

setup(
    name='prism',
    version='0.0.1',
    description='Let there be light!',
    author='Kristoffer Nilsson',
    author_email='smrt@novafaen.se',
    url='http://smrt.novafaen.se/',
    packages=['prism'],
    requires=[
        'smrt',
        'requests',
        'lifxlan',
        'yeelight'
    ],
    dependency_links=[
        'git+https://github.com/novafaen/smrt.git#f0fc9a6a9487fe7e924cd5b72be8a4e45c60cdf9',
        'https://github.com/novafaen/lifxlan#e64921102ded5e7e914e150172a4ac1ea752e598'
    ],
    test_suite='tests',
    tests_require=[

    ])
