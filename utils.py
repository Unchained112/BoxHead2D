
from pyglet.math import Vec2


class Color:
    """Color palette."""

    GROUND_WHITE = (240, 237, 212)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DARK_RED = (183, 4, 4)
    LIGHT_GRAY = (207, 210, 207)
    DARK_GRAY = (67, 66, 66)
    LIGHT_BLACK = (34, 34, 34)
    RED_TRANSPARENT = (160, 100, 100, 120)
    HEALTH_RED = (205, 24, 24)
    ENERGY_BLUE = (77, 166, 255)


class Utils:
    """Utility functions."""

    @staticmethod
    def get_sin(v: Vec2) -> float:
        """Get sine value of a given vector."""
        return v.y / v.distance(Vec2(0, 0))
