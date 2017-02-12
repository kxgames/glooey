For Buttons, I'd like to have a way to specify different horizontal and 
vertical paddings for the text.  Specifically consider a button that htiles to 
fit its text and which has large endcaps.  It will only claim enough space to 
fit the text, so when it's rendered the text will flow over the endcaps.

The way to address this is to specify a horizontal padding for the text, so the 
button will ultimately claim enough space for its text and its endcaps.  I 
would add this feature to the stack class, and set it via an `hpad` parameter 
to add() and friends.  However, right now glooey doesn't have the concept of 
horizontal and vertical padding, just padding.  And it's easy to imagine all 
the other containers (e.g. Grid) wanting this feature as well.  So I think I 
should spend some time finding a general way to add support for this to every 
container.

Of course, then I might also want `rpad`, `lpad`, `tpad`, and `bpad`.  And I 
don't want to add 7 padding arguments to every single add() method.  Maybe I 
should just use \*\*kwargs.  That would work fine as long as I didn't want any 
other kwargs, otherwise I'd have to deconvolute them.  (That said, it wouldn't 
bee too hard to wirte a helper function to do that.  Look at the callee's 
signature, throw out any keywords that aren't mentioned, done.)

---

Ultimately, I resolved this issue by moving padding (and placement, which I 
renamed to alignment) into the Widget class.
