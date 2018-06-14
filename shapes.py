"""
This module defines a bunch of shapes classes.

Shapes are used to defnie the form of an object without any content or color.
A shape class defines two important methods:
 - `get_mask` that creates a white surface of a given size
   with different levels of transparency for gradients and
   a transparency of 0 when a pixel is outside of the shape.
 - `is_inside` to tell if a pixel is inside the shape.

"""
from math import pi

import pygame.examples.fonty

from constants import DEFAULT
from draw import roundrect, polygon
from maths import clamp

INSIDE = (255, 255, 255, 255)
OUTSIDE = (255, 255, 255, 0)
HALFSQRT2 = 0.709


class Rectangle:
    """
    The base shape that represent a rectangle.
    """

    def __init__(self, size, border=DEFAULT, shadow_offset=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        """
        The most basic shape: a rectangle.

        :param (int, int) size:     a tuple (width, height) in pixels
        :param int border:          the border size in pixels
        :param (int, int) min_size: a tuple (min_width, min_height) in pixels.
        :param (int, int) max_size: a tuple (max_width, max_height) in pixels. One or two elements can be None if no maximum size.
        """

        self.widget = None

        self.exact_size = size
        self.size = size
        self.border = border if border else 0
        self.shadow_offset = shadow_offset if shadow_offset else (0, 0)
        self.min_size = min_size if min_size else (5, 5)
        self.max_size = max_size if max_size else (None, None)

    @property
    def total_size(self):
        s = self.size
        return s[0] + self.shadow_offset[0], s[1] + self.shadow_offset[1]

    @property
    def size(self):
        return (clamp(round(self.exact_size[0]), self.min_size[0], self.max_size[0]),
                clamp(round(self.exact_size[1]), self.min_size[1], self.max_size[1]))

    @size.setter
    def size(self, value):
        self.exact_size = value
        if self.widget:
            self.widget.invalidate()  # so we re-draw the img on next render


    def get_mask(self):
        """
        Creates a white surface of the shape size
        with different levels of transparency for gradients and
        a transparency of 0 when a pixel is outside of the shape.
        """

        mask = pygame.Surface(self.size, pygame.SRCALPHA)
        mask.fill(INSIDE)
        return mask

    def create_border_mask(self):
        mask = self.get_mask()
        mask.fill(OUTSIDE, self.inside_surf())
        return mask

    def inside_surf(self):
        """Return the rectangle inside the shape to draw content of widgets."""
        s = self.size
        return pygame.Rect((self.border, self.border),
                           (s[0] - 2*self.border,
                            s[1] - 2*self.border))

    def is_inside(self, point):
        """
        Return true if the point is inside the shape.

        The coordinate of the point are relative of the topleft of the shape (topleft = (0, 0))
        """
        s = self.size
        return point[0] < s[0] and point[1] < s[1]


class RoundedRect(Rectangle):
    def __init__(self, size, rounding=20, percent=True, border=DEFAULT, shadow_offset=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        super().__init__(size, border, shadow_offset, min_size, max_size)
        self.percent = percent
        self.rounding = rounding

    @property
    def exact_rounding(self):
        """Return the rounding in pixels."""
        if self.percent:
            return int(min(self.size) * self.rounding / 100 / 2)
        return self.rounding

    def get_mask(self):
        mask = pygame.Surface(self.size, pygame.SRCALPHA)
        roundrect(mask, mask.get_rect(), INSIDE, self.rounding, self.percent)
        return mask

    def create_border_mask(self):
        mask = self.get_mask()
        temp = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        temp.fill((0,0,0,1))
        roundrect(temp, temp.get_rect().inflate(-2*self.border, -2*self.border), INSIDE, self.rounding, self.percent)
        mask.blit(temp, (0, 0), None, pygame.BLEND_RGBA_SUB)
        return mask

    def inside_surf(self):
        delta = (1 - HALFSQRT2) * self.exact_rounding + self.border
        return pygame.Rect(delta, delta, self.size[0] - 2 * delta, self.size[1] - 2 * delta)

    def is_inside(self, point):
        super(RoundedRect, self).is_inside(point)


class Circle(RoundedRect):
    def __init__(self, diameter, border=DEFAULT, shadow_offset=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        super().__init__((diameter, diameter), 100, True, border, shadow_offset, min_size, max_size)


class PolarCurve(Rectangle):
    def __init__(self, size, x_of_t, y_of_t, border=DEFAULT, shadow_offset=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        """

        :param size:
        :param fun: A function of an angle, in radians that creates a convex shape
        :param min_size:
        :param max_size:
        """

        self.x = x_of_t
        self.y = y_of_t

        super().__init__(size, border, shadow_offset, min_size, max_size)

    def get_mask(self):
        mask = pygame.Surface(self.size, pygame.SRCALPHA)

        pts = self.get_curve_points(1000)
        polygon(mask, pts, (255, 255, 255, 255))

        return mask

    def get_curve_points(self, nb_iterations):
        pts = []
        for t in range(nb_iterations):
            t = t / (nb_iterations - 1) * 2 * pi

            x = self.x(t) # (16 * sin(t) ** 3) / 32
            y = self.y(t) # (-13 * cos(t) + 5 * cos(2 * t) + 2 * cos(3 * t) + cos(4 * t)) / 32

            pts.append((x, y))

        # post treatment

        dist = 2
        last = 10000000, 42
        for i, (x, y) in enumerate(pts[:]):
            if (last[0] - x) ** 2 + (last[1] - y) ** 2 < dist ** 2:
                pts.remove((x, y))
            else:
                last = x, y

        minix = min(pts, key=lambda x: x[0])[0]
        miniy = min(pts, key=lambda x: x[1])[1]

        maxix = max(pts, key=lambda x: x[0])[0]
        maxiy = max(pts, key=lambda x: x[1])[1]

        for i, (x, y) in enumerate(pts):
            pts[i] = (int((x - minix) / (maxix - minix) * self.size[0]),
                      int((y - miniy) / (maxiy - miniy) * self.size[1]))
        return pts

    def inside_surf(self):
        return super().inside_surf()

    def is_inside(self, point):
        return super().is_inside(point)
