import arcade
import utils
import random
import weapon
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
            "graphics/character/CharacterCollider.png",
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
            filename="graphics/character/Foot.png",
            center_x=self.foot_l_pos.x + self.pos.x,
            center_y=self.foot_l_pos.y + self.pos.x,
            image_width=4,
            image_height=4,
            scale=1,
        )
        self.foot_r = arcade.Sprite(
            filename="graphics/character/Foot.png",
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
        # Get damage sprite
        self.damage_sprite = arcade.SpriteSolidColor(20, 24,
                                                     utils.Color.RED_TRANSPARENT)
        self.damage_sprite.alpha = 0

        # Body parts list for rendering
        self.parts = arcade.SpriteList()
        self.parts.append(self.shadow)
        self.parts.append(self.body)
        self.parts.append(self.foot_l)
        self.parts.append(self.foot_r)
        self.parts.append(self.damage_sprite)

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

        self.damage_sprite.center_x = self.center_x
        self.damage_sprite.center_y = self.center_y

    def update(self) -> None:
        self.move()

        # Body animation
        if self.body_move_frames == 0:  # reset frames
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up

        self.body_move_frames -= 1
        self.body.center_y += BODY_ANIM[self.body_move_frames]

        self.get_damage_len -= 1

        if self.get_damage_len > 0:
            self.damage_sprite.alpha = 150
        else:
            self.damage_sprite.alpha = 0

    def draw(self, *, filter=None, pixelated=None, blend_function=None) -> None:
        self.parts.draw()

    def register_dir_field(self, dir_field: dict) -> None:
        self.dir_field = dir_field

    def get_dir(self) -> None:
        grid_x = int(self.center_x / utils.Utils.WALL_SIZE)
        grid_y = int(self.center_y / utils.Utils.WALL_SIZE)
        self.force = self.dir_field[(grid_x, grid_y)]

"""Play characters"""


class Player(Character):
    """Player game object."""

    body_texture = arcade.load_texture("graphics/character/Player.png")
    name = "Nameless"
    description = "Nameless Description"

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None) -> None:
        super().__init__(x, y, physics_engine)
        self.speed = 1600
        self.is_attack = False
        self.energy = int(0)
        self.health = int(500)
        self.kill_recover = int(5)
        self.explosion_damage = 100
        self.money = 150
        self.luck = 6

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
        pistol = weapon.Weapon(x=self.pos.x + self.weapon_pos.x,
                               y=self.pos.y + self.weapon_pos.y)
        self.add_weapon(pistol)
        self.current_weapon = self.weapons[self.weapon_index]
        self.cd_max = self.current_weapon.cd_max

        # Weapon settings
        self.is_rocket_multi = False
        self.is_barrel_multi = False
        self.is_mine_multi = False

        if utils.Utils.IS_TESTING:
            self.health = 10000
            self.energy = 20000
            self.money = 100000

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

    def get_damage(self, damage: int) -> None:
        self.health = max(self.health - damage, 0)

    def health_recover(self) -> None:
        self.health += self.kill_recover

    def get_energy(self, energy: int) -> None:
        self.energy += energy


class Rambo(Player):
    "Rambo character."

    body_texture = arcade.load_texture("graphics/character/Rambo.png")
    name = "Rambo"
    description = "Rambo Description"

    def get_damage(self, damage: int) -> None:
        super().get_damage(damage)
        self.get_energy(damage)


"""Enemy characters"""


