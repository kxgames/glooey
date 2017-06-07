#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt.  Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam. Maecenas tincidunt enim elementum turpis blandit tempus. Nam lectus justo, adipiscing vitae ultricies egestas, porta nec diam. Aenean ac neque tortor. Cras tempus lacus nec leo ultrices suscipit. Etiam sed aliquam tortor. Duis lacus metus, euismod ut viverra sit amet, pulvinar sed urna.\n\nAenean ut metus in arcu mattis iaculis quis eu nisl. Donec ornare, massa ut vestibulum vestibulum, metus sapien pretium ante, eu vulputate lorem augue vestibulum orci. Donec consequat aliquam sagittis. Sed in tellus pretium tortor hendrerit cursus congue sit amet turpis. Sed neque lacus, lacinia ut consectetur eget, faucibus vitae lacus. Integer eu purus ac purus tempus mollis non sed dui. Vestibulum volutpat erat magna. Etiam nisl eros, eleifend a viverra sed, interdum sollicitudin erat. Integer a orci in dolor suscipit cursus. Maecenas hendrerit neque odio. Nulla orci orci, varius id viverra in, molestie vel lacus. Donec at odio quis augue bibendum lobortis nec ac urna. Ut lacinia hendrerit tortor mattis rhoncus. Proin nunc tortor, congue ac adipiscing sit amet, aliquet in lorem. Nulla blandit tempor arcu, ut tempus quam posuere eu. In magna neque, venenatis nec tincidunt vitae, lobortis eget nulla."
label = glooey.Label(text, line_wrap=640)
gui.add(label)

pyglet.app.run()

