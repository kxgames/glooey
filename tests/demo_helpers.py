#!/usr/bin/env python3

import pyglet
import glooey

class interactive_tests:

    def __init__(self, window, batch):
        self.window = window
        self.batch = batch
        self.label = pyglet.text.Label('',
                color=(255, 255, 255, 255),
                x=window.width - 5, y=5,
                anchor_x='right', anchor_y='bottom',
                batch=batch, group=pyglet.graphics.OrderedGroup(100),
        )
        self.test_generator = lambda: iter(())
        self.test_iterator = iter(())
        self.window.push_handlers(self)

    def __call__(self, test_generator):
        self.test_generator = test_generator
        self.test_iterator = test_generator()
        self.run_next_test()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.run_next_test()

    def run_next_test(self):
        try:
            label = next(self.test_iterator)
        except StopIteration:
            self.test_iterator = self.test_generator()
            label = next(self.test_iterator)

        self.label.text = label or ''


