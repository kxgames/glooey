#!/usr/bin/env python3

import glooey

def test_scroll_box_scale_grip_no_child():
    # It should not be an error to attach a scroll box with a scaled grip and 
    # no child to the GUI.  This means the scroll box needs to hold off 
    # calculating how big its grip should be if it's attached before it has a 
    # child.  See #36.

    class TestWindow:

        def __init__(self):
            self.width = 600
            self.height = 480

        def push_handlers(self, listener):
            pass

    class TestScrollBox(glooey.ScrollBox):
     
        class VBar(glooey.VScrollBar):
            custom_scale_grip = True

            class Grip(glooey.Button):
                pass

    win = TestWindow()
    gui = glooey.Gui(win)

    scroll = TestScrollBox()
    gui.add(scroll)
