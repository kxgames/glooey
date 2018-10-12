#!/usr/bin/env python3

import pyglet
import functools
import contextlib
import yaml

from pathlib import Path
from glooey.helpers import *

class ResourceLoader(pyglet.resource.Loader):

    def __init__(self, paths=None):
        super().__init__(paths, Path(__file__).parent / 'assets')

    def yaml(self, name):
        return yaml.load(self.file(name))

