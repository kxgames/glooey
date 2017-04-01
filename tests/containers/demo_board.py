#!/usr/bin/env python3

import pyglet
import glooey
import run_demos
from vecrec import Vector, Rect

window = pyglet.window.Window()
gui = glooey.Gui(window)
frame = glooey.Frame()
frame.decoration.outline = 'green'
board = glooey.Board()
widget = glooey.EventLogger(50, 50, 'orange')

frame.add(board)
gui.add(frame)

def test_scalar_position_arguments():
    board.move(widget, left=0, bottom=0)
    yield "Put the widget in the bottom left corner."

    board.move(widget, right=400, top=300)
    yield "Put the widget in the top right corner."

    board.move(widget, center_x=200, center_y=150)
    yield "Put the widget in the center."

def test_vector_position_arguments():
    board.move(widget, bottom_left=(0, 0))
    yield "Put the widget in the bottom left."

    board.move(widget, bottom_center=(200, 0))
    yield "Put the widget in the bottom center."

    board.move(widget, bottom_right=(400, 0))
    yield "Put the widget in the bottom right."

    board.move(widget, center_left=(0, 150))
    yield "Put the widget in the top left."

    board.move(widget, center=(200, 150))
    yield "Put the widget in the top left."

    board.move(widget, center_right=(400, 150))
    yield "Put the widget in the center right."

    board.move(widget, top_left=(0, 300))
    yield "Put the widget in the top left."

    board.move(widget, top_center=(200, 300))
    yield "Put the widget in the top center."

    board.move(widget, top_right=(400, 300))
    yield "Put the widget in the top right."

def test_rect_argument():
    rect = board.rect.get_shrunk(10)
    rect.center = 200, 150
    board.move(widget, rect=rect)
    yield "Fill the board with a 10 px margin."

def test_scalar_position_percent_arguments():

    board.move(widget, left_percent=0.0, top_percent=1.0)
    yield "Put the widget in the top left corner."

    board.move(widget, right_percent=1.0, bottom_percent=0.0)
    yield "Put the widget in the bottom right corner."

    board.move(widget, center_x_percent=0.5, center_y_percent=0.5)
    yield "Put the widget in the center."

def test_vector_position_percent_arguments():
    board.move(widget, bottom_left_percent=(0, 0))
    yield "Put the widget in the bottom left."

    board.move(widget, bottom_center_percent=(0.5, 0))
    yield "Put the widget in the bottom center."

    board.move(widget, bottom_right_percent=(1.0, 0))
    yield "Put the widget in the bottom right."

    board.move(widget, center_left_percent=(0, 0.5))
    yield "Put the widget in the top left."

    board.move(widget, center_percent=(0.5, 0.5))
    yield "Put the widget in the top left."

    board.move(widget, center_right_percent=(1.0, 0.5))
    yield "Put the widget in the center right."

    board.move(widget, top_left_percent=(0, 1.0))
    yield "Put the widget in the top left."

    board.move(widget, top_center_percent=(0.5, 1.0))
    yield "Put the widget in the top center."

    board.move(widget, top_right_percent=(1.0, 1.0))
    yield "Put the widget in the top right."

def test_size_arguments():
    board.move(widget, center_percent=(0.5, 0.5), width=200, height=100)
    yield "Make the widget 200 px wide and 100 px tall"
    
    board.move(widget, center_percent=(0.5, 0.5),
            width_percent=0.8, height_percent=0.6)
    yield "Make the widget 80% wide and 60% tall"

def test_absolute_claims():
    board.move(widget, left=0, bottom=0)
    yield "Claim just enough space for the widget."

    board.move(widget, left=100, bottom=0)
    yield "Claim 100 extra pixels on the left."

    board.move(widget, center_x=100, bottom=0)
    yield "Claim 75 extra pixels on the left."

    board.move(widget, right=100, bottom=0)
    yield "Claim 50 extra pixels on the left."

    board.move(widget, left=0, bottom=100)
    yield "Claim 100 extra pixels on the bottom."

    board.move(widget, left=0, center_y=100)
    yield "Claim 75 extra pixels on the bottom."

    board.move(widget, left=0, top=100)
    yield "Claim 50 extra pixels on the bottom."

def test_absolute_size_percent_position_claims():
    board.move(widget, left_percent=0.5, bottom=0)
    yield "Claim 50 extra pixels on the left."

    board.move(widget, center_x_percent=0.5, bottom=0)
    yield "Claim no extra space."

    board.move(widget, right_percent=0.5, bottom=0)
    yield "Claim 50 extra pixels on the right."

    board.move(widget, left=0, bottom_percent=0.5)
    yield "Claim 50 extra pixels on the bottom."

    board.move(widget, left=0, center_y_percent=0.5)
    yield "Claim no extra space."

    board.move(widget, left=0, top_percent=0.5)
    yield "Claim 50 extra pixels on the top."

