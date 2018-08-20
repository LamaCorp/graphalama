from _dummy_thread import start_new_thread

from graphalama.colors import ImageBrush, Color
from graphalama.constants import CENTER, DEFAULT, LEFT, TRANSPARENT, WHITE, DATA_PATH
from graphalama.shadow import NoShadow
from graphalama.shapes import Rectangle
from .constants import ALLANCHOR
from .core import Widget
from .text import SimpleText


class Button(Widget):
    ACCEPT_CLICKS = True

    def __init__(self, text, function, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 shadow=None, anchor=None):

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        self.text_widget = None  # type: SimpleText
        self.text = text
        self.function = function

        Widget.LAST_PLACED_WIDGET = self

    def __repr__(self):
        return "<Button-{}>".format(self.text)

    @property
    def text(self):
        return self.text_widget.text

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

        self.children.clear()
        self.text_widget = self.add_child(text)

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
        # case the user leaves the button while clicking, shadow wouldn't follow the offset
        self.invalidate_shadow()

    def pre_render_update(self):
        super(Button, self).pre_render_update()

        self.shape.bg_offset = (1, 1) if self.clicked else (0, 0)
        self.bg_color.shade_intensity = 222 if self.clicked else 242 if self.mouse_over else None


class CheckBox(Widget):
    ACCEPT_CLICKS = True

    def __init__(self, text="", pos=DEFAULT, shape=DEFAULT, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT,
                 shadow=DEFAULT, anchor=DEFAULT):

        if bg_color is DEFAULT:
            bg_color = TRANSPARENT
            shadow = NoShadow()

        box_size = (20, 20)
        self.box_widget = Button("", self.change_checked, (0, 0), Rectangle(box_size, 1, 0, box_size, box_size),
                                 border_color=color, anchor=LEFT)
        self.text_widget = SimpleText(text, (0, 0), color=color, shadow=NoShadow(), anchor=LEFT)

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        self.add_child(self.box_widget)
        self.add_child(self.text_widget)

        self.box_widget.pos = (self.box_widget.shadow.offset[0], self.shape.content_rect().height / 2)
        self.text_widget.pos = (self.box_widget.shadow_rect.width + 3, self.shape.content_rect().height / 2)

        self._checked = False
        self.checked = False

        Widget.LAST_PLACED_WIDGET = self

    def on_click(self, event):
        self.change_checked()

    @property
    def prefered_size(self):
        desired = (self.box_widget.shadow_rect.width + 3 + self.text_widget.shape.width,
                   max(self.box_widget.shadow_rect.height, self.text_widget.shape.height))
        return self.shape.widget_size_from_content_size(desired)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        assert isinstance(value, bool)

        if value != self.checked:
            self._checked = value

        if self.checked:
            self.box_widget.bg_color = ImageBrush(DATA_PATH + "tick.png", CENTER)
        else:
            self.box_widget.bg_color = Color(WHITE)

        self.box_widget.invalidate_bg()

    def change_checked(self):
        self.checked = not self.checked


class ImageButton(Button):
    
    def __init__(self, function, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 shadow=None, anchor=None):
        """A button with an image instead of a text. Set color to an ImageBrush for full control on image position and size."""

        super().__init__("", function, pos, shape, color, bg_color, border_color, shadow, anchor)

    def draw_content(self, content_surf):
        self.color.paint(content_surf)

