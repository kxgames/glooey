I'm trying to come up with new names for the widget rects, and if possible to 
simplify their user-facing interface.

There are really only two things the user cares about: how much space they ask 
for (or more precisely, the minimum space required to render the widget) and 
how much space they get.  How much space they ask for is determined by the 
claim() function.  I also want to add a method in Widget that would allow they 
user to request space without having to override claim().  Part of me thinks 
this method should have "claim" in its name, but another part of me thinks that 
would be confusing.

Right now, here are the actual Widget rect members:

- rect: the space the widget should use for drawing itself
- min_width, min_height: the values returned by claim()
- claimed_width, claimed_height: min_width/min_height, accounting for padding
- assigned_rect: the amount space given to the widget by its parent.

The publicly visible rects are:

- rect
- claimed_rect: accounting for padding

The problem is that padding muddies the issue of what the claim actually is.  
For the user implementing do_claim(), its the minimal amount of space needed 
for the widget.  For container widgets allocating space, it's that plus 
padding.  Well, I guess there is a certain logic there.  It is the minimum 
amount of space the widget needs, considering only things that are within the 
purview of the code in question. 

I could change the name:

    def request_space(self, width, height):
        pass

    def do_request_space(self):
        return width, height

Or I could keep the name:

    def set_min_claim(self, width, height):
        pass

or

    def set_min_size(self):
        pass

You know, I just kinda like that last one the most.  It just kinda says what it 
means the most.  It's a pretty minimal change; I don't even have to create a 
new member variable, I can just piggyback on min_height and min_width.

I decided to use the names:

    def set_size_hint(self, ...):
        pass

    def set_width_hint(self, ...):
        pass

    def set_height_hint(self, ...):
        pass

I like that these names do a good job implying that this attribute is user-set 
and optional.
