import random
import math
import arcade
from typing import Optional
from arcade.application import Window
from pyglet.math import Vec2
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

""" GLOBAL VARIABLE """
# Color palette
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

# Screen size
SCREEN_WIDTH = int(1280)
SCREEN_HEIGHT = int(720)

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.6

# Animations
BODY_ANIM = [-1, -1, -1, -1, -1, -1, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 1, 1, 1, 1, 1, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0,]
BODY_WALK = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]
L_WALK_X = [-1, -1, -1, 0, 0, 0, 1, 1, 1, 0, 0,
            0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0, 0]
L_WALK_Y = [1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0,
            0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0, 0]
R_WALK_X = [1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0,
            0, -1, -1, -1, 0, 0, 0, 1, 1, 1, 0, 0, 0]
R_WALK_Y = [1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0,
            0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0, 0]
GET_DAMAGE_LEN = int(8)

# Grid size, room width and height should be multiple of it
WALL_SIZE = float(30)

BULLET_FORCE = float(1000)
ENEMY_FORCE = float(4000)
KILL_RECOVER = int(5)


def get_sin(v: Vec2) -> float:
    """Get sine value of a given vector."""

    return v.y / v.distance(Vec2(0, 0))


class Wall(arcade.Sprite):
    """Basic wall class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.pos = Vec2(x, y)
        self.grid_idx = (int((x - (WALL_SIZE/2)) / 30),
                         int((y - (WALL_SIZE/2)) / 30))

        # Wall
        super().__init__(
            filename=None,
            center_x=self.pos.x,
            center_y=self.pos.y,
            image_width=WALL_SIZE,
            image_height=WALL_SIZE,
        )


class WallCorner(Wall):
    """Wall at the corner."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("./graphics/WallCorner.png")


class WallSideHorizontal(Wall):
    """Wall along the horizontal side."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("./graphics/WallSide.png")


class WallSideVertical(Wall):
    """Wall along the vertical side."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("./graphics/WallSide.png")
        self.angle = -90


class Room:
    """Room as a background in the game scene."""

    def __init__(self, width: float = 1500, height: float = 900) -> None:
        """width and heigh should be multiples of wall size."""
        self.width = width
        self.height = height
        self.pos = Vec2(self.width / 2, self.height / 2)
        self.spawn_pos = []

        self.grid_w = int(self.width / WALL_SIZE)
        self.grid_h = int(self.height / WALL_SIZE)

        # Basic room layout
        half_wall = WALL_SIZE / 2

        # set boundary corner walls
        self.walls = [WallCorner(half_wall, half_wall), WallCorner(half_wall, self.height - half_wall), WallCorner(
            self.width - half_wall, half_wall), WallCorner(self.width - half_wall, self.height - half_wall)]

        # set bottom walls
        tmp_idx = random.randrange(3, self.grid_w - 3)
        for i in range(1, self.grid_w - 1):
            if i == tmp_idx - 1 or i == tmp_idx + 1:
                self.walls.append(WallCorner(
                    half_wall + i * WALL_SIZE, half_wall))
                continue
            elif i == tmp_idx:
                self.walls.append(WallCorner(
                    half_wall + i * WALL_SIZE, -half_wall))
                self.spawn_pos.append(
                    Vec2(half_wall + i * WALL_SIZE, half_wall))
                continue
            self.walls.append(WallSideHorizontal(
                half_wall + i * WALL_SIZE, half_wall))

        # set top walls
        tmp_idx = random.randrange(3, self.grid_w - 3)
        for i in range(1, self.grid_w - 1):
            if i == tmp_idx - 1 or i == tmp_idx + 1:
                self.walls.append(WallCorner(
                    half_wall + i * WALL_SIZE, self.height - half_wall))
                continue
            elif i == tmp_idx:
                self.walls.append(WallCorner(
                    half_wall + i * WALL_SIZE, self.height + half_wall))
                self.spawn_pos.append(
                    Vec2(half_wall + i * WALL_SIZE, self.height - half_wall))
                continue
            self.walls.append(WallSideHorizontal(
                half_wall + i * WALL_SIZE, self.height - half_wall))

        # set left walls
        tmp_idx = random.randrange(3, self.grid_h - 3)
        for i in range(1, self.grid_h - 1):
            if i == tmp_idx - 1 or i == tmp_idx + 1:
                self.walls.append(WallCorner(
                    half_wall, half_wall + i * WALL_SIZE))
                continue
            elif i == tmp_idx:
                self.walls.append(WallCorner(
                    -half_wall, half_wall + i * WALL_SIZE))
                self.spawn_pos.append(
                    Vec2(half_wall, half_wall + i * WALL_SIZE))
                continue
            self.walls.append(WallSideVertical(
                half_wall, half_wall + i * WALL_SIZE))

        # set right walls
        tmp_idx = random.randrange(3, self.grid_h - 3)
        for i in range(1, self.grid_h - 1):
            if i == tmp_idx - 1 or i == tmp_idx + 1:
                self.walls.append(WallCorner(
                    self.width - half_wall, half_wall + i * WALL_SIZE))
                continue
            elif i == tmp_idx:
                self.walls.append(WallCorner(
                    self.width + half_wall, half_wall + i * WALL_SIZE))
                self.spawn_pos.append(
                    Vec2(self.width - half_wall, half_wall + i * WALL_SIZE))
                continue
            self.walls.append(WallSideVertical(
                self.width - half_wall, half_wall + i * WALL_SIZE))

        # set some walls in the room
        self.walls.append(WallCorner(
            half_wall + 10 * WALL_SIZE, half_wall + 10 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 20 * WALL_SIZE, half_wall + 10 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 30 * WALL_SIZE, half_wall + 10 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 40 * WALL_SIZE, half_wall + 10 * WALL_SIZE))

        self.walls.append(WallCorner(
            half_wall + 10 * WALL_SIZE, half_wall + 20 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 20 * WALL_SIZE, half_wall + 20 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 30 * WALL_SIZE, half_wall + 20 * WALL_SIZE))
        self.walls.append(WallCorner(
            half_wall + 40 * WALL_SIZE, half_wall + 20 * WALL_SIZE))

    def draw(self) -> None:
        # Room background
        arcade.draw_rectangle_filled(
            self.pos.x, self.pos.y, self.width, self.height, GROUND_WHITE
        )
        # Walls
        for wall in self.walls:
            wall.draw()


