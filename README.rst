******************************************************
``glooey`` — An object-oriented GUI library for pyglet
******************************************************

Every game needs a user interface that matches its look and feel.  The purpose 
of ``glooey`` is to help you make such an interface.  Towards this end, 
``glooey`` provides 7 powerful placement widgets, a label widget, an image 
widget, 3 different button widgets, a text entry widget, a variety of scroll 
boxes and bars, 4 different dialog box widgets, and a variety of other 
miscellaneous widgets.  The appearance of any widget can be trivially 
customized, and ``glooey`` comes with built-in fantasy, puzzle, and 8-bit 
themes to prove it (and to help you hit the ground running if your game fits 
one of those genres).  

The philosophy behind ``glooey`` is that deriving subclasses from a basic set 
of widgets with no default style is the most elegant way to control how widgets 
look.  This approach is flexible because subclasses can customize or override 
most aspects of the basic widgets.  But it's also surprisingly succinct and 
powerful: specifying a style is usually as simple as setting a class variable, 
and styles can be easily composed using either inner classes or previously 
defined widgets.  This philosophy makes ``glooey`` easy to get started with, 
and powerful enough to support even the most complicated games.  

.. image:: https://img.shields.io/pypi/v/glooey.svg
   :target: https://pypi.python.org/pypi/glooey
.. image:: https://img.shields.io/pypi/pyversions/glooey.svg
   :target: https://pypi.python.org/pypi/glooey
.. image:: https://img.shields.io/github/workflow/status/kxgames/glooey/Test%20and%20release/master
   :target: https://github.com/kxgames/glooey/actions
.. image:: https://img.shields.io/readthedocs/glooey.svg
   :target: https://glooey.readthedocs.io/en/latest/?badge=latest

A quick example
===============
The `documentation <https://glooey.readthedocs.io/en/latest/>`_ thoroughly explains what ``glooey`` can do and how to use it, 
but here's a quick example to give a feel for what it looks like in action::

   $ pip3 install glooey

.. code-block:: python

   #!/usr/bin/env python3

   import pyglet
   import glooey

   # Define a custom style for text.  We'll inherit the ability to render text 
   # from the Label widget provided by glooey, and we'll define some class 
   # variables to customize the text style.

   class MyLabel(glooey.Label):
       custom_color = '#babdb6'
       custom_font_size = 10
       custom_alignment = 'center'

   # If we want another kind of text, for example a bigger font for section 
   # titles, we just have to derive another class:

   class MyTitle(glooey.Label):
       custom_color = '#eeeeec'
       custom_font_size = 12
       custom_alignment = 'center'
       custom_bold = True

   # It's also common to style a widget with existing widgets or with new 
   # widgets made just for that purpose.  The button widget is a good example.  
   # You can give it a Foreground subclass (like MyLabel from above) to tell it 
   # how to style text, and Background subclasses to tell it how to style the
   # different mouse rollover states:

   class MyButton(glooey.Button):
       Foreground = MyLabel
       custom_alignment = 'fill'

       # More often you'd specify images for the different rollover states, but 
       # we're just using colors here so you won't have to download any files 
       # if you want to run this code.

       class Base(glooey.Background):
           custom_color = '#204a87'

       class Over(glooey.Background):
           custom_color = '#3465a4'

       class Down(glooey.Background):
           custom_color = '#729fcff'

       # Beyond just setting class variables in our widget subclasses, we can 
       # also implement new functionality.  Here we just print a programmed 
       # response when the button is clicked.

       def __init__(self, text, response):
           super().__init__(text)
           self.response = response

       def on_click(self, widget):
           print(self.response)

   # Use pyglet to create a window as usual.

   window = pyglet.window.Window()

   # Create a Gui object, which will manage the whole widget hierarchy and 
   # interact with pyglet to handle events.

   gui = glooey.Gui(window)

   # Create a VBox container, which will arrange any widgets we give it into a 
   # vertical column.  Center-align it, otherwise the column will take up the 
   # full height of the window and put too much space between our widgets.

   vbox = glooey.VBox()
   vbox.alignment = 'center'

   # Create a widget to pose a question to the user using the "title" text 
   # style,  then add it to the top of the vbox.

   title = MyTitle("What...is your favorite color?")
   vbox.add(title)

   # Create several buttons with different answers to the above question, then 
   # add each one to the vbox in turn.

   buttons = [
          MyButton("Blue.", "Right, off you go."),
          MyButton("Blue. No yel--", "Auuuuuuuugh!"),
          MyButton("I don't know that!", "Auuuuuuuugh!"),
   ]
   for button in buttons:
      vbox.add(button)

   # Finally, add the vbox to the GUI.  It's always best to make this the last 
   # step, because once a widget is attached to the GUI, updating it or any of 
   # its children becomes much more expensive.

   gui.add(vbox)

   # Run pyglet's event loop as usual.

   pyglet.app.run()
