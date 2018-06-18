from _dummy_thread import start_new_thread

import pygame

from constants import BLACK, ALLANCHOR
from core import Widget
from text import SimpleText


class Button(Widget):
    def __init__(self, content, function, pos, shape, color=None, bg_color=None, border_color=None, anchor=None):
        super().__init__(pos, shape, color, bg_color, border_color, anchor)

        if isinstance(content, str):
            size = self.shape.content_rect().size
            content = SimpleText(content, (size[0]/2, size[1]/2), size, BLACK, anchor=ALLANCHOR)

        self.child = content
        self.function = function

        self._clicked = False
        self._hovered = False
        self.clicked = False
        self.hovered = False

    @property
    def clicked(self):
        return self._clicked

    @clicked.setter
    def clicked(self, value):
        if self._clicked != value:
            self._clicked = value
            self.invalidate_bg()

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        if self._hovered != value:
            self._hovered = value
            self.invalidate_bg()

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and self.absolute_rect.collidepoint(*event.pos):
                self.clicked = True
                return True
            else:
                self.clicked = False

        elif event.type == pygame.MOUSEBUTTONUP:

            if self.clicked and event.button == 1 and self.absolute_rect.collidepoint(*event.pos):
                start_new_thread(self.function, ())
                self.clicked = False
                return True
            self.clicked = False

        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.absolute_rect.collidepoint(*event.pos)
            return False  # allow other to handle the motion if user is sliding a bar etc.
        return False

    def draw(self):
        super().draw()

    def draw_shadow(self, img):
        super().draw_shadow(img)

    def draw_background(self):
        if self._bg:
            return

        super().draw_background()

        if self.clicked:
            shade = (204,) * 3
        elif self.hovered:
            shade = (242,) * 3
        else:
            return

        shade_img = pygame.Surface(self.size)
        shade_img.fill(shade)
        self._bg.blit(shade_img, (0, 0), None, pygame.BLEND_RGBA_MULT)

    def draw_border(self, img):
        super().draw_border(img)

    def draw_content(self):
        super().draw_content()
