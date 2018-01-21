#!/usr/bin/env python3

import pyglet
import glooey

class BlueRectangle(glooey.Widget):
    custom_alignment = 'center'
    custom_size_hint = 300, 200

    def __init__(self):
        super().__init__()
        self.vertex_list = None

    def do_claim(self):
        return 0, 0

    def do_draw(self):
        vertices = (
                self.rect.bottom_left.tuple + 
                self.rect.bottom_right.tuple + 
                self.rect.top_right.tuple + 
                self.rect.top_left.tuple
        )
        blue = 1, 71, 108

        # Only make a new vertex_list the first time `do_draw()` is called.  
        # After that, just update its position (in case the widget moved).
        if self.vertex_list is None:
            self.vertex_list = self.batch.add(
                    4, pyglet.gl.GL_QUADS, self.group,
                    ('v2f', vertices), ('c3B', 4 * blue)
            )
        else:
            self.vertex_list.vertices = vertices

    def do_undraw(self):
        if self.vertex_list is not None:
            self.vertex_list.delete()
            self.vertex_list = None

window = pyglet.window.Window()
gui = glooey.Gui(window)
demo = BlueRectangle()

gui.add(demo)
gui.push_handlers(on_click=lambda w: 
        demo.unhide() if demo.is_hidden else demo.hide())

pyglet.app.run()

