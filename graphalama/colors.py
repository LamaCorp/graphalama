"""
This module provides functions and classes to manipulate colors and grdients.
"""
import pygame.gfxdraw
from pygame.constants import BLEND_RGBA_MULT, BLEND_RGBA_MIN

from graphalama.draw import greyscaled
from .constants import WHITE, BLACK


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


def to_color(maybe_color):
    if isinstance(maybe_color, Color):
        return maybe_color
    else:
        return Color(maybe_color)


class Color:
    def __init__(self, rgb_or_rgba):
        self.color = tuple(rgb_or_rgba)

        # post processing
        self.shade_intensity = None
        self.grey_scale = False
        self.transparency = None

    def __repr__(self):
        return "{}{}".format(type(self).__name__, self.color)

    @property
    def has_transparency(self):
        """Return true if the color has some transparency."""
        return len(self.color) > 3 and self.color[3] < 255 or self.transparency

    def _paint(self, surf):
        surf.fill(self.color)

    # post processing
    def paint(self, surf):
        self._paint(surf)

        if self.shade_intensity is not None:
            surf.fill((self.shade_intensity,) * 4, None, BLEND_RGBA_MULT)

        if self.grey_scale:
            surf.blit(greyscaled(surf), (0, 0))

        if self.transparency is not None:
            print(self.transparency)
            surf.fill((255, 255, 255, self.transparency), None, BLEND_RGBA_MIN)


class Gradient(Color):
    def __init__(self, start, end, horizontal=True):
        super().__init__(start)
        self.end = tuple(end)
        self.horizontal = horizontal

    def __repr__(self):
        return "Gradient({} -> {})".format(self.color, self.end)

    @property
    def has_transparency(self):
        return super().has_transparency or len(self.end) > 3 and self.end[3] < 255

    def _paint(self, surf):
        width, height = surf.get_size()

        if self.horizontal:
            for x in range(width):
                color = mix(self.color, self.end, 1 - x / (width - 1))
                pygame.gfxdraw.vline(surf, x, 0, height, color)
        else:
            for y in range(height):
                color = mix(self.color, self.end, 1 - y / (height - 1))
                pygame.gfxdraw.hline(surf, 0, width, y, color)


class MultiGradient(Gradient):
    def __init__(self, *colors, positions=None, horizontal=True):
        """
        Paint a surface with a multicolored gradient (with two or more points).

        Exemple for an equaly spaced blue-yellow-orange-red gradient:
            >>> from graphalama.constants import BLUE, YELLOW, ORANGE, RED
            >>> MultiGradient(BLUE, YELLOW, ORANGE, RED)

        You can also choose where the color points are. Here the orange-red part
        will take the left half of the gradient whereas the blue-yellow and yellow-orange
        would take only a fourth. The positions are between 0 and 1
            >>> MultiGradient(BLUE, YELLOW, ORANGE, RED, positions=(0, 1/4, 1/2, 1))

        If horizontal is True, then the gradient is drawn top to bottom and not left to right.
        """

        assert len(colors) >= 2
        assert positions is None or len(positions) == len(colors), \
            "If you define position, give them for each color"

        super().__init__(colors[0], colors[1], horizontal)

        self.colors = colors

        if positions:
            self.positions = tuple(positions)
        else:
            # -1 because n points define n-1 ranges
            spacing = 1 / (len(colors) - 1)
            self.positions = tuple(spacing * i for i in range(len(self.colors)))

    @property
    def has_transparency(self):
        if self.transparency:
            return True

        for r, g, b, *a in self.colors:
            if a and a[0] < 255:
                return True

        return False

    def __repr__(self):
        # Should we add the positions too ? How ?
        return "MultiGradient({})".format(" -> ".join(map(str, self.colors)))

    def _paint(self, surf: pygame.Surface):
        width, height = surf.get_size()

        # The idea is that we break the multi color gradient into 2-colors gradients
        # and then use the Gradient.paint method to paint them

        if self.horizontal:
            # beggining if the first color isn't at x=0
            surf.fill(self.colors[0], (0, 0, round(self.positions[0] * width), height))

            for (start_pos, end_pos, start_color, end_color) in zip(self.positions[:-1],
                                                                    self.positions[1:],
                                                                    self.colors[:-1],
                                                                    self.colors[1:]):
                start_x = round(start_pos * width)
                end_x = round(end_pos * width)

                self.color = start_color
                self.end = end_color

                super(MultiGradient, self)._paint(surf.subsurface((start_x, 0, end_x - start_x, height)))

            end_pos = round(self.positions[-1] * width)
            surf.fill(self.colors[-1], (end_pos, 0, width - end_pos, height))
        else:

            # beggining if the first color isn't at x=0
            surf.fill(self.colors[0], (0, 0, width, round(self.positions[0] * height)))

            for (start_pos, end_pos, start_color, end_color) in zip(self.positions[:-1],
                                                                    self.positions[1:],
                                                                    self.colors[:-1],
                                                                    self.colors[1:]):
                start_y = round(start_pos * height)
                end_y = round(end_pos * height)

                self.color = start_color
                self.end = end_color

                super(MultiGradient, self)._paint(surf.subsurface((0, start_y, width, end_y - start_y)))

            end_pos = round(self.positions[-1] * height)
            surf.fill(self.colors[-1], (0, end_pos, width, height - end_pos))
