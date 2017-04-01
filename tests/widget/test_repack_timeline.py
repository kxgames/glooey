#!/usr/bin/env python3

import pytest
import glooey

TIMELINE = []

class RepackObserver:

    def repack(self):
        TIMELINE.append(self.repack)
        return super().repack()

    def claim(self):
        TIMELINE.append(self.claim)
        return super().claim()

    def realign(self):
        TIMELINE.append(self.realign)
        return super().realign()

    def regroup(self, new_group):
        TIMELINE.append(self.regroup)
        return super().regroup(new_group)

    def draw(self):
        TIMELINE.append(self.draw)
        return super().draw()


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


@pytest.fixture
def dummy_widgets():
    window = DummyWindow()
    return DummyGui(window), DummyBin(), DummyPlaceholder()


def test_add_widget_to_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets

    del TIMELINE[:]
    bin.add(widget)
    print(TIMELINE)
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
            gui.repack,
            gui.claim,
              bin.claim,
                widget.claim,
            gui.realign,
              bin.realign,
                widget.realign,
                widget.draw,
              bin.draw,
            gui.draw,
              bin.regroup,
                widget.regroup,
                widget.draw,
              bin.draw,
    ]

def test_repack_gui(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    gui.repack()
    assert TIMELINE == [
            gui.repack,
            gui.claim,
              bin.claim,
                widget.claim,
            gui.realign,
              bin.realign,
                widget.realign,
                widget.draw,
              bin.draw,
            gui.draw,
    ]

def test_repack_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    bin.repack()
    assert TIMELINE == [
            bin.repack,
            bin.claim,
              widget.claim,
            bin.realign,
              widget.realign,
              widget.draw,
            bin.draw,
    ]
    
def test_repack_widget(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    widget.repack()
    from pprint import pprint
    pprint(TIMELINE)
    assert TIMELINE == [
            widget.repack,
            widget.claim,
            widget.realign,
            widget.draw,
    ]
def test_regroup_gui(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    gui.regroup(None)
    assert TIMELINE == [
            gui.regroup,
              bin.regroup,
                widget.regroup,
                widget.draw,
              bin.draw,
            gui.draw,
    ]

def test_regroup_bin(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    bin.regroup(None)
    assert TIMELINE == [
            bin.regroup,
              widget.regroup,
              widget.draw,
            bin.draw,
    ]

def test_regroup_widget(dummy_widgets):
    gui, bin, widget = dummy_widgets
    bin.add(widget); gui.add(bin)

    del TIMELINE[:]
    widget.regroup(None)
    assert TIMELINE == [
            widget.regroup,
            widget.draw,
    ]