class StartRoom:
    """Game start room."""

    def __init__(self, width: float = 1500, height: float = 900) -> None:
        self.width = width
        self.height = height
        self.pos = Vec2(self.width / 2, self.height / 2)
        self.spawn_pos = []

        self.grid_w = int(self.width / WALL_SIZE)
        self.grid_h = int(self.height / WALL_SIZE)

        # Basic room layout
        half_wall = WALL_SIZE / 2

        # set boundary corner walls
        self.walls = [WallCorner(half_wall, half_wall), WallCorner(half_wall, self.height - half_wall), WallCorner(
            self.width - half_wall, half_wall), WallCorner(self.width - half_wall, self.height - half_wall)]

        # set bottom and top walls
        for i in range(1, self.grid_w - 1):
            self.walls.append(WallSideHorizontal(
                half_wall + i * WALL_SIZE, half_wall))
            self.walls.append(WallSideHorizontal(
                half_wall + i * WALL_SIZE, self.height - half_wall))

        # set left and right walls
        for i in range(1, self.grid_h - 1):
            self.walls.append(WallSideVertical(
                half_wall, half_wall + i * WALL_SIZE))
            self.walls.append(WallSideVertical(
                self.width - half_wall, half_wall + i * WALL_SIZE))

    def draw(self) -> None:
        # Room background
        arcade.draw_rectangle_filled(
            self.pos.x, self.pos.y, self.width, self.height, GROUND_WHITE
        )
        # Walls
        for wall in self.walls:
            wall.draw()


class Bullet(arcade.Sprite):
    """Bullet base class"""

    def __init__(self) -> None:
        super().__init__(
            filename="./graphics/Bullet.png",
            image_width=6,
            image_height=6,
            scale=1,
        )
        self.aim = Vec2(0, 0)
        self.speed = float(0)
        self.damage = int(0)
        self.life_span = int(20)

    def set_angle(self, rotate_angle: float) -> None:
        self.angle = rotate_angle


class FireBall(Bullet):
    """FireBall class for enemy red."""

    def __init__(self) -> None:
        super().__init__()
        self.texture = arcade.load_texture("./graphics/FireBall.png")
        self.life_span = int(60)


