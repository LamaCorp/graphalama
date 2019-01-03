"""
This module defines a bunch of shapes classes.

Shapes are used to defnie the form of an object without any content or color.
A shape class defines two important methods:
 - `get_mask` that creates a white surface of a given size
   with different levels of transparency for gradients and
   a transparency of 0 when a pixel is outside of the shape.
 - `is_inside` to tell if a pixel is inside the shape.

"""
from collections import namedtuple
from math import pi

import pygame.examples.fonty

from graphalama.maths import Pos
from .constants import DEFAULT
from .draw import roundrect, polygon
from .maths import clamp

INSIDE = (255, 255, 255, 255)
OUTSIDE = (255, 255, 255, 0)
HALFSQRT2 = 0.709

Margins = namedtuple("Margins", ("left", "top", "right", "bottom"))


class Padding(namedtuple("Padding", ("left", "top", "right", "bottom"))):
    def __new__(cls, *args):
        # default value of 0
        if not args:
            args = 0, 0, 0, 0

        elif len(args) == 1:
            args = args * 4
            # cls.left = cls.right = cls.top = cls.bottom = args[0]
        elif len(args) == 2:
            args = args * 2
            # cls.left = cls.right = args[0]
            # cls.top = cls.bottom = args[1]
        elif len(args) == 4:
            pass
            # cls.left = args[0]
            # cls.right = args[1]
            # cls.top = args[2]
            # cls.bottom = args[3]
        else:
            raise TypeError("Padding accepts 0, 1, 2 or 4 arguments not {}".format(len(args)))

        # noinspection PyArgumentList
        return tuple.__new__(cls, args)

    def __init__(self, *args):
        """
        Padding(padding) -> Padding: Every side has the same size
        Padding(horizontal, vertical) -> Padding: left and right have the same size and top and bottom too
        Padding(left, top, right, bottom) -> Padding: The four sides have different sizes
        """

        # This just to stop pygame from showing "incorect number of argument" error
        tuple.__init__(self)

    @property
    def extra_width(self):
        """Return the total horizontal padding"""
        return self.left + self.right

    @property
    def extra_height(self):
        """Return the total vertical padding"""
        return self.top + self.bottom


