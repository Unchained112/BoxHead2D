
from pyglet.math import Vec2
import arcade.gui


class Color:
    """Color palette."""

    GROUND_WHITE = (240, 237, 212)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    ALMOST_WHITE = (240, 240, 240)
    DARK_RED = (183, 4, 4)
    LIGHT_GRAY = (207, 210, 207)
    DARK_GRAY = (67, 66, 66)
    LIGHT_BLACK = (34, 34, 34)
    RED_TRANSPARENT = (160, 100, 100, 120)
    HEALTH_RED = (205, 24, 24)
    ENERGY_BLUE = (77, 166, 255)


class Utils:
    """Utility functions."""

    BULLET_FORCE = 1000
    ENEMY_FORCE = 4000
    GET_DAMAGE_LEN = 8
    WALL_SIZE = 30
    HALF_WALL_SIZE = 15

    @staticmethod
    def get_sin(v: Vec2) -> float:
        """Get sine value of a given vector."""
        return v.y / v.distance(Vec2(0, 0))

    @staticmethod
    def round_to_multiple(number: int, multiple: int) -> int:
        """Round n to the nearest multiple of m."""
        quotient = round(number / multiple)
        return quotient * multiple

    @staticmethod
    def clear_ui_manager(manager: arcade.gui.UIManager):
        for _ in range(0, len(manager.children[0])):
            manager.clear()


class Style:
    """Design styles."""

    BUTTON_DEFAULT = {
        "font_name": ("FFF Forward"),
        "font_size": 10,
        "font_color": Color.WHITE,
        "border_width": 2,
        "border_color": Color.BLACK,
        "bg_color": Color.DARK_GRAY,

        # used if button is pressed
        "bg_color_pressed": Color.LIGHT_GRAY,
        "border_color_pressed": Color.WHITE,  # also used when hovered
        "font_color_pressed": Color.BLACK,
    }