def test_percent_size_absolute_position_claims():
    board.move(widget, width_percent=1.0, left=0, bottom=0)
    yield "Claim no extra space."

    board.move(widget, width_percent=0.5, left=25, bottom=0)
    yield "Claim 25 extra pixels on the left and right."

    board.move(widget, width_percent=0.5, left=100, bottom=0)
    yield "Claim 75 extra pixels on the left."

    board.move(widget, width_percent=0.5, right=50, bottom=0)
    yield "Claim 50 extra pixels on the right."

    board.move(widget, width_percent=0.5, right=100, bottom=0)
    yield "Claim 50 extra pixels on the left."

    board.move(widget, width_percent=0.5, center_x=25, bottom=0)
    yield "Claim 50 extra pixels on the right."

    board.move(widget, width_percent=0.5, center_x=50, bottom=0)
    yield "Claim 25 extra pixels on the left and right."

    board.move(widget, width_percent=0.5, center_x=100, bottom=0)
    yield "Claim 75 extra pixels on the left."

    board.move(widget, height_percent=1.0, left=0, bottom=0)
    yield "Claim no extra space."

    board.move(widget, height_percent=0.5, left=0, bottom=25)
    yield "Claim 25 extra pixels on the bottom and top."

    board.move(widget, height_percent=0.5, left=0, bottom=100)
    yield "Claim 75 extra pixels on the bottom."

    board.move(widget, height_percent=0.5, left=0, top=50)
    yield "Claim 50 extra pixels on the top."

    board.move(widget, height_percent=0.5, left=0, top=100)
    yield "Claim 50 extra pixels on the bottom."

    board.move(widget, height_percent=0.5, left=0, center_y=25)
    yield "Claim 50 extra pixels on the top."

    board.move(widget, height_percent=0.5, left=0, center_y=50)
    yield "Claim 25 extra pixels on the bottom and top."

    board.move(widget, height_percent=0.5, left=0, center_y=100)
    yield "Claim 75 extra pixels on the bottom."

def test_percent_claims():
    board.move(widget, width_percent=0.5, left_percent=0.0, bottom=0)
    yield "Claim 50 extra pixels on the right."

    board.move(widget, width_percent=0.5, left_percent=0.5, bottom=0)
    yield "Claim 50 extra pixels on the left."

    board.move(widget, width_percent=0.5, center_x_percent=0.5, bottom=0)
    yield "Claim 25 extra pixels on the left and right."

    board.move(widget, width_percent=0.5, right_percent=0.5, bottom=0)
    yield "Claim 50 extra pixels on the right."

    board.move(widget, width_percent=0.5, right_percent=1.0, bottom=0)
    yield "Claim 50 extra pixels on the left."

    board.move(widget, height_percent=0.5, bottom_percent=0.0, left=0)
    yield "Claim 50 extra pixels on the top."

    board.move(widget, height_percent=0.5, bottom_percent=0.5, left=0)
    yield "Claim 50 extra pixels on the bottom."

    board.move(widget, height_percent=0.5, center_y_percent=0.5, left=0)
    yield "Claim 25 extra pixels on the top and bottom."

    board.move(widget, height_percent=0.5, top_percent=0.5, left=0)
    yield "Claim 50 extra pixels on the top."

    board.move(widget, height_percent=0.5, top_percent=1.0, left=0)
    yield "Claim 50 extra pixels on the bottom."

def test_layers():
    purple = glooey.Placeholder(48, 50, 'purple')

    board.move(widget, center_left=(175, 150), layer=1)
    board.add(purple, center_left=(175, 150), layer=2)
    yield "The purple widget on top."

    board.move(widget, center_left=(175, 150), layer=2)
    board.move(purple, center_left=(175, 150), layer=1)
    yield "The orange widget on top."

    board.remove(purple)
    yield "Remove the purple widget"

@run_demos.on_space(gui) 
def test_board():
    # Make sure the board can correctly place widgets.
    board.size_hint = 400, 300
    board.add(widget, left=0, bottom=0)

    yield from test_scalar_position_arguments()
    yield from test_vector_position_arguments()
    yield from test_rect_argument()
    yield from test_scalar_position_percent_arguments()
    yield from test_vector_position_percent_arguments()
    yield from test_size_arguments()

    # Make sure the board can claim enough space for its children.
    board.size_hint = 0, 0

    yield from test_absolute_claims()
    yield from test_absolute_size_percent_position_claims()
    yield from test_percent_size_absolute_position_claims()
    yield from test_percent_claims()

    # Make sure the board layers its children correctly.
    board.size_hint = 400, 300
    yield from test_layers()

    # Reset the board.
    board.clear()
    yield "Clear the board."


pyglet.app.run()


