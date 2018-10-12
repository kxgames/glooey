#!/usr/bin/env python3

from pyglet.gl import *
from pyglet.graphics import Group, OrderedGroup
from glooey.helpers import *

class StencilGroup(Group):

    def __init__(self, parent=None):
        Group.__init__(self, parent)

    def set_state(self):
        glEnable(GL_STENCIL_TEST)
        glClear(GL_DEPTH_BUFFER_BIT)
        glClear(GL_STENCIL_BUFFER_BIT)

    def unset_state(self):
        glDisable(GL_STENCIL_TEST)


class StencilMask(OrderedGroup):

    def __init__(self, parent=None, order=0):
        super().__init__(order, parent)

    def set_state(self):
        # Disable writing the to color or depth buffers.
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glDepthMask(GL_FALSE)

        glStencilFunc(GL_NEVER, 1, 0xFF)
        glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)
        glStencilMask(0xFF)

    def unset_state(self):
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glDepthMask(GL_TRUE);


class WhereStencilIs(OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        glStencilMask(0x00)
        glStencilFunc(GL_EQUAL, 1, 0xFF)

    def unset_state(self):
        pass


class WhereStencilIsnt(OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        glStencilMask(0x00);
        glStencilFunc(GL_EQUAL, 0, 0xFF)

    def unset_state(self):
        pass



class ScissorGroup(Group):

    def __init__(self, rect=None, parent=None):
        super().__init__(parent)
        self.rect = rect

    def set_state(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_SCISSOR_TEST)
        glScissor(
                int(self.rect.left),
                int(self.rect.bottom),
                int(self.rect.width),
                int(self.rect.height),
        )

    def unset_state(self):
        glPopAttrib()


