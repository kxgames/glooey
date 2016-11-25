#!/usr/bin/env python3

import pyglet

def install_padding_hotkeys(window, container):

    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.J:
            container.padding = max(0, container.padding - 2)
        if symbol == pyglet.window.key.K:
            container.padding += 2

    window.push_handlers(on_key_press)


def install_placement_hotkeys(window, container):

    placement_hotkeys = {
            pyglet.window.key.Q: 'top_left',
            pyglet.window.key.W: 'top_center',
            pyglet.window.key.E: 'top_right',
            pyglet.window.key.A: 'center_left',
            pyglet.window.key.S: 'center',
            pyglet.window.key.D: 'center_right',
            pyglet.window.key.Z: 'bottom_left',
            pyglet.window.key.X: 'bottom_center',
            pyglet.window.key.C: 'bottom_right',
            pyglet.window.key.F: 'fill',
    }

    def on_key_press(symbol, modifiers):
        if symbol in placement_hotkeys:
            container.placement = placement_hotkeys[symbol]

    window.push_handlers(on_key_press)
