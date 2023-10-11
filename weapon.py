import arcade
import math
import utils
from pyglet.math import Vec2

"""
Bullets
"""


class Bullet(arcade.Sprite):
    """Bullet base class."""

    def __init__(self, filename="graphics/weapon/Bullet.png",
                 width=6,
                 height=6,
                 scale=1) -> None:
        super().__init__(
            filename=filename,
            image_width=width,
            image_height=height,
            scale=scale,
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
        self.texture = arcade.load_texture("graphics/weapon/EnergyBullet.png")


class Missile(Bullet):
    """Missile from the Rocket."""

    def __init__(self) -> None:
        super().__init__("graphics/weapon/Missile.png", 15, 15)


class FireBall(Bullet):
    """FireBall class for enemy red."""

    def __init__(self) -> None:
        super().__init__("graphics/weapon/FireBall.png", 20, 20)
        self.life_span = int(60)


class ExplosionParticle(Bullet):
    """Particle class for explosion."""

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/weapon/Particle.png")
        self.height = 4
        self.width = 4


class ExplosionSeed(Bullet):
    """Multi-explosion seed. """


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
        self.texture = arcade.load_texture("graphics/weapon/PlacedWall0.png")
        self.object_type = 0  # Wall object
        self.textures = [
            arcade.load_texture("graphics/weapon/PlacedWall1.png"),
            arcade.load_texture("graphics/weapon/PlacedWall2.png")
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
        self.texture = arcade.load_texture("graphics/weapon/Barrel.png")
        self.health = 0
        self.object_type = 1  # Barrel object


class MineObject(Object):
    """Mine object class (placed by the player). """

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("graphics/weapon/Mine.png")
        self.health = 0
        self.object_type = 2  # Mine object


"""
Weapons
"""


class Weapon(arcade.Sprite):
    """Weapon base class."""

    def __init__(
        self, weapon_name: str = "graphics/weapon/Pistol.png", x: float = 0, y: float = 0
    ) -> None:
        self.is_gun = True
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.is_right = True
        self.damage = int(30)
        self.cd_max = int(30)  # 30/60 s
        self.bullet_speed = 25
        self.cost = int(0)
        self.life_span = int(20)
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
        bullet.center_x = self.center_x - 10
        bullet.center_y = self.center_y
        bullet.speed = self.bullet_speed
        bullet.life_span = self.life_span
        bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
        bullet.damage = self.damage
        bullets.append(bullet)
        return bullets

    def play_sound(self, effect_volume: int) -> None:
        self.sound.play(volume=effect_volume/20)


class Shotgun(Weapon):
    """Shotgun class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__("graphics/weapon/Shotgun.png", x, y)
        self.cd_max = int(40)  # 40/60 s
        self.cost = 15
        self.damage = 40
        self.life_span = 10
        self.bullet_num = 3
        self.bullet = EnergyBullet
        self.sound = arcade.Sound("audio/wpn_fire_m1014.wav")

    def get_bullet(self) -> arcade.SpriteList:
        bullets = arcade.SpriteList()
        for i in range(1, self.bullet_num + 1):
            angle = (-0.02 + 0.04 / (self.bullet_num+1) * i) * self.bullet_num
            bullet = self.bullet()
            bullet.life_span = self.life_span
            bullet.center_x = self.center_x - 10
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
        super().__init__("graphics/weapon/Uzi.png", x, y)
        self.cd_max = int(20)  # 20/60 s
        self.cost = 4
        self.damage = 30
        self.life_span = 25
        self.bullet_speed = 30
        self.bullet = EnergyBullet
        self.sound = arcade.Sound("audio/wpn_fire_p90.wav")

    def get_bullet(self) -> arcade.SpriteList:
        bullets = arcade.SpriteList()
        bullet = self.bullet()
        bullet.life_span = self.life_span
        bullet.center_x = self.center_x - 10
        bullet.center_y = self.center_y
        bullet.speed = self.bullet_speed
        bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
        bullet.damage = self.damage
        bullets.append(bullet)
        return bullets


class Rocket(Weapon):
    """Rocket class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__("graphics/weapon/Rocket.png", x, y)
        self.cd_max = int(40)  # 1/6 s
        self.cost = 30
        self.damage = 0
        self.bullet = Missile
        self.bullet_speed = 32
        self.life_span = 15
        self.bullet_num = 1
        self.sound = arcade.Sound("audio/wpn_fire_rocket.wav")

    def get_bullet(self) -> arcade.SpriteList:
        bullets = arcade.SpriteList()
        for i in range(1, self.bullet_num + 1):
            angle = (-0.1 + 0.2 / (self.bullet_num+1) * i) * self.bullet_num
            bullet = self.bullet()
            bullet.life_span = self.life_span
            bullet.center_x = self.center_x - 10
            bullet.center_y = self.center_y
            bullet.speed = self.bullet_speed
            bullet.aim = bullet.aim.rotate(angle)
            bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
            bullet.damage = self.damage
            bullets.append(bullet)
        return bullets


class PlacedWall(Weapon):
    """Wall class (as a weapon)."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__()
        self.is_gun = False
        self.cd_max = int(4)  # 1/6 s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.cost = 5
        self.is_right = True
        self.texture_list = [
            arcade.load_texture("graphics/weapon/PlacedWall0.png"),
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
        self.cd_max = int(4)  # 1/6 s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.cost = 25
        self.is_right = True
        self.texture_list = [
            arcade.load_texture("graphics/weapon/Barrel.png"),
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


class Mine(Weapon):
    """Mine class (as a weapon)."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__()
        self.is_gun = False
        self.cd_max = int(4)  # 1/6 s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.cost = 25
        self.is_right = True
        self.texture_list = [
            arcade.load_texture("graphics/weapon/Mine.png"),
        ]
        self.sound = arcade.Sound("audio/physics_place_object.wav")

    def update(self) -> None:
        self.center_x = self.pos.x
        self.center_y = self.pos.y

    def draw(self) -> None:
        pass

    def get_object(self) -> arcade.Sprite:
        barrel = MineObject()
        return barrel
