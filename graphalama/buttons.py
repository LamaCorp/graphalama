from _dummy_thread import start_new_thread

from graphalama.constants import CENTER
from graphalama.shadow import NoShadow
from .constants import ALLANCHOR
from .core import Widget
from .text import SimpleText


class Button(Widget):
    def __init__(self, text, function, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 shadow=None, anchor=None):

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        self.text = text
        self.function = function

        Widget.LAST_PLACED_WIDGET = self

    def __repr__(self):
        return "<Button-{}>".format(self.text)

    @property
    def text(self):
        return NotImplemented

    @text.setter
    def text(self, value):

        assert isinstance(value, str), "Button.text is only for strings"

        if self.shape.auto_size:
            text = SimpleText(value, (0, 0), None, self.color, anchor=CENTER, shadow=NoShadow())
            self.shape.size = self.shape.widget_size_from_content_size(text.size)
            cr = self.shape.content_rect()
            text.pos = cr.width // 2, cr.height // 2
        else:
            size = self.shape.content_rect().size
            text = SimpleText(value, (size[0] / 2, size[1] / 2), size, self.color, anchor=ALLANCHOR)

        text.parent = self

        self.children.clear()
        self.children.append(text)

    def on_mouse_enter(self, event):
        self.invalidate_bg()

    def on_mouse_button_down(self, event):
        self.invalidate_bg()
        self.invalidate_shadow()

    def on_click(self, event):
        start_new_thread(self.function, ())

    def on_mouse_button_up(self, event):
        self.invalidate_bg()
        self.invalidate_shadow()

    def on_mouse_exit(self, event):
        self.invalidate_bg()

    def pre_render_update(self):
        super(Button, self).pre_render_update()

        self.shape.bg_offset = (1, 1) if self.clicked else (0, 0)
        self.bg_color.shade_intensity = 222 if self.clicked else 242 if self.mouse_over else None
