#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup

import sys
if sys.version_info < (3, 6):
    raise RuntimeError("glooey requires python3.6 or better.")

import re
with open('glooey/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

setup(
    name='glooey',
    version=version,
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    description='An object-oriented GUI library for pyglet.',
    long_description=readme,
    url='https://github.com/kxgames/glooey',
    packages=[
        'glooey',
        'glooey.drawing',
        'glooey.themes',
    ],
    include_package_data=True,
    install_requires=[
        'pyglet',
        'more_itertools',
        'vecrec', 
        'autoprop',
        'debugtools',
        'pyyaml',
    ],
    license='MIT',
    zip_safe=False,
    keywords=[
        'glooey',
        'pyglet',
        'gui',
        'library',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries',
    ],
)