class Gun(arcade.Sprite):
    """Gun weapon class."""

    def __init__(
        self, gun_name: str = "./graphics/Pistol.png", x: float = 0, y: float = 0
    ) -> None:
        self.damage = 40
        self.cd_max = int(30)  # 0.5s
        self.pos = Vec2(x, y)
        self.aim_pos = Vec2(0, 0)
        self.is_right = True
        self.bullet_speed = 25
        self.texture_list = [
            arcade.load_texture(gun_name),
            arcade.load_texture(gun_name, flipped_horizontally=True),
        ]
        super().__init__(
            filename=gun_name,
            center_x=self.pos.x,
            center_y=self.pos.y,
            image_width=20,
            image_height=10,
        )
        self.bullet = Bullet

    def update(self) -> None:
        self.center_x = self.pos.x
        self.center_y = self.pos.y
        if self.is_right:
            self.texture = self.texture_list[0]
        else:
            self.texture = self.texture_list[1]

    def aim(self, aim_pos: Vec2) -> None:
        self.aim_pos = aim_pos
        if aim_pos.x >= 0:
            self.is_right = True
            rotate_angle = math.degrees(math.asin(get_sin(aim_pos)))
        else:
            self.is_right = False
            rotate_angle = -math.degrees(math.asin(get_sin(aim_pos)))

        self.angle = rotate_angle

    def get_bullet(self) -> Bullet:
        bullet = self.bullet()
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.speed = self.bullet_speed
        bullet.aim = self.aim_pos.normalize().scale(bullet.speed)
        bullet.damage = self.damage
        return bullet


class Character(arcade.Sprite):
    """Character base class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        # Properties
        self.health = 100
        self.is_walking = False
        self.speed = 800
        self.cd = int(0)
        self.cd_max = int(40)  # 40 / 60
        self.get_damage_len = int(0)  # draw get damage effect

        # Init position
        self.pos = Vec2(x, y)

        # Relative positions for visuals
        self.body_pos = Vec2(0, 0)  # controls the actual movement
        self.foot_l_pos = Vec2(-8, -16)
        self.foot_r_pos = Vec2(8, -16)
        self.collider_pos = Vec2(0, -3)

        # init with collider
        super().__init__(
            "./graphics/CharacterCollider.png",
            center_x=self.pos.x + self.collider_pos.x,
            center_y=self.pos.y + self.collider_pos.y,
            image_width=20,
            image_height=30,
            scale=1,
        )

        # Animation init
        self.body_move_up = False
        self.body_move_frames_max = len(BODY_ANIM)
        self.body_move_frames = self.body_move_frames_max
        self.walking_frames_max = len(L_WALK_X)
        self.walking_frames = self.walking_frames_max
        self.velocity = Vec2(0, 0)

        # Visuals
        # Body sprite
        self.body = arcade.Sprite()
        # Feet sprite
        self.foot_l = arcade.Sprite(
            filename="./graphics/Foot.png",
            center_x=self.foot_l_pos.x + self.pos.x,
            center_y=self.foot_l_pos.y + self.pos.x,
            image_width=4,
            image_height=4,
            scale=1,
        )
        self.foot_r = arcade.Sprite(
            filename="./graphics/Foot.png",
            center_x=self.foot_r_pos.x + self.pos.x,
            center_y=self.foot_r_pos.y + self.pos.x,
            image_width=4,
            image_height=4,
            scale=1,
        )

    def move(self, physic_engine: PymunkPhysicsEngine) -> None:
        self.pos.x = self.center_x - self.collider_pos.x
        self.pos.y = self.center_y - self.collider_pos.y

        self.body.center_x = self.pos.x + self.body_pos.x
        self.body.center_y = self.pos.y + self.body_pos.y

        self.foot_l.center_x = self.pos.x + self.foot_l_pos.x
        self.foot_l.center_y = self.pos.y + self.foot_l_pos.y
        self.foot_r.center_x = self.pos.x + self.foot_r_pos.x
        self.foot_r.center_y = self.pos.y + self.foot_r_pos.y

    def update(self, physic_engine: PymunkPhysicsEngine) -> None:
        self.move(physic_engine)

        # Body animation
        if self.body_move_frames == 0:  # reset frames
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up

        self.body_move_frames -= 1
        self.body.center_y += BODY_ANIM[self.body_move_frames]

        # Feet animation
        if self.walking_frames == 0:  # reset frames
            self.walking_frames = self.walking_frames_max

        self.walking_frames -= 1

        if self.is_walking:
            self.foot_l.center_x += L_WALK_X[self.walking_frames]
            self.foot_l.center_y += L_WALK_Y[self.walking_frames]
            self.foot_r.center_x += R_WALK_X[self.walking_frames]
            self.foot_r.center_y += R_WALK_Y[self.walking_frames]
        else:
            # reset the walking animation
            self.foot_l.center_x = self.foot_l_pos.x + self.pos.x
            self.foot_l.center_y = self.foot_l_pos.y + self.pos.y
            self.foot_r.center_x = self.foot_r_pos.x + self.pos.x
            self.foot_r.center_y = self.foot_r_pos.y + self.pos.y
            self.walking_frames = self.walking_frames_max

        self.get_damage_len -= 1

    def draw(self) -> None:
        # self.box_collider.draw()
        self.body.draw()
        self.foot_l.draw()
        self.foot_r.draw()
        if self.get_damage_len > 0:
            self.draw_get_damage()

    def draw_get_damage(self) -> None:
        arcade.draw_rectangle_filled(self.center_x, self.center_y,
                                     20, 24, RED_TRANSPARENT)


class Player(Character):
    """Player game object."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.speed = 2000
        self.is_attack = False
        self.energy = 200
        self.energy_max = 200
        self.player_health_max = 100

        # Player body sprite
        self.body = arcade.Sprite(
            filename="./graphics/Player.png",
            center_x=self.body_pos.x + self.pos.x,
            center_y=self.body_pos.y + self.pos.y,
            image_width=20,
            image_height=24,
            scale=1,
        )

        # Track the player movement input
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        # Weapon
        self.weapon_pos = Vec2(16, -2)
        self.weapons = []
        self.weapon_index = 0
        self.add_weapon()
        self.current_weapon = self.weapons[self.weapon_index]

    def move(self, physic_engine: PymunkPhysicsEngine) -> None:
        force = Vec2(0, 0)

        if self.move_up and not self.move_down:
            force.y = 1
        elif self.move_down and not self.move_up:
            force.y = -1
        if self.move_left and not self.move_right:
            force.x = -1
        elif self.move_right and not self.move_left:
            force.x = 1

        force = force.normalize().scale(self.speed)
        physic_engine.apply_force(self, (force.x, force.y))

        if force.mag != 0:
            self.is_walking = True
        else:
            self.is_walking = False

        super().move(physic_engine)

        self.current_weapon.pos = self.pos + self.weapon_pos

    def draw(self) -> None:
        if self.current_weapon.is_right:
            self.current_weapon.draw()
            super().draw()
        else:
            super().draw()
            self.current_weapon.draw()

    def update(self, physic_engine: PymunkPhysicsEngine) -> None:
        super().update(physic_engine)
        if self.current_weapon.is_right:
            self.weapon_pos = Vec2(16, -2)
        else:
            self.weapon_pos = Vec2(9, -2)
        self.current_weapon.update()

    def add_weapon(self, name: str = "./graphics/Pistol.png") -> None:
        gun = Gun(
            name, x=self.pos.x + self.weapon_pos.x, y=self.pos.y + self.weapon_pos.y
        )
        self.cd_max = gun.cd_max
        self.weapons.append(gun)

    def change_weapon(self):
        # TODO: add change weapon with Q and E
        self.current_weapon = self.weapons[self.weapon_index]

    def aim(self, mouse_pos: Vec2) -> None:
        aim_pos = mouse_pos - self.pos
        self.current_weapon.aim(aim_pos)

    def attack(self) -> Bullet:
        return self.current_weapon.get_bullet()


