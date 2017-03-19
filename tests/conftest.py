#!/usr/bin/env python3

import pytest
from run_demos import run_demo

def pytest_addoption(parser):
    parser.addoption('-D', '--run-demos', action='store_true')

def pytest_collect_file(path, parent):
    if parent.config.option.run_demos:
        if path.fnmatch('demo_*.py'):
            return DemoFile(path, parent)

class DemoFile(pytest.File):

    def collect(self):
        name = self.fspath.basename[:-len('.py')]
        yield DemoItem(name, self, self.fspath)

class DemoItem(pytest.Item):

    def __init__(self, name, parent, path):
        super().__init__(name, parent)
        self.path = path

    def runtest(self):
        run_demo(self.path.strpath)

