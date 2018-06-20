"""
This modules provides different types of shadows aimed at a more appealing UI design.
Shadows' aim is to highlight widgets with an increased contrast with their background.


"""
from collections import namedtuple

from pygame.constants import SRCALPHA, BLEND_RGBA_MULT, BLEND_RGBA_SUB
from pygame.surface import Surface

from draw import blur
from maths import Pos

Offset = namedtuple("Offset", "top left bottom right")


class Shadow:
    def __init__(self, dx=2, dy=2, blur=2, strength=64):
        self.dx = dx
        self.dy = dy
        self.blur = blur
        self.strength = strength

    def __bool__(self):
        return bool(self.dx or self.dy or self.blur)

    @property
    def offset(self):
        return Offset(-min(self.dy, 0) + 2 * self.blur,
                      -min(self.dx, 0) + 2 * self.blur,
                      max(self.dy, 0) + 2 * self.blur,
                      max(self.dx, 0) + 2 * self.blur)

    @property
    def bg_offset(self):
        x = -self.dx if self.dx < 0 else 0
        y = -self.dy if self.dy < 0 else 0
        x += 2 * self.blur
        y += 2 * self.blur
        return Pos(x, y)

    @property
    def extra_size(self):
        return abs(self.dx) + 4 * self.blur, abs(self.dy) + 4 * self.blur

    def create_from(self, widget):
        base = widget.background_image.copy()  # type: Surface
        # base.fill((0, 0, 0, 255), None, BLEND_RGBA_MIN)

        size = (base.get_width() + abs(self.dx) + 4 * self.blur,
                base.get_height() + abs(self.dy) + 4 * self.blur)
        surf = Surface(size, SRCALPHA)
        surf.blit(base, (2 * self.blur + max(0, self.dx),
                         2 * self.blur + max(0, self.dy)))
        if self.blur:
            surf = blur(surf, self.blur)

        surf.blit(base, (2 * self.blur, 2 * self.blur), None, BLEND_RGBA_SUB)
        surf.fill((0, 0, 0, self.strength), None, BLEND_RGBA_MULT)
        return surf


class NoShadow(Shadow):
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
