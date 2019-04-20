#!/usr/bin/env python3

import glooey
import pyglet

win = pyglet.window.Window()
gui = glooey.Gui(win)

sheet = pyglet.image.load('25.png')
sprites = pyglet.image.ImageGrid(sheet, 1, 4)

class MyCheckbox(glooey.Checkbox):
    custom_unchecked_base = sprites[0]
    custom_unchecked_off = sprites[1]
    custom_checked_base = sprites[2]
    custom_checked_off = sprites[3]

check = MyCheckbox()
check.alignment = 'center'
check.disable()
gui.add(check)

print("The checkbox should immediately appear disabled (grey, not blue).")

pyglet.app.run()
