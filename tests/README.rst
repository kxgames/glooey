How to run tests
================
The tests are all executable python scripts named ``demo_*.py``.  They are 
meant to be executed from the directory they live in.  Most of the tests test a 
single widget, and you can press the "space" key to cycle through different 
configurations of that widget.  A brief sentence in the lower right corner 
describes what you should expect to see.

You can also run all the tests at once::

   $ pytest -D .

How to write tests
==================
1. Begin with the widget being tested is a "typical" state, e.g. a few rows and 
   columns for a grid, a few states for a deck, some text for a label, etc.

2. Cycle through a more thorough screening of settings as the tester presses 
   the space bar.