class EnemyWhite(Character):
    """EnemyWhite class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.health_max = int(100)
        self.is_walking = True
        self.hit_damage = int(20)
        self.body.texture = arcade.load_texture(
            "graphics/character/EnemyWhite.png")
        self.player = player
        self.force = Vec2(0, 0)

    def update(self) -> None:
        super().update()

        # if utils.Utils.IS_TESTING_PF:

        self.get_dir()
        self.force = self.force.scale(self.speed)
        self.physics_engines[0].apply_force(
            self, (self.force.x, self.force.y))
        return

        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

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


class EnemyRed(Character):
    """EnemyRed class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.health = int(300)
        self.health_max = int(300)
        self.is_walking = True
        self.hit_damage = int(20)
        # self.last_force = Vec2(0, 0)
        self.shoot_range = 200
        self.cd_max = int(90)
        self.bullet = weapon.FireBall
        self.body.texture = arcade.load_texture(
            "graphics/character/EnemyRed.png")
        # self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        # self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player
        self.force = Vec2(0, 0)

    def update(self) -> None:
        super().update()
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        # force = player_pos - current_pos
        # tmp = Vec2(0, 0)
        self.get_dir()

        if current_pos.distance(player_pos) < self.shoot_range:
            self.is_walking = False
            return
        else:
            self.is_walking = True

        self.force = self.force.scale(self.speed)
        self.physics_engines[0].apply_force(
            self, (self.force.x, self.force.y))
        return

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

    def attack(self) -> weapon.FireBall:
        # Enemy red attack property
        bullet_speed = 6
        damage = 30
        aim_pos = Vec2(self.player.center_x - self.center_x,
                       self.player.center_y - self.center_y)
        bullet = self.bullet()
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.speed = bullet_speed
        bullet.aim = aim_pos.normalize().scale(bullet.speed)
        bullet.damage = damage
        bullet.change_x = bullet.aim.x
        bullet.change_y = bullet.aim.y
        return bullet


class EnemyCrack(Character):
    """EnemyCrack class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.speed = 1000
        self.health = int(200)
        self.health_max = int(200)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(40)
        self.body.texture = arcade.load_texture("graphics/character/Crack.png")
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player

    def update(self) -> None:
        super().update()
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

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


class EnemyBigMouth(Character):
    """Enemy Big Mouth class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.health = int(250)
        self.health_max = int(250)
        self.is_walking = True
        self.hit_damage = int(20)
        self.last_force = Vec2(0, 0)
        self.shoot_range = 300
        self.cd_max = int(70)
        self.bullet = weapon.FireBall
        self.body.texture = arcade.load_texture(
            "graphics/character/BigMouth.png")
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player

    def update(self) -> None:
        super().update()
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

        if current_pos.distance(player_pos) < self.shoot_range:
            self.is_walking = False
            return
        else:
            self.is_walking = True

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

    def attack(self) -> arcade.SpriteList():
        bullets = arcade.SpriteList()
        bullet_speed = 7
        damage = 50
        aim_pos = Vec2(self.player.center_x - self.center_x,
                       self.player.center_y - self.center_y)

        bullet_up = self.bullet()
        bullet_up.life_span = int(120)
        bullet_up.center_x = self.center_x
        bullet_up.center_y = self.center_y + 10
        bullet_up.speed = bullet_speed
        bullet_up.damage = damage
        bullet_up.aim = aim_pos.normalize().scale(bullet_up.speed)
        bullet_up.change_x = bullet_up.aim.x
        bullet_up.change_y = bullet_up.aim.y

        bullet_down = self.bullet()
        bullet_down.life_span = int(120)
        bullet_down.center_x = self.center_x
        bullet_down.center_y = self.center_y - 10
        bullet_down.speed = bullet_speed
        bullet_down.damage = damage
        bullet_down.aim = bullet_up.aim.rotate(-0.05)
        bullet_down.change_x = bullet_down.aim.x
        bullet_down.change_y = bullet_down.aim.y

        bullets.append(bullet_up)
        bullets.append(bullet_down)
        return bullets


