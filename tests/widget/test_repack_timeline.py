#!/usr/bin/env python3

import pytest
import glooey
import pyglet

TIMELINE = []

class RepackObserver:

    def _repack(self):
        TIMELINE.append(self._repack)
        return super()._repack()

    def _claim(self):
        TIMELINE.append(self._claim)
        return super()._claim()

    def _realign(self):
        TIMELINE.append(self._realign)
        return super()._realign()

    def _regroup(self, new_group):
        TIMELINE.append(self._regroup)
        return super()._regroup(new_group)

    def _draw(self):
        TIMELINE.append(self._draw)
        return super()._draw()


class DummyWindow:
    width = 100
    height = 100

    def push_handlers(self, gui):
        pass


class DummyGui(RepackObserver, glooey.Gui):

    def add(self, widget):
        TIMELINE.append(self.add)
        return super().add(widget)


class DummyBin(RepackObserver, glooey.Bin):

    def add(self, widget):
        TIMELINE.append(self.add)
        return super().add(widget)


class DummyPlaceholder(RepackObserver, glooey.Placeholder):
    pass

class DummyGroup(pyglet.graphics.Group):
    pass

@pytest.fixture
def dummy_widgets():
    window = DummyWindow()
    return DummyGui(window), DummyBin(), DummyPlaceholder()


def test_add_widget_to_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets

    del TIMELINE[:]
    bin.add(widget)
    assert TIMELINE == [
            bin.add,
    ]

def test_add_bin_to_gui(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget)

    del TIMELINE[:]
    gui.add(bin)
    assert TIMELINE == [
            gui.add,
            gui._repack,
            gui._claim,
              bin._claim,
                widget._claim,
            gui._realign,
            gui._draw,
              bin._realign,
              bin._draw,
                widget._realign,
                widget._draw,
              bin._regroup,
              bin._draw,
                widget._regroup,
                widget._draw,
    ]

def test_repack_gui(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    gui._repack()
    assert TIMELINE == [
            gui._repack,
            gui._claim,
              bin._claim,
                widget._claim,
            gui._realign,
            gui._draw,
              bin._realign,
              bin._draw,
                widget._realign,
                widget._draw,
    ]

def test_repack_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    bin._repack()
    assert TIMELINE == [
            bin._repack,
            bin._claim,
              widget._claim,
            bin._realign,
            bin._draw,
              widget._realign,
              widget._draw,
    ]
    
def test_repack_widget(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    widget._repack()
    assert TIMELINE == [
            widget._repack,
            widget._claim,
            widget._realign,
            widget._draw,
    ]
def test_regroup_gui(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    gui._regroup(DummyGroup())
    assert TIMELINE == [
            gui._regroup,
            gui._draw,
              bin._regroup,
              bin._draw,
                widget._regroup,
                widget._draw,
    ]

def test_regroup_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    bin._regroup(DummyGroup())
    assert TIMELINE == [
            bin._regroup,
            bin._draw,
              widget._regroup,
              widget._draw,
    ]

def test_regroup_widget(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    widget._regroup(DummyGroup())
    assert TIMELINE == [
            widget._regroup,
            widget._draw,
    ]