class EnemyWhite(Character):
    """EnemyWhite class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.health_max = int(100)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(20)

        # EnemyWhite body sprite
        self.body = arcade.Sprite(
            filename="./graphics/EnemyWhite.png",
            center_x=self.body_pos.x + self.pos.x,
            center_y=self.body_pos.y + self.pos.y,
            image_width=20,
            image_height=24,
            scale=1,
        )

    def follow_sprite(self, player_sprite: arcade.Sprite, physic_engine: PymunkPhysicsEngine) -> None:
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(player_sprite.center_x, player_sprite.center_y)
        force = player_pos - current_pos

        if random.randrange(0, 100) < 20:  # add some randomization
            tmp = Vec2(random.gauss(0, 0.2), random.gauss(0, 0.2))
            force = tmp.normalize().scale(self.speed)
            return

        if self.last_force.distance(force) < 0.1:
            tmp = Vec2(0, 0)
            if abs(self.last_force.x - force.x) < 0.1:
                tmp.x = 1
            if abs(self.last_force.y - force.y) < 0.1:
                tmp.y = 1
            force = tmp.scale(4 * self.speed)  # get rid of the barrier
        else:
            self.last_force = force
            force = force.normalize().scale(self.speed)

        physic_engine.apply_force(self, (force.x, force.y))


class EnemyRed(Character):
    """EnemyRed class."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.health = int(220)
        self.health_max = int(220)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.shoot_range = 280
        self.cd_max = int(60)
        self.bullet = FireBall
        self.hit_damage = int(10)

        # EnemyRed body sprite
        self.body = arcade.Sprite(
            filename="./graphics/EnemyRed.png",
            center_x=self.body_pos.x + self.pos.x,
            center_y=self.body_pos.y + self.pos.y,
            image_width=20,
            image_height=26,
            scale=1,
        )

    def follow_sprite(self, player_sprite: arcade.Sprite, physic_engine: PymunkPhysicsEngine) -> None:
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(player_sprite.center_x, player_sprite.center_y)
        force = player_pos - current_pos

        if current_pos.distance(player_pos) < self.shoot_range:
            self.is_walking = False
            return

        self.is_walking = True

        if random.randrange(0, 100) < 20:  # add some randomization
            tmp = Vec2(random.gauss(0, 0.2), random.gauss(0, 0.2))
            force = tmp.normalize().scale(self.speed)
            return

        if self.last_force.distance(force) < 0.1:
            tmp = Vec2(0, 0)
            if abs(self.last_force.x - force.x) < 0.1:
                tmp.x = 1
            if abs(self.last_force.y - force.y) < 0.1:
                tmp.y = 1
            force = tmp.scale(4 * self.speed)  # get rid of the barrier
        else:
            self.last_force = force
            force = force.normalize().scale(self.speed)

        physic_engine.apply_force(self, (force.x, force.y))

    def attack(self, player_sprite: arcade.Sprite) -> FireBall:
        # enemy red attack property
        bullet_speed = 6
        damage = 30
        aim_pos = Vec2(player_sprite.center_x - self.center_x,
                       player_sprite.center_y - self.center_y)
        bullet = self.bullet()
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.speed = bullet_speed
        bullet.aim = aim_pos.normalize().scale(bullet.speed)
        bullet.damage = damage
        return bullet


