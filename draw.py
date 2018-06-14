# coding=utf-8

"""
This is a module for easy drawings.
Every function provides anti-aliased shapes.
"""

import pygame
from pygame import gfxdraw
from pygame.constants import SRCALPHA, BLEND_RGBA_MAX, BLEND_RGBA_MIN
from pygame.math import Vector2

from constants import BLACK


def line(surf, start, end, color=BLACK, width=1):
    """Draws an antialiased line on the surface."""

    width = round(width, 1)
    if width == 1:
        # return pygame.draw.aaline(surf, color, start, end)
        return gfxdraw.line(surf, *start, *end, color)

    # noinspection PyArgumentList
    start = Vector2(start)
    # noinspection PyArgumentList
    end = Vector2(end)

    line_vector = end - start
    half_side = line_vector.normalise().rotate(90) * width / 2

    point1 = start + half_side
    point2 = start - half_side
    point3 = end - half_side
    point4 = end + half_side

    # noinspection PyUnresolvedReferences
    liste = [
        (point1.x, point1.y),
        (point2.x, point2.y),
        (point3.x, point3.y),
        (point4.x, point4.y)
    ]

    rect = polygon(surf, liste, color)

    return rect


def circle(surf, xy, r, color=BLACK):
    """Draw an filled circle on the given surface"""

    x, y = xy

    x = int(x)
    y = int(y)
    r = int(r)

    gfxdraw.filled_circle(surf, x, y, r, color)
    gfxdraw.aacircle(surf, x, y, r, color)

    r += 1
    return pygame.Rect(x - r, y - r, 2 * r, 2 * r)


def ring(surf, xy, r, width, color, antialiased=False):
    """Draws a ring"""

    r2 = r - width

    x0, y0 = xy
    x = r2
    y = 0
    err = 0

    # collect points of the inner circle
    right = {}
    while x >= y:
        right[x] = y
        right[y] = x
        right[-x] = y
        right[-y] = x

        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1

    def h_fill_the_circle(surf, color, x, y, right):
        if -r2 <= y <= r2:
            pygame.draw.line(surf, color, (x0 + right[y], y0 + y), (x0 + x, y0 + y))
            pygame.draw.line(surf, color, (x0 - right[y], y0 + y), (x0 - x, y0 + y))
        else:
            pygame.draw.line(surf, color, (x0 - x, y0 + y), (x0 + x, y0 + y))

    x = r
    y = 0
    err = 0

    while x >= y:

        h_fill_the_circle(surf, color, x, y, right)
        h_fill_the_circle(surf, color, x, -y, right)
        h_fill_the_circle(surf, color, y, x, right)
        h_fill_the_circle(surf, color, y, -x, right)

        y += 1
        if err < 0:
            err += 2 * y + 1
        if err >= 0:
            x -= 1
            err -= 2 * x + 1

    if antialiased:
        gfxdraw.aacircle(surf, x0, y0, r, color)
        gfxdraw.aacircle(surf, x0, y0, r2, color)

def roundrect(surface, rect, color, rounding=5, percent=False):
    """
    Draw an antialiased round rectangle on the surface.

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    :source: http://pygame.org/project-AAfilledRoundedRect-2349-.html
    """

    if percent:
        rounding = int(min(rect.size) * rounding / 100)

    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, (rounding, rounding))

    rounding = rectangle.blit(circle, (0, 0))
    rounding.bottomright = rect.bottomright
    rectangle.blit(circle, rounding)
    rounding.topright = rect.topright
    rectangle.blit(circle, rounding)
    rounding.bottomleft = rect.bottomleft
    rectangle.blit(circle, rounding)

    rectangle.fill((0, 0, 0), rect.inflate(-rounding.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -rounding.h))

    rectangle.fill(color, special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle, pos)


def circle2(surface, xy, r, color):
    """
    Draw an antialiased round rectangle on the surface.

    surface : destination
    xy    : top left of the circle
    color   : rgb or rgba
    r  : 0 <= radius <= 1
    """

    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0

    circle = pygame.Surface([r * 3] * 2, SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0, 255), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, (2*r, 2*r))

    circle.fill(color, special_flags=BLEND_RGBA_MAX)
    circle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)
    return surface.blit(circle, xy)


def polygon(surf, points, color):
    """Draw an antialiased filled polygon on a surface"""

    gfxdraw.aapolygon(surf, points, color)
    gfxdraw.filled_polygon(surf, points, color)

    x = min([x for (x, y) in points])
    y = min([y for (x, y) in points])
    xm = max([x for (x, y) in points])
    ym = max([y for (x, y) in points])

    return pygame.Rect(x, y, xm - x, ym - y)


__all__ = ['circle', 'line', 'polygon', 'ring', 'roundrect']
