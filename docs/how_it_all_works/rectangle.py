#!/usr/bin/env python3

import pyglet
import glooey

class RectangleDemo(glooey.Widget):
    custom_alignment = 'center'
    custom_size_hint = 300, 200

    def __init__(self):
        super().__init__()
        self.artist = glooey.drawing.Rectangle(
                color=(1, 71, 108),
                hidden=True, # Don't draw the rectangle yet.
        )

    def do_claim(self):
        return 0, 0

    # Glooey calls this method when the widget is assigned a new group.
    # See the section on `How regrouping works` for more details.
    def do_regroup(self):
        self.artist.batch = self.batch
        self.artist.group = self.group

    # Glooey calls this method when the widget is assigned a new size.
    # See the section on `How repacking works` for more details.
    def do_resize(self):
        self.artist.rect = self.rect

    def do_draw(self):
        self.artist.show()

    def do_undraw(self):
        self.artist.hide()

window = pyglet.window.Window()
gui = glooey.Gui(window)
demo = RectangleDemo()

gui.add(demo)
gui.push_handlers(on_click=lambda w: 
        demo.unhide() if demo.is_hidden else demo.hide())

pyglet.app.run()