class BoxHeadGame(arcade.View):
    """Main application class."""

    def __init__(self):
        """Initializer"""

        super().__init__()
        self.mouse_x = None
        self.mouse_y = None
        self.mouse_pos = Vec2(0, 0)
        self.mouse_sprite = arcade.Sprite("./graphics/Cursor.png")

        # Sprite lists
        self.wall_list = None
        self.player = None
        self.player_bullet_list = None
        self.enemy_white_list = None
        self.enemy_red_list = None
        self.enemy_bullet_list = None

        # Physics engine so we don't run into walls.
        self.physics_engine: Optional[PymunkPhysicsEngine] = None

        # track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Create the cameras. One for the GUI, one for the sprites.
        # scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def setup(self):
        """Set up the game and initialize the variables."""

        # Gameplay set up
        self.round = 0
        self.score = 0

        # UI set up
        self.health_sprite = arcade.Sprite(
            filename="./graphics/Health.png",
            center_x=40,
            center_y=SCREEN_HEIGHT - 40,
            image_width=25,
            image_height=25,
            scale=1,
        )
        self.energy_sprite = arcade.Sprite(
            filename="./graphics/Energy.png",
            center_x=40,
            center_y=SCREEN_HEIGHT - 70,
            image_width=25,
            image_height=25,
            scale=1,
        )
        self.weapon_slot_sprite = arcade.Sprite(
            filename="./graphics/WeaponSlot.png",
            center_x=150,
            center_y=SCREEN_HEIGHT - 120,
            image_width=80,
            image_height=40,
            scale=1,
        )

        # GameObject lists
        self.wall_list = arcade.SpriteList()
        self.enemy_white_list = arcade.SpriteList()
        self.enemy_red_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

        # setup room background and player
        self.game_room = Room()
        for wall in self.game_room.walls:
            self.wall_list.append(wall)

        # set up the player
        self.player = Player(float(SCREEN_WIDTH / 2), float(SCREEN_HEIGHT / 2))

        # set up the enemy
        self.spawn_enemy_cd = 0

        # set the most basic background color
        arcade.set_background_color(BLACK)

        # set up th physics engine
        damping = 0.01

        # set the gravity. (0, 0) is good for outer space and top-down.
        gravity = (0, 0)

        # create the physics engine
        self.physics_engine = PymunkPhysicsEngine(damping=damping,
                                                  gravity=gravity)

        # add the player
        self.physics_engine.add_sprite(self.player,
                                       friction=0,
                                       moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
                                       damping=0.001,
                                       collision_type="player",
                                       elasticity=0.1,
                                       max_velocity=400)

        # create the walls
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=0,
                                            collision_type="wall",
                                            body_type=PymunkPhysicsEngine.STATIC)

    def spawn_enemy(self):
        # spawn enemy white
        if self.spawn_enemy_cd <= 5:
            for i in range(0, 4):
                tmp_enemy = EnemyWhite(
                    self.game_room.spawn_pos[i].x, self.game_room.spawn_pos[i].y)
                self.enemy_white_list.append(tmp_enemy)
                self.physics_engine.add_sprite(tmp_enemy,
                                               friction=0,
                                               moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                               damping=0.001,
                                               collision_type="enemy")

        # spawn enemy red
        if self.spawn_enemy_cd == 6:
            for i in range(0, 4):
                tmp_enemy = EnemyRed(
                    self.game_room.spawn_pos[i].x, self.game_room.spawn_pos[i].y)
                self.enemy_red_list.append(tmp_enemy)
                self.physics_engine.add_sprite(tmp_enemy,
                                               friction=0,
                                               moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                               damping=0.001,
                                               collision_type="enemy")
        self.spawn_enemy_cd += 1
        self.spawn_enemy_cd %= 10000

    def update_player_attack(self):
        if self.player.is_attack:
            if self.player.cd == self.player.cd_max:
                self.player.cd = 0

            if self.player.cd == 0:
                bullet = self.player.attack()
                bullet.change_x = bullet.aim.x
                bullet.change_y = bullet.aim.y
                self.player_bullet_list.append(bullet)

        self.player.cd = min(self.player.cd + 1, self.player.cd_max)

    def process_player_bullet(self):
        self.player_bullet_list.update()

        for bullet in self.player_bullet_list:
            bullet.life_span -= 1

            hit_list = arcade.check_for_collision_with_list(
                bullet, self.enemy_white_list)

            hit_list_red = arcade.check_for_collision_with_list(
                bullet, self.enemy_red_list)

            hit_list.extend(hit_list_red)

            for enemy in hit_list:
                enemy.health -= bullet.damage
                self.physics_engine.apply_force(
                    enemy, (bullet.aim.x * BULLET_FORCE, bullet.aim.y * BULLET_FORCE))
                enemy.get_damage_len = GET_DAMAGE_LEN
                if enemy.health <= 0:
                    enemy.remove_from_sprite_lists()
                    self.player.health = min(self.player.health + KILL_RECOVER,
                                             self.player.player_health_max)
                    self.score += enemy.health_max
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def update_enemy_attack(self):
        for enemy in self.enemy_white_list:
            if arcade.check_for_collision(enemy, self.player):
                self.player.health = max(
                    self.player.health - enemy.hit_damage, 0)
                push = enemy.last_force.normalize().scale(ENEMY_FORCE)
                self.physics_engine.apply_force(self.player, (push.x, push.y))
                self.player.get_damage_len = GET_DAMAGE_LEN

        for enemy in self.enemy_red_list:
            if arcade.check_for_collision(enemy, self.player):
                self.player.health = max(
                    self.player.health - enemy.hit_damage, 0)
                push = enemy.last_force.normalize().scale(ENEMY_FORCE)
                self.physics_engine.apply_force(self.player, (push.x, push.y))
                self.player.get_damage_len = GET_DAMAGE_LEN

            if enemy.is_walking == False:
                if enemy.cd == enemy.cd_max:
                    enemy.cd = 0

                if enemy.cd == 0:
                    bullet = enemy.attack(self.player)
                    bullet.change_x = bullet.aim.x
                    bullet.change_y = bullet.aim.y
                    self.enemy_bullet_list.append(bullet)

            enemy.cd = min(enemy.cd + 1, enemy.cd_max)

    def process_enemy_bullet(self):
        self.enemy_bullet_list.update()

        for bullet in self.enemy_bullet_list:
            bullet.life_span -= 1

            # TODO: decide whether to allow enemy shoot at each other
            # hit_list = arcade.check_for_collision_with_list(
            #     bullet, self.enemy_white_list)

            # for enemy in hit_list:
            #     enemy.health -= bullet.damage
            #     self.physics_engine.apply_force(
            #         enemy, (bullet.aim.x * BULLET_FORCE, bullet.aim.y * BULLET_FORCE))
            #     enemy.get_damage_len = GET_DAMAGE_LEN
            #     if enemy.health <= 0:
            #         enemy.remove_from_sprite_lists()

            if arcade.check_for_collision(bullet, self.player):
                self.player.health = max(self.player.health - bullet.damage, 0)
                bullet.remove_from_sprite_lists()
                self.physics_engine.apply_force(
                    self.player, (bullet.aim.x * BULLET_FORCE, bullet.aim.y * BULLET_FORCE))
                self.player.get_damage_len = GET_DAMAGE_LEN

            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def draw_ui_player(self):
        # Health bar
        self.health_sprite.draw()
        arcade.draw_rectangle_filled(160, SCREEN_HEIGHT - 40,
                                     204, 22, LIGHT_BLACK)
        arcade.draw_rectangle_filled(160, SCREEN_HEIGHT - 40,
                                     200, 16, LIGHT_GRAY)
        arcade.draw_rectangle_filled(60 + self.player.health, SCREEN_HEIGHT - 40,
                                     self.player.health * 2, 16, HEALTH_RED)

        # Energy bar
        self.energy_sprite.draw()
        arcade.draw_rectangle_filled(160, SCREEN_HEIGHT - 70,
                                     204, 22, LIGHT_BLACK)
        arcade.draw_rectangle_filled(160, SCREEN_HEIGHT - 70,
                                     200, 16, LIGHT_GRAY)
        arcade.draw_rectangle_filled(60 + float(self.player.energy/2), SCREEN_HEIGHT - 70,
                                     self.player.energy, 16, ENERGY_BLUE)

        # Weapon slot
        self.weapon_slot_sprite.draw()
        cur_weapon_sprit = arcade.Sprite()
        cur_weapon_sprit.texture = self.player.current_weapon.textures[0]
        cur_weapon_sprit.scale = 2
        cur_weapon_sprit.center_x = 150
        cur_weapon_sprit.center_y = SCREEN_HEIGHT - 120
        cur_weapon_sprit.draw()

        if self.player.weapon_index - 1 >= 0:
            pass
        if self.player.weapon_index <= len(self.player.weapons) - 1:
            pass
        last_weapon_sprit = cur_weapon_sprit
        last_weapon_sprit.center_x = 70
        last_weapon_sprit.color = (255, 255, 255, 100)
        last_weapon_sprit.draw()
        next_weapon_sprit = cur_weapon_sprit
        next_weapon_sprit.center_x = 230
        next_weapon_sprit.color = (255, 255, 255, 100)
        next_weapon_sprit.draw()

    def draw_ui_game(self):
        round = str(self.round)
        arcade.draw_text(round, float(SCREEN_WIDTH/2),
                         SCREEN_HEIGHT - 50, BLACK,
                         20, 2, "left", "Kenney Future")
        score = str(self.score)
        arcade.draw_text(score, SCREEN_WIDTH - 150,
                         SCREEN_HEIGHT - 50, BLACK,
                         20, 2, "left", "Kenney Future")

    def on_draw(self):
        """Render the screen."""

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # draw all the sprites.
        self.game_room.draw()
        self.player.draw()
        # TODO: Bullet design review
        for enemy in self.enemy_white_list:
            enemy.draw()
        for enemy in self.enemy_red_list:
            enemy.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()

        # Select the (un-scrolled) camera for our GUI
        self.camera_gui.use()

        # Mouse cursor
        if self.mouse_x and self.mouse_y:
            self.mouse_sprite.draw()

        # Render the GUI
        self.draw_ui_player()
        self.draw_ui_game()

    def on_update(self, delta_time):
        # call update on all sprites
        self.physics_engine.step()

        # update player
        self.player.update(self.physics_engine)
        self.update_player_attack()
        self.process_player_bullet()

        # update enemy
        if len(self.enemy_white_list) == 0 and len(self.enemy_red_list) == 0:
            self.round += 1
            # TODO: change this value when refining the numbers
            self.spawn_enemy_cd = 0

        self.spawn_enemy()
        for enemy in self.enemy_white_list:
            enemy.update(self.physics_engine)
            enemy.follow_sprite(self.player, self.physics_engine)

        for enemy in self.enemy_red_list:
            enemy.update(self.physics_engine)
            enemy.follow_sprite(self.player, self.physics_engine)
        self.update_enemy_attack()
        self.process_enemy_bullet()

        # scroll the screen to the player
        self.scroll_to_player()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.W:
            self.player.move_up = True
        elif key == arcade.key.S:
            self.player.move_down = True
        elif key == arcade.key.A:
            self.player.move_left = True
        elif key == arcade.key.D:
            self.player.move_right = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.W:
            self.player.move_up = False
        elif key == arcade.key.S:
            self.player.move_down = False
        elif key == arcade.key.A:
            self.player.move_left = False
        elif key == arcade.key.D:
            self.player.move_right = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Mouse movement."""

        self.mouse_x = x
        self.mouse_y = y
        self.mouse_pos.x = self.mouse_x + self.camera_sprites.position.x
        self.mouse_pos.y = self.mouse_y + self.camera_sprites.position.y
        self.mouse_sprite.center_x = self.mouse_x
        self.mouse_sprite.center_y = self.mouse_y
        self.player.aim(self.mouse_pos)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.is_attack = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.is_attack = False

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.

        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        position = Vec2(self.camera_sprites.position.x,
                        self.camera_sprites.position.y)
        # limit the camera position within the room
        if (
            self.player.pos.x > float(SCREEN_WIDTH / 2) - 5
            and self.game_room.width - self.player.pos.x > float(SCREEN_WIDTH / 2) - 5
        ):
            position.x = self.player.pos.x - float(SCREEN_WIDTH / 2)
        if (
            self.player.pos.y > float(SCREEN_HEIGHT / 2) - 5
            and self.game_room.height - self.player.pos.y > float(SCREEN_HEIGHT / 2) - 5
        ):
            position.y = self.player.pos.y - float(SCREEN_HEIGHT / 2)

        self.camera_sprites.move_to(position, CAMERA_SPEED)


class BoxHeadMenu(BoxHeadGame):
    """Start menu."""

    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()
        
        # clean up
        for wall in self.wall_list:
            self.physics_engine.remove_sprite(wall)
        self.wall_list.clear()

        # setup game view
        self.game_view = BoxHeadGame()
        self.game_view.setup()

        # Start menu background
        self.game_room = StartRoom()
        self.physics_engine.add_sprite_list(self.game_room.walls,
                                            friction=0,
                                            collision_type="wall",
                                            body_type=PymunkPhysicsEngine.STATIC)
        self.start_sprite_list = arcade.SpriteList()
        self.start_sprite_list.append(
            arcade.Sprite(filename="./graphics/Title.png",
                          scale=0.4,
                          center_x=SCREEN_WIDTH / 2,
                          center_y=SCREEN_HEIGHT - 160)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="./graphics/MoveGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=200)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="./graphics/ShootGuide.png",
                          scale=0.3,
                          center_x=SCREEN_WIDTH - 200,
                          center_y=200)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="./graphics/PauseGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=SCREEN_HEIGHT - 100)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="./graphics/WeaponChangeGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=SCREEN_HEIGHT - 200)
        )
        self.start_button = arcade.Sprite(
            filename="./graphics/Start.png",
            scale=0.6,
            center_x=SCREEN_WIDTH/2 + 160,
            center_y=SCREEN_HEIGHT / 2
        )
        self.option_button = arcade.Sprite(
            filename="./graphics/Option.png",
            scale=0.6,
            center_x=SCREEN_WIDTH/2 + 160,
            center_y=SCREEN_HEIGHT / 2 - 60
        )
        self.exit_button = arcade.Sprite(
            filename="./graphics/Exit.png",
            scale=0.6,
            center_x=SCREEN_WIDTH/2 + 160,
            center_y=SCREEN_HEIGHT / 2 - 120
        )

    def on_update(self, delta_time):
        # call update on all sprites
        self.physics_engine.step()

        # update player
        self.player.update(self.physics_engine)
        self.update_player_attack()
        self.process_player_bullet()

        # scroll the screen to the player
        self.scroll_to_player()

    def on_draw(self):
        self.clear()
        self.camera_sprites.use()

        # draw all the sprites.
        self.game_room.draw()
        self.start_sprite_list.draw()
        self.player.draw()
        self.player_bullet_list.draw()
        self.start_button.draw()
        self.option_button.draw()
        self.exit_button.draw()

        # Select the (un-scrolled) camera for our GUI
        self.camera_gui.use()

        # Mouse cursor
        if self.mouse_x and self.mouse_y:
            self.mouse_sprite.draw()

    def spawn_enemy(self):
        pass

    def draw_ui_game(self):
        pass

    def draw_ui_player(self):
        pass

    def process_player_bullet(self):
        self.player_bullet_list.update()

        for bullet in self.player_bullet_list:
            bullet.life_span -= 1

            if arcade.check_for_collision(bullet, self.start_button):
                self.window.show_view(self.game_view)
                bullet.remove_from_sprite_lists()

            if arcade.check_for_collision(bullet, self.option_button):
                bullet.remove_from_sprite_lists()

            if arcade.check_for_collision(bullet, self.exit_button):
                arcade.close_window()
                pass

            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def update_enemy_attack(self):
        pass

    def process_enemy_bullet(self):
        pass


def main():
    """Main function"""

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT,
                           "BoxHead 2D: Invincible")
    window.set_mouse_visible(False)
    menu_view = BoxHeadMenu()
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
