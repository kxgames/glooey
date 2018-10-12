#!/usr/bin/env python3

"""\
Run individual demos.  

Usage:
    ./run_demo.py [-v] <demo_paths>...

Options:
    -v --verbose
        Print the path to each test that runs.  This can be useful if you have 
        a test that's crashing right away but you can't tell which one it is.

You could also directly run the demos (they're all standalone python scripts), 
but you'd have to be in the same directory as the demo (otherwise some imports 
and assets won't be found).  This script manages the current directory so you 
can run demos from anywhere, which is sometimes convenient.
"""

import pyglet
import glooey

class on_space:

    def __init__(self, *args):
        if len(args) == 1:
            self.window = args[0].window
            self.batch = args[0].batch
        elif len(args) == 2:
            self.window = args[0]
            self.batch = args[1]
        else:
            raise TypeError(f"on_space() takes either 1 (gui) or 2 (window, batch) positional arguments, but {len(args)} were given")

        self.window.set_caption(__file__)
        self.label = pyglet.text.Label('',
                color=(255, 255, 255, 255),
                x=self.window.width - 5, y=5,
                anchor_x='right', anchor_y='bottom',
                batch=self.batch, group=pyglet.graphics.OrderedGroup(100),
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


def run_demos(path):
    import os, glob, fnmatch
    paths_to_ignore = 'assets', '__pycache__'

    if os.path.isdir(path):
        for subpath in os.listdir(path):
            if subpath not in paths_to_ignore:
                run_demo(os.path.join(path, subpath))

    elif fnmatch.fnmatch(os.path.basename(path), 'demo_*.py'):
        run_demo(path)

def run_demo(path):
    import os, runpy

    original_dir = os.getcwd()
    demo_dir = os.path.dirname(path)
    demo_script = os.path.basename(path)

    try:
        if demo_dir: os.chdir(demo_dir)
        runpy.run_path(demo_script)
    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    for path in args['<demo_paths>']:
        if args['--verbose']:
            print(path)
        run_demo(path)


