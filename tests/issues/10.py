#!/usr/bin/env python3

# Regarding the first error message you reported, that seems buggy to me 
# because it's straight-up lying to you: it's saying that the Gui can't fit 
# it's children, but also that the Gui is much bigger than its children.  
# Something has to be wrong there.
#
# Regarding the example that crashes immediately, this is expected behavior.  I 
# just made the decision to not allow GUIs that are too small to fit all their 
# children.  My reasons for this were:
# 
# 1. I thought that allowing widgets to shrink below their "minimum" sizes 
#    would add a lot of complexity, and I figured that most games just use 
#    fixed size windows anyways, so I didn't think this complexity would be 
#    worth it.
#
# 2. I thought that shrinking widgets below their minimum size would just cause 
#    things to look wrong.  Images and text could be overlapping, some buttons 
#    might be covered such that they can't be clicked, etc.  I figured that 
#    it'd be better to let the designer know that their GUI looks wrong, so 
#    that they can redesign it accordingly, than to soldier on.
#
# I only really have my use-cases in mind, though.  I'd like to hear more about 
# what you're trying to achieve with a dynamically resizing GUI.  
# 
# Also, I should mention that you can get around this problem by putting the 
# part of the GUI that's too big inside a ScrollBox widget.  Scroll boxes can 
# be arbitrarily small, so the Gui won't complain about not being able to fit 
# things.  If the window is big enough to fit everything, the scroll box won't 
# do anything, but if the window is too small, the scroll box will let the user 
# scroll around to see everything.
#
# You could also write a custom container that rearranges it's children as 
# necessary to make them all fit, but that would be a bigger undertaking.  
# (Just made harder by the fact that I haven't written the relevant 
# documentation yet...)
#