class EnemyCrash(Character):
    """EnemyCrash class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.speed = 1000
        self.health = int(100)
        self.health_max = int(100)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(80)
        self.body.texture = arcade.load_texture("graphics/character/Crash.png")
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player
        self.cd_max = int(120)
        self.shoot_range = 200
        self.dash_force = Vec2(0, 0)

    def update(self) -> None:
        super().update()
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

        if current_pos.distance(player_pos) < self.shoot_range:
            self.is_walking = False
            return
        else:
            self.is_walking = True

        if self.last_force.distance(force) < 0.1:
            if abs(self.last_force.x - force.x) < 0.1:
                tmp.x = self.l_or_r
            if abs(self.last_force.y - force.y) < 0.1:
                tmp.y = self.u_or_d
            force = tmp.scale(2 * self.speed)  # get rid of the barrier
        else:
            self.last_force = force
            force = force.normalize().scale(self.speed)
            self.dash_force = force

        self.physics_engines[0].apply_force(self, (force.x, force.y))

    def dash(self) -> None:
        force = self.dash_force.scale(2)
        self.physics_engines[0].apply_force(self, (force.x, force.y))


class EnemyTank(Character):
    """EnemyTank class."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        super().__init__(x, y, physics_engine)
        self.speed = 800
        self.health = int(400)
        self.health_max = int(400)
        self.is_walking = True
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(120)
        self.body.texture = arcade.load_texture("graphics/character/Tank.png")
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player
        self.cd_max = int(120)
        self.shoot_range = 200
        self.dash_force = Vec2(0, 0)

    def update(self) -> None:
        super().update()
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

        if current_pos.distance(player_pos) < self.shoot_range:
            self.is_walking = False
            return
        else:
            self.is_walking = True

        if self.last_force.distance(force) < 0.1:
            if abs(self.last_force.x - force.x) < 0.1:
                tmp.x = self.l_or_r
            if abs(self.last_force.y - force.y) < 0.1:
                tmp.y = self.u_or_d
            force = tmp.scale(2 * self.speed)  # get rid of the barrier
        else:
            self.last_force = force
            force = force.normalize().scale(self.speed)
            self.dash_force = force

        self.physics_engines[0].apply_force(self, (force.x, force.y))

    def dash(self) -> None:
        force = self.dash_force.scale(5)
        self.physics_engines[0].apply_force(self, (force.x, force.y))


