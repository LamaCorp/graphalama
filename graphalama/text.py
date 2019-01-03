import pygame

from .constants import CENTER, DEFAULT, TRANSPARENT
from .core import Widget
from .font import default_font
from .shadow import NoShadow


class SimpleText(Widget):

    def __init__(self, text, pos=None, shape=None, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT, font=DEFAULT,
                 shadow=None, anchor=DEFAULT, text_anchor=DEFAULT):

        self.text_anchor = text_anchor if text_anchor is not None else CENTER
        self._text = text
        self.font = font if font else default_font()

        # Better defaults for Texts
        if bg_color is DEFAULT:
            bg_color = TRANSPARENT
        if border_color is DEFAULT:
            border_color = TRANSPARENT
        if shadow is DEFAULT:
            shadow = NoShadow()

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

    def __repr__(self):
        return "<SimpleText-{}>".format(self.text)

    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self,value):
        self._text = value
        if self.shape.auto_size:
            # otherwise the size would stay the same even if the text is smaller/bigger
            self.shape.size = self.prefered_size
            # We need to invalidate everything since the size changed => the shadow and bg too
            self.invalidate()
        else:
            # Only the content has changed, not the shadow/bg
            self.invalidate_content()

    @property
    def prefered_size(self):
        return self.shape.widget_size_from_content_size(self.font.size(self.text))

    def draw_content(self, content_surf):

        fg = (255, 255, 255, 255)
        temp = self.font.render(self.text, True, fg)
        surf = pygame.Surface(temp.get_size(), pygame.SRCALPHA)
        self.color.paint(surf)
        surf.blit(temp, (0, 0), None, pygame.BLEND_RGBA_MULT)

        # colrectly align things
        img_rect = content_surf.get_rect()
        surf_rect = surf.get_rect()
        atr_name = self.anchor_to_rect_attr(self.text_anchor)

        setattr(surf_rect, atr_name, getattr(img_rect, atr_name))
        content_surf.blit(surf, surf_rect)

    @property
    def has_content(self):
        return self.text != ""
