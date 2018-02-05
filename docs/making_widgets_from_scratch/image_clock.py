#!/usr/bin/env python3

import pyglet
import glooey
import autoprop
import datetime

@autoprop
class ImageClock(glooey.Widget):
    custom_face = None
    custom_hour_hand = None
    custom_minute_hand = None
    custom_second_hand = None

    def __init__(self):
        super().__init__()
        self._images = {
                'face': self.custom_face,
                'hour': self.custom_hour_hand,
                'min': self.custom_minute_hand,
                'sec': self.custom_second_hand,
        }
        self._sprites = {
                'face': None,
                'hour': None,
                'min': None,
                'sec': None,
        }

    def get_face(self):
        return self._images['face']

    def set_face(self, image):
        self._images['face'] = image
        self._repack()

    def get_hour_hand(self):
        return self._images['hour']

    def set_hour_hand(self, image):
        self._images['hour'] = image
        self._repack()

    def get_minute_hand(self):
        return self._images['min']

    def set_minute_hand(self, image):
        self._images['min'] = image
        self._repack()

    def get_second_hand(self):
        return self._images['sec']

    def set_second_hand(self, image):
        self._images['sec'] = image
        self._repack()

    def on_update(self, dt):
        self._draw()

    def do_attach(self):
        pyglet.clock.schedule_interval(self.on_update, 1)

    def do_detach(self):
        pyglet.clock.unschedule(self.on_update)
    
    def do_claim(self):
        width, height = 0, 0
        min_size = 0

        if self._images['face'] is not None:
            width = self._images['face'].width
            height = self._images['face'].height

        # Since the hands can rotate, we need to claim enough space to fit the 
        # largest hand in both dimensions.

        for k in ['hour', 'min', 'sec']:
            if self._images[k] is not None:
                min_size = max(min_size, self._images[k].width)
                min_size = max(min_size, self._images[k].height)

        return max(width, min_size), max(height, min_size)

    def do_regroup(self):
        for sprite in self._sprites.values():
            if sprite is not None:
                sprite.batch = self.batch
                sprite.group = self._get_layer(k)

    def do_draw(self):
        now = datetime.datetime.now()
        rotations = {
                'hour': 360 * now.hour / 12,
                'min': 360 * now.minute / 60,
                'sec': 360 * now.second / 60,
        }
        for k in self._sprites:
            if self._images[k] is None:
                if self._sprites[k] is not None:
                    self._sprite.delete()
                    self._sprites[k] = None
                continue

            if self._sprites[k] is None:
                self._sprites[k] = pyglet.sprite.Sprite(
                        self._images[k],
                        batch=self.batch,
                        group=self._get_layer(k),
                )
            else:
                self._sprites[k].image = self._images[k]

            # The following lines assume that each image has `anchor_x` and 
            # `anchor_y` properties indicating where the center of the clock 
            # should be.

            self._sprites[k].x = self.rect.center_x
            self._sprites[k].y = self.rect.center_y
            if k in rotations:
                self._sprites[k].rotation = rotations[k]

    def do_undraw(self):
        for k in self._sprites:
            if self._sprites[k] is not None:
                self._sprites[k].delete()
                self._sprites[k] = None
             
    def _get_layer(self, key):
        layers = {
                'face': 0,
                'hour': 1,
                'min': 2,
                'sec': 3,
        }
        return pyglet.graphics.OrderedGroup(layers[key], self.group)


class VintageClock(ImageClock):
    custom_face = pyglet.image.load('face.png')
    custom_face.anchor_x, custom_face.anchor_y = 150, 150
    custom_hour_hand = pyglet.image.load('hour_hand.png')
    custom_hour_hand.anchor_x, custom_hour_hand.anchor_y = 13, 0
    custom_minute_hand = pyglet.image.load('minute_hand.png')
    custom_minute_hand.anchor_x, custom_minute_hand.anchor_y = 9, 0
    custom_second_hand = pyglet.image.load('second_hand.png')
    custom_second_hand.anchor_x, custom_second_hand.anchor_y = 4, 24


window = pyglet.window.Window()
gui = glooey.Gui(window)
gui.add(VintageClock())
pyglet.app.run()
