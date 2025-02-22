"""
Math functions and object useful in any code.
"""
from collections import namedtuple
from math import sqrt, cos, sin, pi

import pygame


def clamp(value, min=None, max=None):
    """Clamp the value between min and max. Only one boundary can be specified."""
    if min is not None and value < min:
        return min

    if max is not None and value > max:
        return max

    return value

def merge_rects(rect1, rect2):
    """Return the smallest rect containning two rects"""
    r = pygame.Rect(rect1)
    t = pygame.Rect(rect2)

    right = max(r.right, t.right)
    bot = max(r.bottom, t.bottom)
    x = min(t.x, r.x)
    y = min(t.y, r.y)

    return pygame.Rect(x, y, right - x, bot - y)


class Pos(namedtuple("Pos", ('x', 'y'))):
    """A vector."""

    def __new__(cls, *c):
        if len(c) == 0:
            c = (0, 0)
        elif len(c) == 1:
            assert len(c[0]) == 2
            c = c[0]
        elif len(c) > 2:
            raise TypeError

        # noinspection PyArgumentList
        return tuple.__new__(cls, c)

    def __add__(self, other):
        return Pos(self[0] + other[0], self[1] + other[1])

    __radd__ = __add__

    def __sub__(self, other):
        return Pos(self[0] - other[0], self[1] - other[1])

    def __rsub__(self, other):
        return Pos(other[0] - self[0], other[1] - self[1])

    def __neg__(self):
        return Pos(-self[0], -self[1])

    def __mul__(self, other):
        return Pos(self[0] * other, self[1] * other)

    __rmul__ = __mul__

    def __truediv__(self, other: int):
        return Pos(self[0] / other, self[1] / other)

    def __floordiv__(self, other: int):
        return Pos(self[0] // other, self[1] // other)

    @property
    def t(self):
        """The vecor as a tuple"""
        return self[0], self[1]

    @property
    def ti(self):
        """The vecor as a tuple of integer (round to closest)"""
        return round(self[0]), round(self[1])

    def squared_norm(self):
        """Return the squared norm of the vector"""
        return self[0] ** 2 + self[1] ** 2

    def norm(self):
        """Return the norm of the vector"""
        return sqrt(self.squared_norm())

    def rotate(self, degree):
        c = cos(pi / 180 * degree)
        s = sin(pi / 180 * degree)
        return Pos(c*self[0] + s*self[1],
                   s*self[0] - c*self[1])

