
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
    RED_LIGHT_TRANS = (200, 50, 50, 40)
    WHITE_TRANSPARENT = (255, 255, 255, 80)
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

    IS_TESTING = False

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
                               window.fullscreen,
                               window.lang_idx)
            pickle.dump(settings, setting_file)


class Style:
    """Design styles."""

    BUTTON_DEFAULT = {
        "font_name": ("Cubic 11"),
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

    def __init__(self,
                 e_volume: int,
                 m_volume: int,
                 r_idx: int,
                 fullscreen: bool,
                 lang_idx: int) -> None:
        self.effect_volume = e_volume
        self.music_volume = m_volume
        self.res_index = r_idx
        self.fullscreen = fullscreen
        self.lang_idx = lang_idx


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
        PRESS_ANY_KEY = "Press any key to proceed..."
        MISSION_FAILED = "Mission Failed"
        MISSION_SUCCESS = "Mission Success"
        SCORE = "Score: "

        # Shop
        REFRESH = "Refresh"
        BUY = "Buy"
        BUY_SUCCESS = "Purchase succeeded"
        BUY_FAIL = "Purchase failed"
        REFRESH_FAIL = "Refresh failed"
        PLAYER_STATUS = "Player status"
        HEALTH = "- Health: "
        ENERGY = "- Energy: "
        SPEED = "- Speed: "
        KILL_RECOVER = "- Recover after kill: "
        LUCK = "- Luck: "
        EXPLOSION_DAMAGE = "- Explosion damage: "
        PISTOL = "Pistol"
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
        ItemText = {
            "Get Uzi": "Get Uzi",
            "Get Shotgun": "Get Shotgun",
            "Get Rocket": "Get Rocket",
            "Get Wall": "Get Wall",
            "Get Barrel": "Get Barrel",
            "Get Mine": "Get Mine",
            "Sell health: ": "Sell health: ",
            "Sell energy: ": "Sell energy: ",
            "Add speed: ": "Add speed: ",
            "Sell speed: ": "Sell speed: ",
            "Increase luck: ": "Increase luck: ",
            "Sell luck: ": "Sell luck: ",
            "Add health recover after kill: ": "Add health recover after kill: ",
            "Add explosion damage: ": "Add explosion damage: ",
            "Increase Pistol damage: ": "Increase Pistol damage: ",
            "Reduce Pistol CD: ": "Reduce Pistol CD: ",
            "Increase Pistol attack range: ": "Increase Pistol attack range: ",
            "Increase Uzi damage: ": "Increase Uzi damage: ",
            "Reduce Uzi CD: ": "Reduce Uzi CD: ",
            "Increase Uzi attack range: ": "Increase Uzi attack range: ",
            "Reduce Uzi energy cost: ": "Reduce Uzi energy cost: ",
            "Sell Uzi": "Sell Uzi",
            "Increase Shotgun damage: ": "Increase Shotgun damage: ",
            "Reduce Shotgun CD: ": "Reduce Shotgun CD: ",
            "Increase Shotgun attack range: ": "Increase Shotgun attack range: ",
            "Reduce Shotgun energy cost: ": "Reduce Shotgun energy cost: ",
            "Sell Shotgun": "Sell Shotgun",
            "Increase Shotgun bullets: ": "Increase Shotgun bullets: ",
            "Reduce Rocket CD: ": "Reduce Rocket CD: ",
            "Increase Rocket attack range: ": "Increase Rocket attack range: ",
            "Reduce Rocket energy cost: ": "Reduce Rocket energy cost: ",
            "Increase Rocket bullets: ": "Increase Rocket bullets: ",
            "Sell Rocket": "Sell Rocket",
            "Reduce Wall energy cost: ": "Reduce Wall energy cost: ",
            "Increase Wall durability: ": "Increase Wall durability: ",
            "Sell Wall": "Sell Wall",
            "Reduce Barrel energy cost: ": "Reduce Barrel energy cost: ",
            "Sell Barrel": "Sell Barrel",
            "Reduce Mine energy cost: ": "Reduce Mine energy cost: ",
            "Sell Mine": "Sell Mine",
            "Enable Rocket Multi-explosion": "Enable Rocket Multi-explosion",
            "Enable Barrel Multi-explosion": "Enable Barrel Multi-explosion",
            "Enable Mine Multi-explosion": "Enable Mine Multi-explosion",
        }

    class CN:
        # Basic
        TITLE = "僵尸危机幸存者"
        START = "开始"
        OPTION = "设置"
        QUIT = "退出"
        BACK = "返回"
        NEXT = "下一项"
        START_MENU = "开始菜单"
        CONTINUE = "继续"
        EFFECT_VOLUME = "音效音量"
        MUSIC_VOLUME = "音乐音量"
        LANG = "语言"
        CUR_LANG = "中文"
        FULLSCREEN = "全屏"
        RESOLUTION = "分辨率"
        SWITCH = "开关"
        PRESS_ANY_KEY = "按任意键继续..."
        MISSION_FAILED = "任务失败"
        MISSION_SUCCESS = "任务完成"
        SCORE = "最终得分: "

        # Shop
        REFRESH = "刷新"
        BUY = "购买"
        BUY_SUCCESS = "购买成功"
        BUY_FAIL = "购买失败"
        REFRESH_FAIL = "刷新失败"
        PLAYER_STATUS = "角色状态"
        HEALTH = "- 生命: "
        ENERGY = "- 能量: "
        SPEED = "- 速度: "
        KILL_RECOVER = "- 杀敌恢复生命: "
        LUCK = "- 幸运: "
        EXPLOSION_DAMAGE = "- 爆炸伤害: "
        PISTOL = "手枪"
        UZI = "冲锋枪"
        SHOTGUN = "霰弹枪"
        ROCKET = "火箭筒"
        WALL = "墙"
        BARREL = "油桶"
        MINE = "地雷"
        DAMAGE = "- 伤害: "
        CD = "- 冷却: "
        ATTACK_RANGE = "- 攻击范围: "
        ENERGY_COST = "- 能量消耗: "
        BULLET_NUMBER = "- 子弹数: "

        # Item
        ItemText = {
            "Get Uzi": "冲锋枪",
            "Get Shotgun": "霰弹枪",
            "Get Rocket": "火箭筒",
            "Get Wall": "墙",
            "Get Barrel": "油桶",
            "Get Mine": "地雷",
            "Sell health: ": "卖血: ",
            "Sell energy: ": "出售能量: ",
            "Add speed: ": "增加移速: ",
            "Sell speed: ": "出售移速: ",
            "Increase luck: ": "增加幸运: ",
            "Sell luck: ": "出售幸运: ",
            "Add health recover after kill: ": "增加击杀后恢复: ",
            "Add explosion damage: ": "增加爆炸伤害: ",
            "Increase Pistol damage: ": "增加手枪伤害: ",
            "Reduce Pistol CD: ": "减少手枪冷却: ",
            "Increase Pistol attack range: ": "增加手枪射程: ",
            "Increase Uzi damage: ": "增加冲锋枪伤害: ",
            "Reduce Uzi CD: ": "减少冲锋枪冷却: ",
            "Increase Uzi attack range: ": "增加冲锋枪射程: ",
            "Reduce Uzi energy cost: ": "减少冲锋枪能量消耗: ",
            "Sell Uzi": "出售冲锋枪",
            "Increase Shotgun damage: ": "增加霰弹枪伤害: ",
            "Reduce Shotgun CD: ": "减少霰弹枪冷却: ",
            "Increase Shotgun attack range: ": "增加霰弹枪射程: ",
            "Reduce Shotgun energy cost: ": "减少霰弹枪能量消耗: ",
            "Sell Shotgun": "出售霰弹枪",
            "Increase Shotgun bullets: ": "增加霰弹枪子弹数: ",
            "Reduce Rocket CD: ": "减少火箭筒冷却: ",
            "Increase Rocket attack range: ": "增加火箭筒射程: ",
            "Reduce Rocket energy cost: ": "减少火箭筒能量消耗: ",
            "Increase Rocket bullets: ": "增加火箭筒子弹数: ",
            "Sell Rocket": "出售火箭筒",
            "Reduce Wall energy cost: ": "减少墙能量消耗: ",
            "Increase Wall durability: ": "增加墙耐久度: ",
            "Sell Wall": "出售墙",
            "Reduce Barrel energy cost: ": "减少油桶能量消耗: ",
            "Sell Barrel": "出售油桶",
            "Reduce Mine energy cost: ": "减少地雷能量消耗: ",
            "Sell Mine": "出售地雷",
            "Enable Rocket Multi-explosion": "火箭筒连环爆炸",
            "Enable Barrel Multi-explosion": "油桶连环爆炸",
            "Enable Mine Multi-explosion": "地雷连环爆炸",
        }
