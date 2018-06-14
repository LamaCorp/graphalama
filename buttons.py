from _dummy_thread import start_new_thread

import pygame

from constants import TOPLEFT, GREY, WHITESMOKE, BLUE, BLACK, RED, TRANSPARENT, CENTER, ALLANCHOR
from core import Widget
from text import SimpleText


class Button(Widget):
    def __init__(self, content, function, pos, shape, color=None, bg_color=None, border_color=None, anchor=None):
        super().__init__(pos, shape, color, bg_color, border_color, anchor)

        if isinstance(content, str):
            size = self.shape.inside_surf().size
            content = SimpleText(content, (size[0]/2, size[1]/2), size, BLACK, anchor=ALLANCHOR)

        self.child = content
        self.function = function

        self.clicked = False

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




