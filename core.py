"""
In this module are defined all the core concepts of the library.
You shouldn't need to import or use this module unless you are developping new widgets from scratch.
"""
import pygame

from colors import Color
from constants import *
from shapes import Rectangle


class Widget(pygame.rect.RectType):
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

        self.shape = shape  # type: Rectangle
        """Determine the global geometrical shape of the widget, where it's clickable, its shadow"""
        self.shape.widget = self

        super(Widget, self).__init__(pos, shape.size)

        self._child = None  # type: Widget
        self.child = None  # type: Widget
        """Widget contained inside the widget. Not every widget can act as containers."""
        self.parent = None  # type: Widget
        """Do not set the parent of a widget, only set childs"""

        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color

        self._pos = pos
        self._anchor = anchor if anchor is not None else TOPLEFT

        self.pos = pos
        self.anchor = anchor if anchor is not None else TOPLEFT

        self._img = None  # type: pygame.SurfaceType
        self._bg = None  # type: pygame.SurfaceType
        self._content = None  # type: pygame.SurfaceType

        self.visible = True

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, value: "Widget"):
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
        img.blit(self._bg, (0, 0))
        img.blit(self._content, self.shape.inside_surf().topleft)

        self._img = img

    def draw_shadow(self, img):
        so = self.shape.shadow_offset
        if any(so):
            mask = self.shape.get_mask()
            mask.blit(mask, (-so[0], -so[1]), None, pygame.BLEND_RGBA_SUB)
            mask.fill((0, 0, 0, 64), None, pygame.BLEND_RGBA_MULT)
            img.blit(mask, so)

    def draw_background(self):
        """
        Draws the background of the widget if it'snot already.

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
        img.blit(bg, (0,0))

        self._bg = img

    def draw_border(self, img):
        if not self.shape.border:
            return

        surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)

        self.border_color.paint(surf)
        mask = self.shape.create_border_mask()
        surf.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
        img.blit(surf, (0, 0))

    def draw_content(self):
        if self._content:
            return

        self._content = pygame.Surface(self.shape.inside_surf().size, pygame.SRCALPHA)

        if self.child:
            self.child.render(self._content)


    def invalidate(self):
        """Forces the widget to re-draw"""

        if self.parent:
            self.parent.invalidate_content()

        self._img = None
        self._bg = None
        self._content = None

    def invalidate_content(self):
        """Force the widget to redraw its content."""

        if self._img or self._content:
            self._img = None
            self._content = None

            if self.child:
                self.child.invalidate()

    def invalidate_bg(self):
        """Force the widget to redraw the background."""
        self._img = None
        self._bg = None

    # Pos, size, anchor

    def resize(self, new_screen_size, past_screen_size):

        past_inside_size = self.shape.inside_surf().size

        new_x = self._pos[0] * new_screen_size[0] / past_screen_size[0]
        new_y = self._pos[1] * new_screen_size[1] / past_screen_size[1]

        new_w, new_h = self.size
        scaled_w = new_screen_size[0] - (past_screen_size[0] - self.shape.exact_size[0])
        scaled_h = new_screen_size[1] - (past_screen_size[1] - self.shape.exact_size[1])

        if self.anchor & LEFT and self.anchor & RIGHT:
            new_x = self.pos[0]
            new_w = scaled_w
        elif self.anchor & LEFT:
            new_x = self.pos[0]
        elif self.anchor & RIGHT:
            new_x = new_screen_size[0] - (past_screen_size[0] - self.right)

        if self.anchor & TOP and self.anchor & BOTTOM:
            new_y = self.pos[1]
            new_h = scaled_h
        elif self.anchor & TOP:
            new_y = self.pos[1]
        elif self.anchor & BOTTOM:
            new_y = new_screen_size[1] - (past_screen_size[1] - self.bottom)

        self.shape.size = (new_w, new_h)
        self.pos = (new_x, new_y)

        # resizing child
        if self.child:
            self.child.resize(self.shape.inside_surf().size, past_inside_size)

    @property
    def size(self):
        return self.shape.size

    @property
    def pos(self):
        return round(self._pos[0]), round(self._pos[1])

    @pos.setter
    def pos(self, value):
        self._pos = value
        self.anchor = self.anchor  # sync the Rect pos with mine

    @property
    def absolute_topleft(self):
        if self.parent:
            par_tl = self.parent.absolute_topleft
            pitl = self.parent.shape.inside_surf().topleft
            return (par_tl[0] + pitl[0] + self.x,
                    par_tl[1] + pitl[1] + self.y)
        else:
            return self.topleft

    @property
    def absolute_rect(self):
        return pygame.Rect(self.absolute_topleft, self.size)

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, anchor):

        # don't change and modify something at the same time
        pos = self.pos

        if anchor & TOP and anchor & BOTTOM:
            self.centery = pos[1]
        elif anchor & TOP:
            self.y = pos[1]
        elif anchor & BOTTOM:
            self.bottom = pos[1]
        else:
            self.centery = pos[1]

        if anchor & LEFT and anchor & RIGHT:
            self.centerx = pos[0]
        elif anchor & LEFT:
            self.left = pos[0]
        elif anchor & RIGHT:
            self.right = pos[0]
        else:
            self.centerx = pos[0]

        self._anchor = anchor

    @staticmethod
    def anchor_to_rect_attr(anchor):
        d = {
            TOP: "midtop",
            LEFT: "midleft",
            RIGHT: "midright",
            BOTTOM: "midbottom",
            TOP|LEFT: "topleft",
            TOP|RIGHT: "topright",
            BOTTOM|LEFT: "bottomleft",
            BOTTOM|RIGHT: "bottomright",
            TOP|LEFT|RIGHT: "midtop",
            BOTTOM|LEFT|RIGHT: "midbottom",
            LEFT|TOP|BOTTOM: "midleft",
            RIGHT|TOP|BOTTOM: "midright",
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

