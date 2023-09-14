import arcade
import utils
import random
from weapon import Weapon
from pyglet.math import Vec2

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
GET_DAMAGE_LEN = 8


class Character(arcade.Sprite):
    """Character base class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None) -> None:
        # Properties
        self.health = 100
        self.is_walking = False
        self.speed = 800
        self.cd = int(0)
        self.cd_max = int(40)  # 2/3 s
        self.get_damage_len = int(0)  # draw get damage effect

        # Init position
        self.pos = Vec2(x, y)

        # Relative positions for visuals
        self.body_pos = Vec2(0, 0)  # controls the actual movement
        self.foot_l_pos = Vec2(-8, -16)
        self.foot_r_pos = Vec2(8, -16)
        self.collider_pos = Vec2(0, -3)
        self.shadow_pos = Vec2(-1, -9)

        # Init collider and physics engine
        super().__init__(
            "graphics/CharacterCollider.png",
            center_x=self.pos.x + self.collider_pos.x,
            center_y=self.pos.y + self.collider_pos.y,
            image_width=20,
            image_height=30,
            scale=1,
        )
        self.register_physics_engine(physics_engine)

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
            filename="graphics/Foot.png",
            center_x=self.foot_l_pos.x + self.pos.x,
            center_y=self.foot_l_pos.y + self.pos.x,
            image_width=4,
            image_height=4,
            scale=1,
        )
        self.foot_r = arcade.Sprite(
            filename="graphics/Foot.png",
            center_x=self.foot_r_pos.x + self.pos.x,
            center_y=self.foot_r_pos.y + self.pos.x,
            image_width=4,
            image_height=4,
            scale=1,
        )
        # Shadow sprite
        self.shadow = arcade.Sprite(
            center_x=self.collider_pos.x + self.pos.x,
            center_y=self.collider_pos.y + self.pos.x,
            scale=1,
        )
        self.shadow.texture = arcade.make_soft_square_texture(
            22, utils.Color.LIGHT_BLACK, 160, 100)

        # Body parts list for rendering
        self.parts = arcade.SpriteList()
        self.parts.append(self.shadow)
        self.parts.append(self.body)
        self.parts.append(self.foot_l)
        self.parts.append(self.foot_r)

    def move(self) -> None:
        """Move all the body parts"""
        self.pos.x = self.center_x - self.collider_pos.x
        self.pos.y = self.center_y - self.collider_pos.y

        self.body.center_x = self.pos.x + self.body_pos.x
        self.body.center_y = self.pos.y + self.body_pos.y

        self.foot_l.center_x = self.pos.x + self.foot_l_pos.x
        self.foot_l.center_y = self.pos.y + self.foot_l_pos.y
        self.foot_r.center_x = self.pos.x + self.foot_r_pos.x
        self.foot_r.center_y = self.pos.y + self.foot_r_pos.y

        self.shadow.center_x = self.pos.x + self.shadow_pos.x
        self.shadow.center_y = self.pos.y + self.shadow_pos.y

    def update(self) -> None:
        self.move()

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

    def draw(self, *, filter=None, pixelated=None, blend_function=None) -> None:
        self.parts.draw()
        if self.get_damage_len > 0:
            self.draw_get_damage()

    def draw_get_damage(self) -> None:
        arcade.draw_rectangle_filled(self.center_x, self.center_y,
                                     20, 24, utils.Color.RED_TRANSPARENT)


"""Play characters"""


class Player(Character):
    """Player game object."""

    body_texture = arcade.load_texture("graphics/Player.png")

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None) -> None:
        super().__init__(x, y, physics_engine)
        self.speed = 2000
        self.is_attack = False
        # self.energy = 0
        # self.health = 100
        self.kill_recover = 1
        self.explosion_damage = 20

        # For testing
        self.health = 100000
        self.energy = 100000

        # Player body sprite
        self.body.texture = self.body_texture

        # Track the player movement input
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.change_weapon_left = False
        self.change_weapon_right = False

        # Weapon
        self.weapon_pos = Vec2(16, -2)
        self.weapons = []
        self.weapon_index = 0
        pistol = Weapon(x=self.pos.x + self.weapon_pos.x,
                        y=self.pos.y + self.weapon_pos.y)
        self.add_weapon(pistol)
        self.current_weapon = self.weapons[self.weapon_index]
        self.cd_max = self.current_weapon.cd_max

    def move(self) -> None:
        """Player move by applying force from physics engine."""
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
        self.physics_engines[0].apply_force(self, (force.x, force.y))

        if force.mag != 0:
            self.is_walking = True
        else:
            self.is_walking = False

        super().move()

        self.current_weapon.pos = self.pos + self.weapon_pos

    def draw(self) -> None:
        if self.current_weapon.is_right:
            self.current_weapon.draw()
            super().draw()
        else:
            super().draw()
            self.current_weapon.draw()

    def update(self) -> None:
        if self.change_weapon_left:
            self.change_weapon(-1)
        if self.change_weapon_right:
            self.change_weapon(1)

        super().update()

        if self.current_weapon.is_right:
            self.weapon_pos = Vec2(16, -2)
        else:
            self.weapon_pos = Vec2(9, -2)

        self.current_weapon.update()

    def add_weapon(self, weapon: arcade.Sprite) -> None:
        self.weapons.append(weapon)

    def change_weapon(self, index_change: int) -> None:
        self.weapon_index += index_change
        self.weapon_index = self.weapon_index % len(self.weapons)
        self.current_weapon = self.weapons[self.weapon_index]
        self.cd_max = self.current_weapon.cd_max
        self.change_weapon_left = False
        self.change_weapon_right = False

    def aim(self, mouse_pos: Vec2) -> None:
        aim_pos = mouse_pos - self.pos
        self.current_weapon.aim(aim_pos)

    def attack(self) -> arcade.SpriteList:
        return self.current_weapon.get_bullet()

    def place(self) -> arcade.Sprite:
        return self.current_weapon.get_object()


class Rambo(Player):
    "Rambo character."

    body_texture = arcade.load_texture("graphics/Rambo.png")


"""Enemy characters"""


class EnemyWhite(Character):
    """EnemyWhite class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.health_max = int(100)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(20)
        self.body.texture = arcade.load_texture("graphics/EnemyWhite.png")
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player
        self.physics_engines.clear()

    def update(self) -> None:
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

        # if random.randrange(0, 10) < 2:  # add some randomization
        #     tmp = Vec2(2*random.random() - 1,
        #                2*random.random() - 1)
        #     force = tmp.normalize().scale(self.speed)
        #     return

        if self.last_force.distance(force) < 0.1:
            if abs(self.last_force.x - force.x) < 0.1:
                tmp.x = self.l_or_r
            if abs(self.last_force.y - force.y) < 0.1:
                tmp.y = self.u_or_d
            force = tmp.scale(2 * self.speed)  # get rid of the barrier
        else:
            self.last_force = force
            force = force.normalize().scale(self.speed)

        self.physics_engines[0].apply_force(self, (force.x, force.y))

        super().update()
