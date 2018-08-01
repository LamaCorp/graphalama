"""
In this module are defined all the core concepts of the library.
You shouldn't need to import or use this module unless you are developping new widgets from scratch.
"""
from typing import List

import pygame
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, BLEND_RGBA_MIN

from graphalama.anim import Anim
from graphalama.colors import to_color
from graphalama.maths import Pos
from .colors import Color
from .constants import *
from .maths import clamp
from .shadow import Shadow
from .shapes import Rectangle


class Widget:
    LAST_PLACED_WIDGET = None

    def __init__(self, pos=DEFAULT, shape=DEFAULT, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT,
                 shadow=DEFAULT,
                 anchor=DEFAULT):
        """
        The base of any widget.

        :param pos:
        :param shape: A subclass of Rectangle, this determines the size and shape of the background
        :param bg_color: A tuple of RGB or RGBA value or an object with a paint(img: Surface) method
        :param anchor: The sides where the widget will be anchored: BOTTOM|RIGHT
        """

        self._shadow_img = None  # type: pygame.SurfaceType
        self._img = None  # type: pygame.SurfaceType
        self._bg = None  # type: pygame.SurfaceType
        self._content = None  # type: pygame.SurfaceType

        self._child = None  # type: Widget
        self.child = None  # type: Widget
        self.parent = None  # type: Widget
        """Do not set the parent of a widget, only set childs"""

        self.shadow = shadow if shadow is not DEFAULT else Shadow()  # type: Shadow
        self.shape = shape  # type: Rectangle

        if self.shape.auto_size:
            self.shape.size = self.get_auto_size()

        if pos is DEFAULT:
            if Widget.LAST_PLACED_WIDGET:
                y = Widget.LAST_PLACED_WIDGET.y + Widget.LAST_PLACED_WIDGET.shape.height + 8
            else:
                y = 5
            self.pos = (pygame.display.get_surface().get_width() // 2, y)
            self.anchor = TOP  # there is no reason for someone to set the anchor without the pos, so we do it the best we can
        else:
            self.pos = pos
            self.anchor = anchor if anchor is not None else TOPLEFT

        self.visible = True

        self.color = color if color else BLACK  # type: Color
        self.bg_color = bg_color if bg_color else LLAMA  # type: Color
        self.border_color = border_color if border_color else GREY  # type: Color
        self.transparency = None

        # input stuff
        self.mouse_over = False
        self.clicked = False
        self.focus = False

        self.animations = []  # type: List[Anim]

        Widget.LAST_PLACED_WIDGET = self

    def __repr__(self):
        return "<Widget at {}>".format(self.pos)

    # Parts of the widget

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

        self.invalidate()

    @property
    def shadow(self):
        """The shadow of the widget."""
        return self._shadow  # type: Shadow

    @shadow.setter
    def shadow(self, value):
        self._shadow = value
        self.invalidate_bg()

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        if isinstance(value, Rectangle):
            self._shape = value
        else:
            self._shape = Rectangle(value)

        self._shape.widget = self
        self.invalidate()

    # Propeties

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = to_color(value)
        self.invalidate_content()

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = to_color(value)
        self.invalidate_bg()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, value):
        self._border_color = to_color(value)
        self.invalidate_bg()

    @property
    def transparency(self):
        return self._transparency

    @transparency.setter
    def transparency(self, value):
        assert value is None or 0 <= value <= 255
        self._transparency = value
        self.invalidate()

    @property
    def has_transparency(self):
        return self.color.has_transparency or \
               self.bg_color.has_transparency or \
               self.border_color.has_transparency or \
               self.transparency is not None and self.transparency < 255

    # Inputs / update

    def animate(self, animation):
        self.animations.append(animation)
        animation.start()

    def update(self, event):
        if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):

            rel_pos = event.pos - self.absolute_topleft
            inside = self.shape.is_inside(rel_pos)

            if event.type == MOUSEMOTION:
                if inside and not self.mouse_over:  # Enter
                    self.mouse_over = True
                    self.on_mouse_enter(event)
                    self.on_mouse_move(event)
                elif inside:  # Moving inside
                    self.on_mouse_move(event)
                elif not inside and self.mouse_over:  # Exit
                    self.mouse_over = False
                    self.clicked = False
                    self.on_mouse_exit(event)

            elif event.type == MOUSEBUTTONDOWN:
                if inside:
                    self.clicked = True
                    self.on_mouse_button_down(event)
                else:
                    self.clicked = False
                    self.focus = False

            elif event.type == MOUSEBUTTONUP:
                if inside and self.clicked:
                    self.focus = True
                    self.on_click(event)
                    self.on_mouse_button_up(event)
                elif inside:
                    self.on_mouse_button_up(event)
                self.clicked = False

        elif self.focus and event.type in (KEYDOWN, KEYUP):
            if event.type == KEYDOWN:
                self.on_key_press(event)
            else:
                self.on_key_release(event)

    def on_click(self, event):
        """Called after the user clicked and released a mouse button over the widget."""

    def on_mouse_enter(self, event):
        """Called the mouse enters the widget."""

    def on_mouse_exit(self, event):
        """Called the mouse exits the widget."""

    def on_mouse_move(self, event):
        """Called the mouse moves inside the widget."""

    def on_mouse_button_down(self, event):
        """Called user press a button of the mouse over the widget."""

    def on_mouse_button_up(self, event):
        """Called user releases a button of the mouse over the widget."""

    def on_key_press(self, event):
        """Called when a key is pressed and the widget has focus."""

    def on_key_release(self, event):
        """Called when a key is released and the widget has focus."""

    # Drawing methods

    @property
    def background_image(self):
        if not self._bg:
            self.draw_background()

        return self._bg  # type: pygame.SurfaceType

    @property
    def content_image(self):
        if not self._content:
            self.draw_content()

        return self._content

    @property
    def shadow_image(self):
        if not self._shadow_img:
            self.draw_shadow()

        return self._shadow_img

    @property
    def widget_image(self):
        if not self._img:
            self.draw()

        return self._img

    def render(self, screen):
        self.pre_draw_update()

        if self.visible:
            screen.blit(self.widget_image, self.blit_pos)

    def pre_draw_update(self):
        """
        Update drawing parameters before drawing.
        """

        for anim in self.animations:
            if not anim.running:
                self.animations.remove(anim)
            else:
                anim.run(self)

    def draw(self):
        """Draw the whole widget on its .widget_image"""

        # create the surface
        img = pygame.Surface(self.blit_size, flags=pygame.SRCALPHA)
        if self.shadow:
            img.blit(self.shadow_image, (0, 0))
        img.blit(self.background_image, self.shape.bg_offset + self.shadow.bg_offset)
        img.blit(self.content_image, self.shape.content_rect() + self.shadow.bg_offset)

        if self.transparency is not None:
            img.fill((255, 255, 255, self.transparency), None, BLEND_RGBA_MIN)

        # noinspection PyArgumentList
        img.convert_alpha()

        self._img = img

    def draw_shadow(self):
        if self.shadow:
            self._shadow_img = self.shadow.create_from(self)

    def draw_background(self):
        """
        Draws the background of the widget if isn't already.

        To redraw it, use .invalidate_bg() first.
        """

        # And create the background
        bg = pygame.Surface(self.shape.size, pygame.SRCALPHA)
        self.bg_color.paint(bg)

        # And shape it correctly
        shape = self.shape.get_mask()
        bg.blit(shape, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Then we draw the border
        self.draw_border(bg)

        # noinspection PyArgumentList
        bg.convert_alpha()

        self._bg = bg

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

        if not (self._img or self._shadow_img or self._bg or self._content):
            return

        if _propagation & UP and self.parent:
            self.parent.invalidate_content(UP)
        if _propagation & DOWN and self.child:
            self.child.invalidate(DOWN)

        self._img = None
        self._shadow_img = None
        self._bg = None
        self._content = None

        if self.shape.auto_size:
            self.shape.size = self.get_auto_size()

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

        if self.shape.auto_size:
            self.shape.size = self.get_auto_size()

    def invalidate_bg(self):
        """Force the widget to redraw the background."""

        # The background doesn't change the contents, we don't need to propagate down
        if self.parent:
            # but the contents of the container must be updated
            self.parent.invalidate_content(UP)

        self._img = None
        self._bg = None
        self._shadow_img = None

    # Pos, size, anchor

    @property
    def pos(self):
        """Position of the widget relative to the parent of the window if the widget has no parent."""
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
            return Pos(par_tl[0] + pitl[0] + self.x,
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
        return Pos(self.x, self.y)

    @property
    def blit_pos(self):
        return Pos(self.x - self.shadow.offset.left,
                   self.y - self.shadow.offset.top)

    @property
    def blit_size(self):
        return (self.shape.width + self.shadow.extra_size[0],
                self.shape.height + self.shadow.extra_size[1])

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

    def get_auto_size(self):
        """Get the right size for the widget to contain its contents."""

        if self.child:
            return self.shape.widget_size_from_content_size(self.child.size)
        else:
            return 50, 35


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
