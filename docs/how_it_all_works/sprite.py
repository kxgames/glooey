#!/usr/bin/env python3

import pyglet
import glooey

class SpriteDemo(glooey.Widget):
    custom_alignment = 'center'

    def __init__(self):
        super().__init__()
        self.sprite = None

    def do_claim(self):
        return 200, 200

    # Glooey calls this method when the widget is assigned a new group.
    # See the section on `How regrouping works` for more details.
    def do_regroup(self):
        if self.sprite is not None:
            self.sprite.batch = self.batch
            self.sprite.group = self.group

    def do_draw(self):
        if self.sprite is None:
            self.sprite = pyglet.sprite.Sprite(
                    img=pyglet.image.load('wesnoth_logo.png'),
                    x=self.rect.left,
                    y=self.rect.bottom,
                    batch=self.batch,
                    group=self.group,
            )
        else:
            self.sprite.set_position(
                    x=self.rect.left,
                    y=self.rect.bottom,
            )

    def do_undraw(self):
        if self.sprite is not None:
            self.sprite.delete()
            self.sprite = None

window = pyglet.window.Window()
gui = glooey.Gui(window)
demo = SpriteDemo()

gui.add(demo)
gui.push_handlers(on_click=lambda w: 
        demo.unhide() if demo.is_hidden else demo.hide())

pyglet.app.run()
