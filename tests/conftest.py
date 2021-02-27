#!/usr/bin/env python3

import pytest
from run_demos import run_demo

def pytest_addoption(parser):
    parser.addoption('-D', '--run-demos', action='store_true')

def pytest_collect_file(path, parent):
    if parent.config.option.run_demos:
        if path.fnmatch('demo_*.py'):
            return DemoFile.from_parent(parent, fspath=path)

class DemoFile(pytest.File):

    def collect(self):
        name = self.fspath.basename[:-len('.py')]
        yield DemoItem.from_parent(self, name=name, fspath=self.fspath)

class DemoItem(pytest.Item):

    def __init__(self, name, parent, fspath):
        super().__init__(name, parent)
        self.path = fspath

    def runtest(self):
        run_demo(self.path.strpath)