class BossRed(arcade.Sprite):
    """Simple Red Boss."""

    def __init__(self, x: float = 0, y: float = 0,
                 physics_engine: arcade.PymunkPhysicsEngine = None,
                 player: Player = None) -> None:
        # Properties
        self.health_max = 4200
        self.health = 4200
        self.is_walking = False
        self.speed = 5000
        self.cd = int(0)
        self.cd_max = int(120)
        self.get_damage_len = int(0)  # draw get damage effect

        # Init position
        self.pos = Vec2(x, y)

        # Relative positions for visuals
        self.body_pos = Vec2(0, 0)  # controls the actual movement
        self.foot_l_pos = Vec2(-16, -32)
        self.foot_r_pos = Vec2(16, -32)
        self.collider_pos = Vec2(0, -6)

        # Init collider and physics engine
        super().__init__(
            "graphics/character/BossCollider.png",
            center_x=self.pos.x + self.collider_pos.x,
            center_y=self.pos.y + self.collider_pos.y,
            image_width=40,
            image_height=60,
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
        self.body = arcade.Sprite(filename="graphics/character/BossRedBody.png",
                                  image_width=40,
                                  image_height=52)
        # Feet sprite
        self.foot_l = arcade.Sprite(
            filename="graphics/character/BossFoot.png",
            center_x=self.foot_l_pos.x + self.pos.x,
            center_y=self.foot_l_pos.y + self.pos.x,
            image_width=10,
            image_height=10,
            scale=1,
        )
        self.foot_r = arcade.Sprite(
            filename="graphics/character/BossFoot.png",
            center_x=self.foot_r_pos.x + self.pos.x,
            center_y=self.foot_r_pos.y + self.pos.x,
            image_width=10,
            image_height=10,
            scale=1,
        )

        # Get damage sprite
        self.damage_sprite = arcade.SpriteSolidColor(40, 52,
                                                     utils.Color.WHITE)
        self.damage_sprite.alpha = 0

        # Body parts list for rendering
        self.parts = arcade.SpriteList()
        self.parts.append(self.body)
        self.parts.append(self.foot_l)
        self.parts.append(self.foot_r)
        self.parts.append(self.damage_sprite)

        # Set up
        self.bullet = weapon.FireBall
        self.last_force = Vec2(0, 0)
        self.hit_damage = int(250)
        self.l_or_r = 1 if bool(random.getrandbits(1)) else -1
        self.u_or_d = 1 if bool(random.getrandbits(1)) else -1
        self.player = player
        self.direction = Vec2(0, 0)
        self.is_set_dir = False
        self.shoot_range = 400
        self.dash_force = Vec2(0, 0)
        self.cnt = 0

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

        self.damage_sprite.center_x = self.body.center_x
        self.damage_sprite.center_y = self.body.center_y

        # Body animation
        if self.body_move_frames == 0:  # reset frames
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up

        self.body_move_frames -= 1
        self.body.center_y += BODY_ANIM[self.body_move_frames] * 2

        self.get_damage_len -= 1

        # Feet animation
        if self.walking_frames == 0:  # reset frames
            self.walking_frames = self.walking_frames_max

        self.walking_frames -= 1

        if self.is_walking:
            self.foot_l.center_x += L_WALK_X[self.walking_frames] * 2
            self.foot_l.center_y += L_WALK_Y[self.walking_frames] * 2
            self.foot_r.center_x += R_WALK_X[self.walking_frames] * 2
            self.foot_r.center_y += R_WALK_Y[self.walking_frames] * 2
        else:
            # reset the walking animation
            self.foot_l.center_x = self.foot_l_pos.x + self.pos.x
            self.foot_l.center_y = self.foot_l_pos.y + self.pos.y
            self.foot_r.center_x = self.foot_r_pos.x + self.pos.x
            self.foot_r.center_y = self.foot_r_pos.y + self.pos.y
            self.walking_frames = self.walking_frames_max

        if self.get_damage_len > 0:
            self.damage_sprite.alpha = 150
        else:
            self.damage_sprite.alpha = 0

    def update(self) -> None:
        self.move()

        self.cnt += 1
        current_pos = Vec2(self.center_x, self.center_y)
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        force = player_pos - current_pos
        tmp = Vec2(0, 0)

        if self.health > 2100:  # phase 1
            if current_pos.distance(player_pos) < self.shoot_range:
                self.is_walking = False
                return
            else:
                self.is_walking = True

            if self.last_force.distance(force) < 0.1:
                if abs(self.last_force.x - force.x) < 0.1:
                    tmp.x = self.l_or_r
                if abs(self.last_force.y - force.y) < 0.1:
                    tmp.y = self.u_or_d
                force = tmp.scale(2 * self.speed)  # get rid of the barrier
            else:
                self.last_force = force
                force = force.normalize().scale(self.speed)
                self.dash_force = force
        else:  # phase 2
            self.cd_max = 90
            self.is_walking = True
            if self.cnt % 250 == 0:
                self.is_set_dir = False

            dis = current_pos.distance(player_pos)

            if self.is_set_dir == False:
                if dis <= self.shoot_range / 4.0:
                    self.direction = - \
                        force.rotate(float(random.randrange(0, 45)))
                    self.direction = self.direction.normalize()
                    self.is_set_dir = True

            if dis > self.shoot_range:
                self.direction = force.normalize()

            if self.last_force.distance(force) < 0.1:
                # Rest direction if stuck somewhere
                four_dir = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]
                self.direction = four_dir[self.cd % 4]
                self.is_set_dir = True

            self.last_force = force
            force = self.direction.scale(self.speed)

        self.physics_engines[0].apply_force(self, (force.x, force.y))

    def dash(self) -> None:
        # Dash
        force = self.dash_force.scale(5)
        self.physics_engines[0].apply_force(self, (force.x, force.y))

    def shoot_ring(self) -> arcade.SpriteList():
        # Shoot
        bullets = arcade.SpriteList()
        bullet_speed = 5
        damage = 50
        life_span = 90
        aim = Vec2(1, 0)
        for i in range(0, 10):
            bullet = self.bullet()
            bullet.life_span = life_span
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.aim = aim.rotate(i * 0.628).scale(bullet_speed)
            bullet.speed = bullet_speed
            bullet.damage = damage
            bullet.change_x = bullet.aim.x
            bullet.change_y = bullet.aim.y
            bullets.append(bullet)
        return bullets

    def shoot_around(self, width: int, height: int) -> arcade.SpriteList():
        bullets = arcade.SpriteList()
        for i in range(0, 100):
            if i == 0:
                pos_x = self.player.pos.x
                pos_y = self.player.pos.y
            else:
                pos_x = random.randrange(max(int(self.player.center_x - 300), 30),
                                         min(int(self.player.center_x + 300), width - 30))
                pos_y = random.randrange(max(int(self.player.center_y - 300), 30),
                                         min(int(self.player.center_y + 300), height - 30))
            bullet = weapon.BossFireBall(pos_x, pos_y)
            bullet.damage = 200
            bullet.life_span = 90
            bullets.append(bullet)
        return bullets
