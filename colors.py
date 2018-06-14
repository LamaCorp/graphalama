"""
This module provides functions and classes to manipulate colors and grdients.
"""
import pygame.gfxdraw

from constants import WHITE, BLACK


def bw_contrasted(color, threshold=200):
    """Return a color (B or W) of oposite balance : it will be easy to distinguish both"""
    return [WHITE, BLACK][sum(color) / 3 > threshold]


def mix(color1, color2, pos=0.5):
    """
    Return the mix of two colors at a state of :pos:

    Retruns color1 * pos + color2 * (1 - pos)
    The return color always has an alpha value
    """

    if len(color1) < 4:
        color1 += 255,
    if len(color2) < 4:
        color2 += 255,

    opp_pos = 1 - pos

    red = color1[0] * pos + color2[0] * opp_pos
    green = color1[1] * pos + color2[1] * opp_pos
    blue = color1[2] * pos + color2[2] * opp_pos
    alpha = color1[3] * pos + color2[3] * opp_pos
    return int(red), int(green), int(blue), int(alpha)


class Color:
    def __init__(self, rgb_or_rgba):
        self.color = tuple(rgb_or_rgba)

    def paint(self, surf):
        surf.fill(self.color)


class Gradient(Color):
    def __init__(self, start, end, horizontal=True):
        super().__init__(start)
        self.end = tuple(end)
        self.horizontal = horizontal

    def paint(self, surf):
        width, height = surf.get_size()

        if self.horizontal:
            for x in range(width):
                color = mix(self.color, self.end, 1 - x/(width-1))
                pygame.gfxdraw.vline(surf, x, 0, height, color)
        else:
            for y in range(height):
                color = mix(self.color, self.end, 1 - y/(height-1))
                pygame.gfxdraw.hline(surf, 0, width, y, color)

