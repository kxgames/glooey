************
Installation
************

Installing glooey is easy::

    $ pip install glooey

The only thing to be aware of is that glooey requires `python3.6 or later  
<https://www.python.org/downloads/>`_.  If you have an earlier version of 
python, the installation will fail with a (hopefully) informative error 
message.

You may also be interested in installing the development version of glooey from 
Github.  Especially while glooey is still under active development (see the 
release schedule below), this version may have more widgets, themes, and 
features than the released version::

    $ git clone git@github.com:kxgames/glooey.git
    $ pip install ./glooey

Release Schedule
================

The glooey API is not yet considered stable.  Although I'm pretty happy with 
how the API turned out and I don't intend to make any substantial changes to 
it, the API won't be considered stable until it's been used (by myself or 
others) in a few different games and seems to have all the kinks ironed out.  I 
don't write games very quickly, so it could be 1-2 years before this happens.

Once this does happen, I will advance the version number to 1.0 and use 
`semantic versioning <semver.org>`_ to indicate which releases break or 
maintain backwards compatibility.  Until then, there is no guarantee that any 
release will maintain backwards compatibility (although I will try to use minor 
versions to indicate possibly backwards-incompatible new features and patches 
to indicate mostly backwards-compatible bug fixes).
