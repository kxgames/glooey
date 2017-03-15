#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
    ],
    include_package_data=True,
    install_requires=[
        'pyglet',
        'more_itertools',
        'vecrec', 
        'autoprop',
        'debugtools',
        'yaml',
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
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries',
    ],
)
