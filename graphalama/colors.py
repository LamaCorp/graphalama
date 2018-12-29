"""
This module provides functions and classes to manipulate colors and grdients.
"""
import pygame.gfxdraw
from pygame.constants import BLEND_RGBA_MIN, BLEND_RGB_MULT

from graphalama.constants import TRANSPARENT, FIT, FILL, STRETCH
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

    def __bool__(self):
        return not (len(self.color) > 3 and self.color[3] == 0)

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
            surf.fill((self.shade_intensity,) * 3, None, BLEND_RGB_MULT)

        if self.grey_scale:
            surf.blit(greyscaled(surf), (0, 0))

        if self.transparency is not None:
            surf.fill((255, 255, 255, self.transparency), None, BLEND_RGBA_MIN)


class Gradient(Color):
    def __init__(self, start: tuple, end: tuple, horizontal=True):
        """
        Linear Gradient from the color `start` and the color `end`.

        The colors are the line in the 3D or 4D cube between the two points.

        :param tuple start: A RGB or RGBA tuple
        :param tuple end: A RGB or RGBA tuple
        :param bool horizontal: The orientation (horizontal or vertical)
        """

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

        Example for an equaly spaced blue-yellow-orange-red gradient:
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


class ImageBrush(Color):
    def __init__(self, file, mode=FIT, background=TRANSPARENT):
        """
        Color a surface with an image.

        :param file: Path to the image
        :param mode: One of the four constants:
          CENTER: Center the image on the surface without changing the size.
          FIT: Fit the image inside the surface, leaving some space on the edges
          FILL: Fill the surface but some parts of the image may not be visible.
          STRETCH: Stretch the image so it exactly fits the rectangle.
        :param tuple background: color of the background if the image doesn't fill the surface
        """

        super().__init__(background)
        self.file = file
        self.image = pygame.image.load(file)  # type: pygame.Surface
        self.mode = mode

    def __repr__(self):
        return "<Brush-{}>".format(self.file)

    def __bool__(self):
        return True

    @property
    def has_transparency(self):
        return True  # I don't know of an easy way to do it

    def _paint(self, surf: pygame.Surface):
        super()._paint(surf)

        surf_rect = surf.get_rect()  # type: pygame.Rect
        img_rect = self.image.get_rect()  # type: pygame.Rect
        image = self.image.copy()

        if self.mode == FIT:
            img_rect = img_rect.fit(surf_rect)
        elif self.mode == FILL:

            sr_fit = surf_rect.fit(img_rect)
            wr = surf_rect.width / sr_fit.width
            hr = surf_rect.height / sr_fit.height

            ratio = max(wr, hr)

            img_rect.width *= ratio
            img_rect.height *= ratio
        elif self.mode == STRETCH:
            img_rect = surf_rect

        img_rect.center = surf_rect.center
        image = pygame.transform.smoothscale(image, img_rect.size)
        surf.blit(image, img_rect.topleft)


class ImageListBrush(ImageBrush):
    def __init__(self, *files, mode=FIT, background=TRANSPARENT):
        """
        Paint a surface with the image from a list. Set index to choose which image

        :param files: List of path to the images. They wont be loaded unless required
        :param mode: See ImageBrush
        :param background: See ImageBrush
        """
        assert len(files), "There should be at least one image."
        super().__init__(files[0], mode, background)

        self._files = files
        self.images = [None] * len(files)
        self._index = 0
        self.index = 0

    @property
    def index(self):
        """
        Set the image to use to paint a surface.

        Don't forget to call an invalidate_* on the widget if you want it to update.
        """

        return self._index

    @index.setter
    def index(self, value):
        self.index = value % len(self._files)

    def _paint(self, surf: pygame.Surface):
        # We load the image if it isn't
        if not self.images[self.index]:
            self.images[self.index] = pygame.image.load(self._files[self.index])

        self.image = self.images[self.index]
        super()._paint(surf)
