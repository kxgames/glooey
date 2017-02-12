Should `del` mean "set to nothing", or should it mean "reset to the default"?

For Image.image, "set to nothing" makes more sense to me, since there's not 
really a natural way to say "no image" using set_image().

But for Widget.padding, "reset to default" makes more sense to me, since in 
this case there is a natural way to say "no padding" with set_padding().

Maybe I should be more judicious in my use of `del_*()`, and reserve it for 
attributes that can't be naturally unset.  (So in the example above, I just 
wouldn't define Widget.del_padding()).
