"""
In this module are defined all the core concepts of the library.
You shouldn't need to import or use this module unless you are developping new widgets from scratch.
"""
import pygame

from colors import Color
from constants import *
from draw import blur
from maths import clamp
from shapes import Rectangle

try:
    PIL = True
    from PIL import Image, ImageFilter
except (ImportError, ModuleNotFoundError):
    PIL = None


class Widget:
    def __init__(self, pos, shape, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT, anchor=DEFAULT):
        """
        The base of any widget.

        :param pos:
        :param shape: A subclass of Rectangle, this determines the size and shape of the background
        :param bg_color: A tuple of RGB or RGBA value or an object with a paint(img: Surface) method
        :param anchor: The sides where the widget will be anchored: BOTTOM|RIGHT
        """

        if isinstance(shape, tuple):
            shape = Rectangle(shape)
        if not isinstance(color, Color):
            color = Color(color) if color else Color(BLACK)
        if not isinstance(bg_color, Color):
            bg_color = Color(bg_color) if bg_color else Color(LLAMA)
        if not isinstance(border_color, Color):
            border_color = Color(border_color) if border_color else Color(GREY)

        self._child = None  # type: Widget
        self.child = None  # type: Widget
        self.parent = None  # type: Widget
        """Do not set the parent of a widget, only set childs"""

        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color

        self.pos = pos
        self.anchor = anchor if anchor is not None else TOPLEFT

        self.shape = None  # type: Rectangle
        """
        Determine the global geometrical shape of the widget, where it's clickable, its shadow.
        Don't assign shape, use .set_shape(shape) instead.
        """
        self.set_shape(shape)

        self._img = None  # type: pygame.SurfaceType
        self._bg = None  # type: pygame.SurfaceType
        self._content = None  # type: pygame.SurfaceType

        self.visible = True

    def set_shape(self, shape: Rectangle):
        """Change the shape of the widget."""
        self.shape = shape
        self.shape.widget = self
        self.invalidate()

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, value: "Widget"):
        """Widget contained inside the widget. Not every widget can act as containers."""

        # remove the parent of the last child
        if self.child:
            self.child.parent = None

        self._child = value

        if value:
            self.child.parent = self

    # Inputs

    def __contains__(self, point):
        return self.shape.is_inside(point)

    def update(self, event):
        pass

    # Drawing methods

    def render(self, screen):
        if not self.visible:
            return

        if self._img is None:
            self.draw()

        screen.blit(self._img, self.topleft)

    def draw(self):
        """Draw the whole widget on its ._img"""

        if self._img:
            return

        # we draw background and content to have both ._bg and ._content
        self.draw_background()
        self.draw_content()

        # create the surface
        img = pygame.Surface(self.shape.total_size, flags=pygame.SRCALPHA)
        img.blit(self._bg, self.shape.bg_offset)
        img.blit(self._content, self.shape.content_rect())

        # noinspection PyArgumentList
        img.convert_alpha()

        self._img = img

    def draw_shadow(self, img):
        so = self.shape.shadow_offset
        if any(so):

            if not PIL:  # no pillow, simple shadow
                mask = self.shape.get_mask()
                mask.blit(mask, (-so[0], -so[1]), None, pygame.BLEND_RGBA_SUB)
                mask.fill((0, 0, 0, 42), None, pygame.BLEND_RGBA_MULT)
                img.blit(mask, so)

            else:
                margin = min(self.shape.shadow_offset) // 2
                mask = self.shape.get_mask()
                mask.fill((0, 0, 0, 128), None, pygame.BLEND_RGBA_MULT)
                tmp = pygame.Surface((mask.get_width() + 2 * margin,
                                      mask.get_height() + 2 * margin), pygame.SRCALPHA)
                tmp.blit(mask, (margin, margin))
                tmp = blur(tmp, margin)
                tmp.blit(mask, (0, 0), None, pygame.BLEND_RGBA_SUB)
                img.blit(tmp, (0, 0))

    def draw_background(self):
        """
        Draws the background of the widget if isn't already.

        To redraw it, use .invalidate_bg() first.
        """

        if self._bg:
            return

        img = pygame.Surface(self.shape.total_size, pygame.SRCALPHA)

        # we draw the shadow on the image
        self.draw_shadow(img)

        # And create the background
        bg = pygame.Surface(self.shape.size, pygame.SRCALPHA)
        self.bg_color.paint(bg)

        # And shape it correctly
        shape = self.shape.get_mask()
        bg.blit(shape, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Then we draw the border
        self.draw_border(bg)
        # we blit the bg on the image
        img.blit(bg, (0, 0))

        # noinspection PyArgumentList
        img.convert_alpha()

        self._bg = img

    def draw_border(self, img):
        if not self.shape.border:
            return

        surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)

        self.border_color.paint(surf)
        mask = self.shape.get_border_mask()
        surf.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
        img.blit(surf, (0, 0))

    def draw_content(self):
        if self._content:
            return

        self._content = pygame.Surface(self.shape.content_rect().size, pygame.SRCALPHA)

        if self.child:
            self.child.render(self._content)

        # noinspection PyArgumentList
        self._content.convert_alpha()

    def invalidate(self, _propagation=UP | DOWN):
        """Forces the widget to re-draw"""

        if _propagation & UP and self.parent:
            self.parent.invalidate_content(UP)
        if _propagation & DOWN and self.child:
            self.child.invalidate(DOWN)

        self._img = None
        self._bg = None
        self._content = None

    def invalidate_content(self, _propagation=UP | DOWN):
        """Force the widget to redraw its content."""

        if _propagation & UP and self.parent:
            self.parent.invalidate_content(UP)
        if _propagation & DOWN and self.child:
            self.child.invalidate(DOWN)

        if self._img or self._content:
            self._img = None
            self._content = None

            if self.child:
                self.child.invalidate()

    def invalidate_bg(self):
        """Force the widget to redraw the background."""

        # The background doesn't change the contents, we don't need to propagate down
        if self.parent:
            # but the contents of the container must be updated
            self.parent.invalidate_content(UP)

        self._img = None
        self._bg = None

    # Pos, size, anchor

    @property
    def pos(self):
        return round(self._pos[0]), round(self._pos[1])

    @pos.setter
    def pos(self, value):
        self._pos = value
        if self.parent:
            self.parent.invalidate_content(UP)

    def resize(self, new_screen_size, past_screen_size):

        past_inside_size = self.shape.content_rect().size

        new_x = self._pos[0] * new_screen_size[0] / past_screen_size[0]
        new_y = self._pos[1] * new_screen_size[1] / past_screen_size[1]

        new_w, new_h = self.size
        scaled_w = new_screen_size[0] - (past_screen_size[0] - self.shape.exact_width)
        scaled_h = new_screen_size[1] - (past_screen_size[1] - self.shape.exact_height)

        if self.anchor & LEFT and self.anchor & RIGHT:
            new_x = self.x + clamp(scaled_w, self.shape.min_size[0], self.shape.max_size[0]) // 2
            new_w = scaled_w
        elif self.anchor & LEFT:
            new_x = self.pos[0]
        elif self.anchor & RIGHT:
            new_x = new_screen_size[0] - (past_screen_size[0] - (self.x + self.shape.width))

        if self.anchor & TOP and self.anchor & BOTTOM:
            new_y = self.y + clamp(scaled_h, self.shape.min_size[1], self.shape.max_size[0]) // 2
            new_h = scaled_h
        elif self.anchor & TOP:
            new_y = self.pos[1]
        elif self.anchor & BOTTOM:
            new_y = new_screen_size[1] - (past_screen_size[1] - (self.y + self.shape.height))

        self.shape.size = (new_w, new_h)
        self.pos = (new_x, new_y)

        # resizing child
        if self.child:
            self.child.resize(self.shape.content_rect().size, past_inside_size)

    @property
    def size(self):
        return self.shape.size

    @property
    def absolute_topleft(self):
        if self.parent:
            par_tl = self.parent.absolute_topleft
            pitl = self.parent.shape.content_rect().topleft
            return (par_tl[0] + pitl[0] + self.x,
                    par_tl[1] + pitl[1] + self.y)
        else:
            return self.topleft

    @property
    def absolute_rect(self):
        return pygame.Rect(self.absolute_topleft, self.size)

    @property
    def x(self):
        if self.anchor & LEFT and self.anchor & RIGHT:
            return self.pos[0] - self.shape.width // 2
        elif self.anchor & LEFT:
            return self.pos[0]
        elif self.anchor & RIGHT:
            return self.pos[0] - self.shape.width
        else:
            return self.pos[0] - self.shape.width // 2

    @property
    def y(self):
        if self.anchor & TOP and self.anchor & BOTTOM:
            return self.pos[1] - self.shape.height // 2
        elif self.anchor & TOP:
            return self.pos[1]
        elif self.anchor & BOTTOM:
            return self.pos[1] - self.shape.height
        else:
            return self.pos[1] - self.shape.height // 2

    @property
    def topleft(self):
        return self.x, self.y

    @staticmethod
    def anchor_to_rect_attr(anchor):
        d = {
            TOP: "midtop",
            LEFT: "midleft",
            RIGHT: "midright",
            BOTTOM: "midbottom",
            TOP | LEFT: "topleft",
            TOP | RIGHT: "topright",
            BOTTOM | LEFT: "bottomleft",
            BOTTOM | RIGHT: "bottomright",
            TOP | LEFT | RIGHT: "midtop",
            BOTTOM | LEFT | RIGHT: "midbottom",
            LEFT | TOP | BOTTOM: "midleft",
            RIGHT | TOP | BOTTOM: "midright",
        }

        return d.get(anchor, "center")


class WidgetList(list):

    def render(self, screen):
        for w in self:
            w.render(screen)

    def update(self, event):
        for w in self:
            if w.update(event):
                return True
        return False

    def resize(self, new_screen_size, past_screen_size):
        for w in self:
            w.resize(new_screen_size, past_screen_size)
