"""
Math functions and object useful in any code.
"""
import pygame


def clamp(value, min=None, max=None):
    """Clamp the value between min and max. Only one boundary can be specified."""
    if min is not None and value < min:
        value = min
    if max is not None and value > max:
        value = max

    return value

def merge_rects(rect1, rect2):
    """Return the smallest rect containning two rects"""
    r = pygame.Rect(rect1)
    t = pygame.Rect(rect2)

    right = max(r.right, t.right)
    bot = max(r.bottom, t.bottom)
    x = min(t.x, r.x)
    y = min(t.y, r.y)

    return pygame.Rect(x, y, right - x, bot - y)
