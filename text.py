import pygame

from constants import CENTER, DEFAULT, TRANSPARENT
from core import Widget
from font import default_font


class SimpleText(Widget):

    def __init__(self, text, pos, shape, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT, font=DEFAULT, anchor=DEFAULT, text_anchor=DEFAULT):

        self.text_anchor = text_anchor if text_anchor is not None else CENTER
        self.text = text
        self.font = font if font else default_font()

        # Better defaults for Texts
        if bg_color is DEFAULT:
            bg_color = TRANSPARENT
        if border_color is DEFAULT:
            border_color = TRANSPARENT

        super().__init__(pos, shape, color, bg_color, border_color, anchor)

    def draw_content(self):
        if self._content:
            return

        img = pygame.Surface(self.shape.content_rect().size, pygame.SRCALPHA)

        fg = (255, 255, 255, 255)
        temp = self.font.render(self.text, True, fg)
        surf = pygame.Surface(temp.get_size(), pygame.SRCALPHA)
        self.color.paint(surf)
        surf.blit(temp, (0, 0), None, pygame.BLEND_RGBA_MULT)

        # colrectly align things
        img_rect = img.get_rect()
        surf_rect = surf.get_rect()
        atr_name = self.anchor_to_rect_attr(self.text_anchor)

        setattr(surf_rect, atr_name, getattr(img_rect, atr_name))
        img.blit(surf, surf_rect)

        self._content = img




