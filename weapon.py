import arcade
import math
import utils
from pyglet.math import Vec2

"""
Bullets
"""


class Bullet(arcade.Sprite):
    """Bullet base class."""

    def __init__(self) -> None:
        super().__init__(
            filename="graphics/Bullet.png",
            image_width=6,
            image_height=6,
            scale=1,
        )
        self.aim = Vec2(0, 0)
        self.speed = float(0)
        self.damage = int(0)
        self.life_span = int(20)

    def set_angle(self, rotate_angle: float) -> None:
        """Rotate the bullet sprite when needed."""
        self.angle = rotate_angle


class EnergyBullet(Bullet):
    """Bullet that cost energy."""

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/EnergyBullet.png")


class FireBall(Bullet):
    """FireBall class for enemy red."""

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/FireBall.png")
        self.life_span = int(60)


class ExplosionParticle(Bullet):
    """Particle class for explosion."""

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/Particle.png")
        self.height = 4
        self.width = 4


"""
Objects
"""


class Object(arcade.Sprite):
    """Base object class that can be placed by the player."""

    def __init__(self) -> None:
        super().__init__(
            image_width=30,
            image_height=30,
            scale=1,
        )
        self.health = 100
        self.object_type = 0  # Specify the object type
        self.grid_idx = (0, 0)


class PlacedWallObject(Object):
    """Wall that can be placed by the player."""

    def __init__(self, health_max: int = 200) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/PlacedWall0.png")
        self.object_type = 0  # Wall object
        self.textures = [
            arcade.load_texture("graphics/PlacedWall1.png"),
            arcade.load_texture("graphics/PlacedWall2.png")
        ]
        self.health_max = health_max
        self.health = health_max

    def update(self) -> None:
        if self.health <= self.health_max * 0.8 and self.health > self.health_max * 0.4:
            self.texture = self.textures[0]
        elif self.health <= self.health_max * 0.4:
            self.texture = self.textures[1]
        super().update()


class BarrelObject(Object):
    """Barrel object class (placed by the player). """

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/Barrel.png")
        self.health = 0
        self.object_type = 1  # Barrel object


"""
Weapons
"""


class Weapon(arcade.Sprite):
    """Weapon base class."""

    def __init__(
        self, weapon_name: str = "graphics/Pistol.png", x: float = 0, y: float = 0
    ) -> None:
        self.is_gun = True
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.is_right = True
        self.damage = 30
        self.cd_max = int(20)  # 1/3 s
        self.bullet_speed = 25
        self.cost = 0
        self.texture_list = [
            arcade.load_texture(weapon_name),
            arcade.load_texture(weapon_name, flipped_horizontally=True),
        ]
        super().__init__(
            filename=weapon_name,
            center_x=self.pos.x,
            center_y=self.pos.y,
            image_width=20,
            image_height=10,
        )
        self.sound = arcade.Sound("audio/wpn_fire_usp45.wav")
        self.bullet = Bullet

    def update(self) -> None:
        self.center_x = self.pos.x
        self.center_y = self.pos.y
        if self.is_right:
            self.texture = self.texture_list[0]
        else:
            self.texture = self.texture_list[1]

    def aim(self, aim_pos: Vec2) -> None:
        """Adjust the sprite angle to the aiming position."""

        self.aim_pos = aim_pos
        if aim_pos.x >= 0:
            self.is_right = True
            rotate_angle = math.degrees(
                math.asin(utils.Utils.get_sin(aim_pos)))
        else:
            self.is_right = False
            rotate_angle = - \
                math.degrees(math.asin(utils.Utils.get_sin(aim_pos)))

        self.angle = rotate_angle

    def get_bullet(self) -> arcade.SpriteList:
        """Get the bullet list shot by the weapon."""
        bullets = arcade.SpriteList()
        bullet = self.bullet()
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.speed = self.bullet_speed
        bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
        bullet.damage = self.damage
        bullets.append(bullet)
        return bullets

    def play_sound(self, effect_volume: int) -> None:
        self.sound.play(volume=effect_volume/20)


class Shotgun(Weapon):
    """Shotgun class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__("graphics/Shotgun.png", x, y)
        self.cd_max = int(30)  # 1/2 s
        self.cost = 8
        self.damage = 40
        self.bullet = EnergyBullet
        self.sound = arcade.Sound("audio/wpn_fire_m1014.wav")

    def get_bullet(self) -> arcade.SpriteList:
        bullets = arcade.SpriteList()
        for angle in [-0.05, 0, 0.05]:
            bullet = self.bullet()
            bullet.life_span = 10
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.speed = self.bullet_speed
            bullet.aim = self.aim_pos.rotate(angle)
            bullet.aim = bullet.aim.normalize().scale(bullet.speed)
            bullet.damage = self.damage
            bullets.append(bullet)
        return bullets


class Uzi(Weapon):
    """Uzi class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__("graphics/Uzi.png", x, y)
        self.cd_max = int(10)  # 1/6 s
        self.cost = 2
        self.damage = 30
        self.bullet = EnergyBullet
        self.sound = arcade.Sound("audio/wpn_fire_p90.wav")

    def get_bullet(self) -> arcade.SpriteList:
        bullets = arcade.SpriteList()
        bullet = self.bullet()
        bullet.life_span = 25
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.speed = self.bullet_speed
        bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
        bullet.damage = self.damage
        bullets.append(bullet)
        return bullets


class Rocket(Weapon):

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__("graphics/Rocket.png", x, y)


class PlacedWall(Weapon):

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__()
        self.is_gun = False
        self.cd_max = int(10)  # 1/6 s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.cost = 5
        self.is_right = True
        self.texture_list = [
            arcade.load_texture("graphics/PlacedWall0.png"),
        ]
        self.sound = arcade.Sound("audio/wall_placed.wav")
        self.health_max = 200

    def update(self) -> None:
        self.center_x = self.pos.x
        self.center_y = self.pos.y

    def draw(self) -> None:
        pass

    def get_object(self) -> arcade.Sprite:
        placed_wall = PlacedWallObject(self.health_max)
        return placed_wall


class Barrel(Weapon):
    """Barrel class (as a weapon)."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__()
        self.is_gun = False
        self.damage = 30
        self.cd_max = int(10)  # 1/6 s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.cost = 20
        self.is_right = True
        self.texture_list = [
            arcade.load_texture("graphics/Barrel.png"),
        ]
        self.sound = arcade.Sound("audio/physics_place_object.wav")

    def update(self) -> None:
        self.center_x = self.pos.x
        self.center_y = self.pos.y

    def draw(self) -> None:
        pass

    def get_object(self) -> arcade.Sprite:
        barrel = BarrelObject()
        return barrel
