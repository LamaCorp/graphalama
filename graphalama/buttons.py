from _dummy_thread import start_new_thread

from .constants import BLACK, ALLANCHOR
from .core import Widget
from .text import SimpleText


class Button(Widget):
    def __init__(self, content, function, pos, shape, color=None, bg_color=None, border_color=None, shadow=None,
                 anchor=None):
        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        if isinstance(content, str):
            size = self.shape.content_rect().size
            content = SimpleText(content, (size[0]/2, size[1]/2), size, BLACK, anchor=ALLANCHOR)

        self.child = content
        self.function = function

    def on_mouse_enter(self, event):
        self.invalidate_bg()

    def on_mouse_button_down(self, event):
        self.invalidate_bg()

    def on_click(self, event):
        start_new_thread(self.function, ())

    def on_mouse_button_up(self, event):
        self.invalidate_bg()

    def on_mouse_exit(self, event):
        self.invalidate_bg()

    def pre_draw_update(self):
        super(Button, self).pre_draw_update()

        self.shape.bg_offset = (1, 1) if self.clicked else (0, 0)
        self.bg_color.shade_intensity = 222 if self.clicked else 242 if self.mouse_over else None
