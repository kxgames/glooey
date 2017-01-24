Also, I this I should tweak the repack() interface a bit, so the parent knows 
if the child requesting repacking got bigger or smaller.  Right now repack is 
only called if the child got smaller, but this leaves parents with no way to 
react to children getting smaller.  That's forced me to proliferate 
repack(force=True) calls in "leaf" widgets, but that's a hack.  Probably the 
only reason I haven't run into real problems with it yet is that all the 
tests I've written have had only one or two levels of hierarchy.

The reason I did it this way was to prevent every size change from causing 
the entire GUI to be repacked, 