class Rectangle:
    """
    The base shape that represent a rectangle.
    """

    def __init__(self, size=DEFAULT, border=DEFAULT, padding=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        """
        The most basic shape: a rectangle.

        :param (int, int) size:     a tuple (width, height) in pixels
        :param int border:          the border size in pixels
        :param (int, int) min_size: a tuple (min_width, min_height) in pixels.
        :param (int, int) max_size: a tuple (max_width, max_height) in pixels.
            One or two elements can be None if no maximum size.
        """

        self.widget = None

        self.border = border if border else 0

        self.bg_offset = (0, 0)
        self.min_size = min_size if min_size else (5, 5)
        self.max_size = max_size if max_size else (None, None)

        if padding is DEFAULT:
            padding = 0
        self.padding = padding if isinstance(padding, Padding) else Padding(padding)

        if size is DEFAULT:
            self.auto_size = True
            size = (5, 5)  # placeholder
        else:
            self.auto_size = False

        self.exact_width = size[0]
        """A float giving a precise width for accurate resizing. Don't set it."""
        self.exact_height = size[1]
        """A float giving a precise height for accurate resizing. Don't set it."""
        self.width, self.height = size

    # Size, width, height

    @property
    def width(self):
        return clamp(round(self.exact_width), self.min_size[0], self.max_size[0])

    @width.setter
    def width(self, value):
        self.last_width = self.width
        self.exact_width = value

        if self.widget and self.last_width != self.width:
            # so we re-draw the img on next render and reposition children
            self.widget.invalidate()


    @property
    def height(self):
        return clamp(round(self.exact_height), self.min_size[1], self.max_size[1])

    @height.setter
    def height(self, value):
        self.last_height = self.height
        self.exact_height = value

        if self.widget and self.last_height != self.height:
            # so we re-draw the img on next render and reposition children
            self.widget.invalidate()

    @property
    def size(self):
        return Pos(self.width, self.height)

    @size.setter
    def size(self, value):
        self.width, self.height = value

    def get_mask(self):
        """
        Creates a white surface of the shape size
        with different levels of transparency for gradients and
        a transparency of 0 when a pixel is outside of the shape.
        """

        mask = pygame.Surface(self.size, pygame.SRCALPHA)
        mask.fill(INSIDE)
        return mask

    def get_border_mask(self):
        """
        Get a mask with only the border of the widget with alpha values at 255 and the rest at 0.
        """

        mask = self.get_mask()
        mask.fill(OUTSIDE, (self.border, self.border, self.width - 2 * self.border, self.height - 2 * self.border))
        return mask

    @property
    def margins(self):
        """Return the margin between the border of the widge and the content rectangle."""
        return Margins(self.border + self.padding.extra_height + max(0, self.bg_offset[0]),
                       self.border + max(0, self.bg_offset[1]),
                       self.border + self.padding.extra_width - min(0, self.bg_offset[0]),
                       self.border - min(0, self.bg_offset[1]))

    def content_rect(self):
        """
        Return the rectangle inside the shape to draw content and children of widgets.
        This is this availaible space to draw stuff.
        The rectangle is positioned relatively to the topleft of its widget.
        """

        return pygame.Rect((self.margins.left, self.margins.top),
                           (self.width - self.margins.left - self.margins.right,
                            self.height - self.margins.top - self.margins.bottom))

    def widget_size_from_content_size(self, size):
        """Set the shape size the that the content_rect size is `size`."""

        return (size[0] + self.margins.left + self.margins.right,
                size[1] + self.margins.top + self.margins.bottom)

    def is_inside(self, relative_point):
        """
        Return true if the point is inside the shape.

        The coordinate of the point are relative of the topleft of the shape (topleft = (0, 0))
        """

        return bool(0 < relative_point[0] < self.width and 0 < relative_point[1] < self.height)


class RoundedRect(Rectangle):
    def __init__(self, size=DEFAULT, rounding=20, percent=True, border=DEFAULT, padding=DEFAULT, min_size=DEFAULT,
                 max_size=DEFAULT):
        super().__init__(size, border, padding, min_size, max_size)

        self.percent = percent
        """If true the rounding is evalutate in percentage of the size, otherwise in pixels."""
        self.rounding = rounding
        """The amount rounded on each corner, it can be percents or pixels depending on :percent"""

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

    def get_border_mask(self):
        mask = self.get_mask()
        temp = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        temp.fill((0, 0, 0, 1))
        roundrect(temp, temp.get_rect().inflate(-2 * self.border, -2 * self.border), INSIDE, self.rounding,
                  self.percent)
        mask.blit(temp, (0, 0), None, pygame.BLEND_RGBA_SUB)
        return mask

    @property
    def margins(self):
        delta = (1 - HALFSQRT2) * self.exact_rounding

        m = super().margins
        return Margins(m.left + delta, m.top + delta, m.right + delta, m.bottom + delta)

    def widget_size_from_content_size(self, size):
        if self.percent:
            m = super().margins
            width = size[0] + m.left + m.right
            height = size[1] + m.top + m.bottom

            coeff = (1 - HALFSQRT2) * self.rounding / 100

            if width < height:
                real_width = width / (1 - coeff)
                real_height = height + real_width * coeff
            else:
                real_height = height / (1 - coeff)
                real_width = width + real_height * coeff

            return real_width, real_height

        else:
            delta = (1 - HALFSQRT2) * self.rounding
            m = super().margins

            return (size[0] + 2 * delta + m.left + m.right,
                    size[1] + 2 * delta + m.top + m.bottom)


class Circle(RoundedRect):
    def __init__(self, diameter=None, border=DEFAULT, padding=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):
        if diameter is None:
            # noinspection PyTypeChecker
            super().__init__(None, 100, True, border, padding, min_size, max_size)
        else:
            super().__init__((diameter, diameter), 100, True, border, min_size, max_size)

    # we always want the same width and height so we bind the height to the width

    @property
    def height(self):
        return self.width

    @height.setter
    def height(self, value):
        self.width = value

    def widget_size_from_content_size(self, size):
        diameter = max(size) / HALFSQRT2
        return diameter, diameter


class PolarCurve(Rectangle):
    def __init__(self, size, x_of_t, y_of_t, border=DEFAULT, padding=DEFAULT, min_size=DEFAULT, max_size=DEFAULT):

        self.x = x_of_t
        self.y = y_of_t

        super().__init__(size, border, padding, min_size, max_size)

    def get_mask(self):
        mask = pygame.Surface(self.size, pygame.SRCALPHA)

        pts = self.get_curve_points(1000)
        polygon(mask, pts, (255, 255, 255, 255))

        return mask

    def get_curve_points(self, nb_iterations):
        pts = []
        for t in range(nb_iterations):
            t = t / (nb_iterations - 1) * 2 * pi

            x = self.x(t)  # (16 * sin(t) ** 3) / 32
            y = self.y(t)  # (-13 * cos(t) + 5 * cos(2 * t) + 2 * cos(3 * t) + cos(4 * t)) / 32

            pts.append((x, y))

        # post treatment

        dist = 1
        last = pts[0]
        for i, (x, y) in enumerate(pts[1:]):
            if (last[0] - x) ** 2 + (last[1] - y) ** 2 < 1:  # dist ** 2:
                pts.remove((x, y))
            else:
                last = x, y

        minix = min(pts, key=lambda p: p[0])[0]
        miniy = min(pts, key=lambda p: p[1])[1]

        maxix = max(pts, key=lambda p: p[0])[0]
        maxiy = max(pts, key=lambda p: p[1])[1]

        for i, (x, y) in enumerate(pts):
            pts[i] = (int((x - minix) / (maxix - minix) * self.size[0]),
                      int((y - miniy) / (maxiy - miniy) * self.size[1]))
        return pts
