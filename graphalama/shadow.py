"""
This modules provides different types of shadows aimed at a more appealing UI design.
Shadows' aim is to highlight widgets with an increased contrast with their background.
"""

from collections import namedtuple

from pygame.constants import SRCALPHA, BLEND_RGBA_MULT, BLEND_RGBA_SUB
from pygame.surface import Surface

from .draw import blured
from .maths import Pos

Offset = namedtuple("Offset", "top left bottom right")


class Shadow:
    """
    Describe the shadow behind a widget.
    """

    def __init__(self, dx=2, dy=2, blur=2, strength=100):
        """
        Describe the shadow behind a widget.

        :param int dx: horizontal pixel shift, a negative value is a shift to the left
        :param int dy: vertical pixel shift, a negative value is an upward shift
        :param int blur: blur radius
        :param int strength: transparency of the shadow between 0 and 255
        """

        self.dx = dx
        self.dy = dy
        self.blur = blur
        self.strength = strength

    def __repr__(self):
        return "Shadow({}, {}, {}, {})".format(self.dx, self.dy, self.blur, self.strength)

    def __bool__(self):
        return bool((self.dx or self.dy or self.blur) and self.strength)

    @property
    def offset(self):
        """The magin in pixel around the widget requiered for the shadow."""
        return Offset(-min(self.dy, 0) + 2 * self.blur,
                      -min(self.dx, 0) + 2 * self.blur,
                      max(self.dy, 0) + 2 * self.blur,
                      max(self.dx, 0) + 2 * self.blur)

    @property
    def bg_offset(self):
        """The offset between the topleft cornor of the shadow and the topleft corner of the widget."""
        return Pos(self.offset.left,
                   self.offset.top)

    @property
    def extra_size(self):
        """The total size requiered by the shadow, not counting the widget."""
        return Pos(abs(self.dx) + 4 * self.blur,
                   abs(self.dy) + 4 * self.blur)

    def create_from(self, widget):
        """
        Create a surface with the shadow.

        The surface has a size of widget.size + shadow.extra_size.
        """

        base = widget.shape.get_mask()  # type: Surface
        # The shadow surface
        surf = Surface(base.get_size() + self.extra_size, SRCALPHA)
        # We keep a margin of 2*blur on each side to avoid side effects
        # And we place the shadow (dx, dy) from where the background is
        surf.blit(base, self.bg_offset + (self.dx, self.dy))

        if self.blur:
            surf = blured(surf, self.blur)

        # We remove the shadow from where the widget is, so semi-transparent widget don't get shaded
        surf.blit(base, self.bg_offset + widget.shape.bg_offset, special_flags=BLEND_RGBA_SUB)
        # We color the shadow's mask with the actual shadow color
        surf.fill((0, 0, 0, self.strength), None, BLEND_RGBA_MULT)

        return surf


class NoShadow(Shadow):
    """A shadow objet that doesn't create any shadow behind the widget."""

    def __init__(self):
        super().__init__(0, 0, 0)

    def __bool__(self):
        return False

    @property
    def offset(self):
        return Offset(0, 0, 0, 0)

    @property
    def bg_offset(self):
        return Pos(0, 0)

    @property
    def extra_size(self):
        return Pos(0, 0)

    def create_from(self, widget):
        raise NotImplemented
