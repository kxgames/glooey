#!/usr/bin/env python3

"""\
The window should just be black, but the cursor should be a gold triangle.
"""

import pyglet
import glooey.themes.golden as golden

print(__doc__)

window = pyglet.window.Window()
root = golden.Gui(window)

pyglet.app.run()


