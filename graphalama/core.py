"""
In this module are defined all the core concepts of the library.
You shouldn't need to import or use this module unless you are developping new widgets from scratch.
"""
from typing import List, Union

import pygame
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP
from pygame.rect import Rect
from pygame.surface import Surface

from .anim import Anim
from .colors import Color, to_color
from .constants import *
from .draw import make_transparent
from .maths import Pos, clamp
from .shadow import Shadow
from .shapes import Rectangle


class Widget:

    LAST_PLACED_WIDGET = None
    ACCEPT_CLICKS = False
    ACCEPT_KEYBOARD_INPUT = False

    def __init__(self, pos=DEFAULT, shape=DEFAULT, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT,
                 shadow=DEFAULT, anchor=DEFAULT):
        """
        The base of any widget.

        :param pos:
        :param shape: A subclass of Rectangle, this determines the size and shape of the background
        :param bg_color: A tuple of RGB or RGBA value or an object with a paint(img: Surface) method
        :param anchor: The sides where the widget will be anchored: BOTTOM|RIGHT
        """

        self._shadow_img = None  # type: pygame.SurfaceType
        self._bg = None  # type: pygame.SurfaceType
        self._content = None  # type: pygame.SurfaceType

        self.children = WidgetList()  # type: Union[WidgetList[Widget], Widget]

        """You're not supposed to use this unless you're developping a new widget."""
        self.parent = None  # type: Widget
        """Do not set the parent of a widget, only set childs"""

        self._shadow = None
        self.shadow = shadow if shadow is not DEFAULT else Shadow()  # type: Shadow
        self._shape = None  # type: Rectangle
        self.shape = shape  # type: Rectangle

        if self.shape.auto_size:
            self.shape.size = self.prefered_size

        self._pos = None
        if pos is DEFAULT:
            if Widget.LAST_PLACED_WIDGET:
                y = Widget.LAST_PLACED_WIDGET.shadow_rect.bottom + 3
                x = Widget.LAST_PLACED_WIDGET.background_rect.centerx
            else:
                x = pygame.display.get_surface().get_width() // 2
                y = 5
            self.pos = x, y
            # there is no reason for someone to set the anchor without the pos, so we do it the best we can
            self.anchor = TOP
        else:
            self.pos = pos
            self.anchor = anchor if anchor is not None else TOPLEFT

        self.visible = True

        self._color = None  # type: Color
        self.color = color if color else BLACK  # type: Color
        self._bg_color = None  # type: Color
        self.bg_color = bg_color if bg_color else LLAMA  # type: Color
        self._border_color = None  # type: Color
        self.border_color = border_color if border_color else GREY  # type: Color
        self._transparency = None  # type: int
        self.transparency = None  # type: int

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

    def add_child(self, child: "Widget"):
        """Recommended way to add a child to a widget."""
        child.parent = self
        self.children.append(child)
        return child

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
        if value == 255:
            value = None
        self._transparency = value
        for child in self.children: child.transparency = value

        self.invalidate()

    @property
    def has_transparency(self):
        return self.color.has_transparency or \
               self.bg_color.has_transparency or \
               self.border_color.has_transparency or \
               self.transparency is not None and self.transparency < 255

    @property
    def has_content(self):
        return bool(self.children)

    # Inputs / update

    def animate(self, animation):
        self.animations.append(animation)
        animation.start()

    def update(self, event):

        if self.children.update(event):
            return

        event_used = False

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

            elif event.type == MOUSEBUTTONDOWN and self.ACCEPT_CLICKS:
                if inside:
                    self.focus = True
                    self.clicked = True
                    self.on_mouse_button_down(event)
                    event_used = True
                else:
                    self.clicked = False
                    self.focus = False

            elif event.type == MOUSEBUTTONUP and self.ACCEPT_CLICKS:
                if inside and self.clicked:
                    self.focus = True
                    self.on_click(event)
                    self.on_mouse_button_up(event)
                    event_used = True
                elif inside:
                    self.on_mouse_button_up(event)
                self.clicked = False

        elif self.focus and event.type in (KEYDOWN, KEYUP) and self.ACCEPT_KEYBOARD_INPUT:
            if event.type == KEYDOWN:
                self.on_key_press(event)
            else:
                self.on_key_release(event)
            event_used = True

        return event_used

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

    def get_surf_to_update(self):
        ...

    # Drawing methods

    @property  # shadow
    def shadow_image(self):
        if not self._shadow_img:
            self.draw_shadow()

            if self.transparency is not None:
                make_transparent(self._shadow_img, self.transparency)

            # noinspection PyArgumentList
            self._shadow_img.convert_alpha()

        return self._shadow_img

    def draw_shadow(self):
        if self.shadow:
            self._shadow_img = self.shadow.create_from(self)

    def invalidate_shadow(self):
        """Force the shadow to redraw."""

        self._shadow_img = None

    @property  # background
    def background_image(self):
        if not self._bg:
            # create the surface
            self._bg = pygame.Surface(self.shape.size, pygame.SRCALPHA)
            # and fill it
            self.draw_background(self._bg)

            # mostly for fade in and out effects
            if self.transparency is not None:
                make_transparent(self._bg, self.transparency)

            # noinspection PyArgumentList
            self._bg.convert_alpha()

        return self._bg  # type: pygame.SurfaceType

    def draw_background(self, bg_surf):
        """
        Don't call this directly.

        Draws the background of the widget if isn't already.
        To redraw it, use .invalidate_bg() first.
        :param bg_surf: The surface to draw the background on
        """

        # And create the background
        if self.bg_color:
            self.bg_color.paint(bg_surf)

            # And shape it correctly
            shape = self.shape.get_mask()
            bg_surf.blit(shape, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Then we draw the border if we need too
        if self.shape.border and self.border_color:
            surf = pygame.Surface(bg_surf.get_size(), pygame.SRCALPHA)

            self.border_color.paint(surf)
            mask = self.shape.get_border_mask()
            surf.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
            bg_surf.blit(surf, (0, 0))

    def invalidate_bg(self):
        """Force the widget to redraw the background."""

        self._bg = None

    @property  # content
    def content_image(self):
        if not self._content:

            # create the surface
            self._content = pygame.Surface(self.content_rect.size, pygame.SRCALPHA)
            # and fill it
            self.draw_content(self._content)

            # mostly for fade in and out effects
            if self.transparency is not None:
                make_transparent(self._content, self.transparency)

            # noinspection PyArgumentList
            self._content.convert_alpha()

        return self._content

    def draw_content(self, content_surf):
        """
        Don't call this directly.

        But override it to design your widget's content.
        :param content_surf: The surface to draw the content on
        """

        pass

    def invalidate_content(self):
        """Force the widget to redraw its content."""

        self._content = None

    def invalidate(self):
        """Forces the widget to re-draw"""

        self._shadow_img = None
        self._bg = None
        self._content = None

    # Rendering

    def pre_render_update(self):
        """
        Update drawing parameters before rendering to trigger a redrawing if needed.
        """

        for anim in self.animations:
            if not anim.running:
                self.animations.remove(anim)
            else:
                anim.run(self)

    def render(self, screen: Surface, rects: List[pygame.Rect] = ()):
        """
        Draw the widget and it's child into the screen.

        An optional `rects` can be passed tu update only the rects. It is used for optimized rendering,
        where we want to update only the parts of the screen that have changed during the last frame.
        """

        self.pre_render_update()

        # on render we blit the shadow, background, content and every child in this order.
        # I choosed to blit everything everytime as blit operation are somewhat fast
        # and it's a much cleaner code than is each widget was a surface containing their children
        # (were each widget would be blited on their parents

        if self.visible:

            content_surf = None
            if self.children:
                clip = screen.get_rect().clip(self.content_rect)
                content_surf = screen.subsurface(clip)

            if not rects:
                if self.shadow:
                    screen.blit(self.shadow_image, self.shadow_blit_pos)
                if self.bg_color or self.border_color:
                    screen.blit(self.background_image, self.background_pos)  # background and border
                if self.has_content:
                    screen.blit(self.content_image, self.content_pos)  # widget's own content
                if self.children:
                    self.children.render(content_surf)
            else:

                shadow_rect = self.shadow_rect
                collides = shadow_rect.collidelistall(rects)
                intersections = [shadow_rect.clip(rects[i]) for i in collides]

                for child in self.children:
                    if not child.has_transparency and type(child.shape) is Rectangle:

                        # we don't want to blit stuff if it will be overridden by the child who has as no transparency
                        for inter in intersections[:]:
                            if child.background_rect.contains(inter):
                                child.render(content_surf, inter)
                            intersections.remove(inter)

                for inter in intersections:

                    if self.shadow:
                        screen.blit(self.shadow_image, self.shadow_blit_pos, inter)
                    if self.bg_color or self.border_color:
                        screen.blit(self.background_image, self.background_pos, inter)  # background and border
                    if self.has_content:
                        screen.blit(self.content_image, self.content_pos, inter)  # widget's own content
                    if self.children:
                        print(content_surf.get_size())
                        self.children.render(content_surf)

    # Pos, size, anchor

    @property
    def pos(self):
        """Position of the widget relative to the parent of the window if the widget has no parent."""
        return round(self._pos[0]), round(self._pos[1])

    @pos.setter
    def pos(self, value):
        self._pos = value

    def resize(self, new_screen_size, past_screen_size):
        """
        Resize and replace the widget according to its anchor.

        You shouldn't need to call this function directly as `Widget.size.setter` and `Widget.update` do it already.
        Call this when the window / parent widget size changes from `past_screen_size` to `new_screen_size`.
        """

        past_inside_size = self.shape.content_rect().size

        # The is idea is to calculate margins on each side, since that's what an anchor fixes
        # and then deduce the new size
        # But we all know that it is just math that happen to work

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

        if self.shape.auto_size:
            self.shape.size = self.prefered_size

        # resizing children
        if self.children:
            self.children.resize(self.shape.content_rect().size, past_inside_size)

    @property
    def prefered_size(self):
        """Get the size of a rectangular area into which the widget is happy."""
        return Pos(50, 35)

    @property
    def size(self):
        """Get the size of the widget and correctly resize children when setting size."""
        return self.shape.size

    @size.setter
    def size(self, new_size):
        previous_size = self.shape.content_rect().size
        self.shape.size = new_size
        for child in self.children:
            child.resize(self.shape.content_rect().size, previous_size)

    @property
    def absolute_topleft(self):
        """Position of the topleft of the background inside the whole window."""

        if self.parent:
            par_tl = self.parent.absolute_topleft
            pitl = self.parent.shape.content_rect().topleft
            return Pos(par_tl[0] + pitl[0] + self.x,
                       par_tl[1] + pitl[1] + self.y)
        else:
            return self.topleft

    @property
    def absolute_rect(self):
        """Rectangle containing the widget (its background) inside the whole window."""

        return pygame.Rect(self.absolute_topleft, self.size)

    @property
    def x(self):
        """X position relative to its parent (or the left of the window if it has no parent)"""

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
        """Y position relative to its parent (or the top of the window if it has no parent)"""

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
        """Position of the background relative the the parent's topleft (or the window topleft if no parent)."""

        return Pos(self.x, self.y)

    @property
    def shadow_blit_pos(self):
        """Position of the shadow relative the parent's top left corner."""

        return Pos(self.x - self.shadow.offset.left,
                   self.y - self.shadow.offset.top)

    @property
    def shadow_blit_size(self):
        """Size of the shadow"""
        return self.size + self.shadow.extra_size

    @property
    def shadow_rect(self):
        """The shadow's rectangle relative to the topleft corner of the parent."""
        return Rect(self.shadow_blit_pos, self.shadow_blit_size)

    @property
    def background_pos(self):
        """Position of the background relative the parent's top left corner."""
        return self.topleft + self.shape.bg_offset

    @property
    def background_rect(self):
        """Rectangle containing the background, relatively to the widget's parent"""
        return Rect(self.topleft, self.size)

    @property
    def content_pos(self):
        """Position of the content relative the parent's top left corner."""
        return self.topleft + self.shape.content_rect().topleft

    @property
    def content_rect(self):
        """Position of the content rectangle relative the parent's top left corner."""
        return Rect(self.content_pos, self.shape.content_rect().size)

    @staticmethod
    def anchor_to_rect_attr(anchor):
        """Return the name of the point fixed by the given anchor."""

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

    def __bool__(self):
        return len(self) > 0

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
