
from pyglet.math import Vec2
import arcade.gui
import pickle


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
    DARK_GREEN = (65, 100, 74)
    BRIGHT_GREEN = (114, 176, 29)
    YELLOW = (255, 215, 0)
    # For multiplier only
    MUL_GREEN = [76, 187, 23, 255]
    MUL_YELLOW = [255, 215, 0, 255]
    MUL_ORANGE = [255, 79, 0, 255]
    MUL_RED = [255, 36, 0, 255]


class Utils:
    """Utility functions."""

    BULLET_FORCE = 1000
    ENEMY_FORCE = 4000
    GET_DAMAGE_LEN = 8
    WALL_SIZE = 30
    HALF_WALL_SIZE = 15

    # Minimum CD for guns,
    # might change later for different weapons
    CD_MIN = 4

    @staticmethod
    def get_sin(v: Vec2) -> float:
        """Get sine value of a given vector."""
        d = v.distance(Vec2(0, 0))
        d = 0.001 if d == 0 else d
        return v.y / d

    @staticmethod
    def round_to_multiple(number: int, multiple: int) -> int:
        """Round n to the nearest multiple of m."""
        quotient = round(number / multiple)
        return quotient * multiple

    @staticmethod
    def clear_ui_manager(manager: arcade.gui.UIManager):
        for _ in range(0, len(manager.children[0])):
            manager.clear()
        manager.clear()

    @staticmethod
    def save_settings(window: arcade.Window):
        with open("data/settings.bin", "wb") as setting_file:
            settings = Setting(window.effect_volume,
                               window.music_volume,
                               window.res_index,
                               window.fullscreen)
            pickle.dump(settings, setting_file)


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

    BUTTON_CN = {
        "font_name": ("Dotted Songti Square"),
        "font_size": 16,
        "font_color": Color.WHITE,
        "border_width": 2,
        "border_color": Color.BLACK,
        "bg_color": Color.DARK_GRAY,

        # used if button is pressed
        "bg_color_pressed": Color.LIGHT_GRAY,
        "border_color_pressed": Color.WHITE,  # also used when hovered
        "font_color_pressed": Color.BLACK,
    }


class Setting:
    """Game settings."""

    def __init__(self, e_volume: int, m_volume: int, r_idx: int, fullscreen: bool) -> None:
        self.effect_volume = e_volume
        self.music_volume = m_volume
        self.res_index = r_idx
        self.fullscreen = fullscreen


class Language:
    """Language settings."""

    class EN:
        # Basic
        TITLE = "Box Head 2D: Survivor"
        START = "Start"
        OPTION = "Option"
        QUIT = "Quit"
        BACK = "Back"
        NEXT = "Next"
        START_MENU = "Start Menu"
        CONTINUE = "Continue"
        EFFECT_VOLUME = "Effect Volume"
        MUSIC_VOLUME = "Music Volume"
        LANG = "Language"
        CUR_LANG = "English"
        FULLSCREEN = "Fullscreen"
        RESOLUTION = "Resolution"
        SWITCH = "Switch"

        # Shop
        REFRESH = "Refresh"
        BUY = "Buy"
        BUY_SUCCESS = "Purchase succeeded"
        BUY_FAIL = "Purchase failed"
        REFRESH_FAIL = "Refresh failed"
        PLAYER_STATUS = "Player status"
        HEALTH = "- Health: "
        ENERGY = "- Energy: "
        KILL_RECOVER = "- Recover after kill: "
        LUCK = "- Luck: "
        EXPLOSION_DAMAGE = "- Explosion damage: "
        PISTOL = "Pistol:"
        UZI = "Uzi"
        SHOTGUN = "Shotgun"
        ROCKET = "Rocket"
        WALL = "Wall"
        BARREL = "Barrel"
        MINE = "Mine"
        DAMAGE = "- Damage: "
        CD = "- CD: "
        ATTACK_RANGE = "- Attack range: "
        ENERGY_COST = "- Energy cost: "
        BULLET_NUMBER = "- Bullet numbers: "

        # Item
        GET_UZI = "Get Uzi"
        GET_SHOTGUN = "Get Shotgun"
        GET_ROCKET = "Get Rocket"
        GET_WALL = "Get Wall"
        GET_BARREL = "Get Barrel"
        GET_MINE = "Get Mine"
        SELL_HEALTH = "Sell health: "
        SELL_ENERGY = "Sell energy: "
        ADD_SPEED = "Add speed: "
        SELL_SPEED = "Sell speed: "
        ADD_LUCK = "Increase luck: "
        SELL_LUCK = "Sell luck: "
        ADD_HEALTH_RECOVER = "Add health recover after kill: "
        ADD_EXPLOSION_DAMAGE = "Add explosion damage: "
        PISTOL_DAMAGE = "Increase Pistol damage: "
        PISTOL_CD = "Reduce Pistol CD: "
        PISTOL_RANGE = "Increase Pistol attack range: "
        UZI_DAMAGE = "Increase Uzi damage: "
        UZI_CD = "Reduce Uzi CD: "
        UZI_RANGE = "Increase Uzi attack range: "
        UZI_COST = "Reduce Uzi energy cost: "
        SELL_UZI = "Sell Uzi"
        SHOTGUN_DAMAGE = "Increase Shotgun damage: "
        SHOTGUN_CD = "Reduce Shotgun CD: "
        SHOTGUN_RANGE = "Increase Shotgun attack range: "
        SHOTGUN_COST = "Reduce Shotgun energy cost: "
        SELL_SHOTGUN = "Sell Shotgun"
        SHOTGUN_BULLET = "Increase Shotgun bullets: "
        ROCKET_CD = "Reduce Rocket CD: "
        ROCKET_RANGE = "Increase Rocket attack range: "
        ROCKET_COST = "Reduce Rocket energy cost: "
        SELL_ROCKET = "Sell Rocket"
        WALL_COST = "Reduce Wall energy cost: "
        WALL_HEALTH = "Increase Wall durability: "
        SELL_WALL = "Sell Wall"
        BARREL_COST = "Reduce Barrel energy cost: "
        SELL_BARREL = "Sell Barrel"
        MINE_COST = "Reduce Mine energy cost: "
        SELL_MINE = "Sell Mine"

    class CN:
        START = "开始"
