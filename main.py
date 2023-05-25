import random
import arcade
from pyglet.math import Vec2

''' GLOBAL VARIABLE '''
# Color palette
GROUND_WHITE = (240, 237, 212)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (183, 4, 4)
LIGHT_GRAY = (207, 210, 207)
DARK_GRAY = (67, 66, 66)
LIGHT_BLACK = (34, 34, 34)

# Screen size
SCREEN_WIDTH = int(1280)
SCREEN_HEIGHT = int(720)

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.6

# Animations
BODY_ANIM = [-1,-1,-1,-1,-1,-1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              1, 1, 1, 1, 1, 1,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
BODY_WALK = [ 1, 1, 1,-1,-1,-1, 1, 1, 1,-1,-1,-1]
L_WALK_X  = [-1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1]
L_WALK_Y  = [ 1, 1, 1,-1,-1,-1, 1, 1, 1,-1,-1,-1]
R_WALK_X  = [ 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1, 1]
R_WALK_Y  = [ 1, 1, 1,-1,-1,-1, 1, 1, 1,-1,-1,-1]

class GameObject:
    ''' GameObject Base Class. '''

    def __init__(self):
        self.pos = Vec2(0, 0)

    # update the GameObject logic
    def update(self):
        pass

    # render the GameObject
    def draw(self):
        pass

class FixedWall(GameObject):
    ''' Fixed wall for background in the room. '''

    def __init__(self, x = 0, y = 0):
        self.pos = Vec2(x, y)
        self.grid_idx = (0, 0)
        self.len = 30

        # Wall
        self.sprite = arcade.Sprite(filename = "./graphics/FixedWall1.png",
                                    center_x = self.pos.x,
                                    center_y = self.pos.y,
                                    image_width = 30,
                                    image_height = 30)

    def draw(self):
        self.sprite.draw()

class Room:
    ''' Room as a background in the game scene. '''

    def __init__(self, width = 1500, height = 900):
        self.width = width
        self.height = height
        self.pos = Vec2(self.width / 2, self.height / 2)
        self.walls = [FixedWall(50, 50),
                      FixedWall(50, 100),
                      FixedWall(100, 100)]
        for i in range(0, 50):
            self.walls.append(FixedWall(15 + i * 30, 15))
        
    def draw(self):
        # Room background
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y,
                                     self.width, self.height, GROUND_WHITE)
        # Walls
        for wall in self.walls:
            wall.draw()

class Character(GameObject):
    ''' Character base class. '''

    def __init__(self, x = 0, y = 0):
        # Perporties
        self.is_walking = False
        self.speed = 3

        # Init position
        self.pos = Vec2(x, y)

        # Relative positions for visuals
        self.body_pos = Vec2(0, 0) # controls the actual movement
        self.foot_l_pos = Vec2(-8, -16)
        self.foot_r_pos = Vec2(8, -16)
        self.collider_pos = Vec2(0, -3)

        # Track the player movement input
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

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
        self.foot_l = arcade.Sprite(filename = "./graphics/Foot.png",
                                    center_x = self.foot_l_pos.x + self.pos.x,
                                    center_y = self.foot_l_pos.y + self.pos.x,
                                    image_width = 4,
                                    image_height = 4,
                                    scale = 1)
        self.foot_r = arcade.Sprite(filename = "./graphics/Foot.png",
                                    center_x = self.foot_r_pos.x + self.pos.x,
                                    center_y = self.foot_r_pos.y + self.pos.x,
                                    image_width = 4,
                                    image_height = 4,
                                    scale = 1)
        # Collider sprite for physics
        self.box_collider = arcade.SpriteSolidColor(20, 30, DARK_GRAY)
        self.box_collider.center_x = self.pos.x + self.collider_pos.x
        self.box_collider.center_y = self.pos.y + self.collider_pos.y

    def move(self):

        if self.box_collider.change_x != 0 or self.box_collider.change_y != 0:
            self.is_walking = True
        else:
            self.is_walking = False

        self.pos.x = self.box_collider.center_x - self.collider_pos.x
        self.pos.y = self.box_collider.center_y - self.collider_pos.y

        self.body.center_x = self.pos.x + self.body_pos.x
        self.body.center_y = self.pos.y + self.body_pos.y

        self.foot_l.center_x = self.pos.x + self.foot_l_pos.x
        self.foot_l.center_y = self.pos.y + self.foot_l_pos.y
        self.foot_r.center_x = self.pos.x + self.foot_r_pos.x
        self.foot_r.center_y = self.pos.y + self.foot_r_pos.y

    def update(self):
        self.move()

        # Body animation
        if self.body_move_frames == 0: # reset frames
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up

        self.body_move_frames -= 1
        self.body.center_y += BODY_ANIM[self.body_move_frames]

        # Feet animation
        if self.walking_frames == 0: # reset frames
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

    def draw(self):
        # self.box_collider.draw()
        self.body.draw()
        self.foot_l.draw()
        self.foot_r.draw()

class Player(Character):
    ''' Player game object. '''

    def __init__(self, x, y):
        super().__init__(x, y)

        # Player body sprite
        self.body = arcade.Sprite(filename = "./graphics/Player.png",
                                    center_x = self.body_pos.x + self.pos.x,
                                    center_y = self.body_pos.y + self.pos.x,
                                    image_width = 20,
                                    image_height = 24,
                                    scale = 1)

    def move(self):
        self.box_collider.change_x = 0
        self.box_collider.change_y = 0

        if self.move_up and not self.move_down:
            self.box_collider.change_y = self.speed
        elif self.move_down and not self.move_up:
            self.box_collider.change_y = -self.speed
        if self.move_left and not self.move_right:
            self.box_collider.change_x = -self.speed
        elif self.move_right and not self.move_left:
            self.box_collider.change_x = self.speed

        super().move()

class EnemyWhite(Character):
    ''' EnemyWhite class. '''

    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)

        # EnemyWhite body sprite
        self.body = arcade.Sprite(filename = "./graphics/EnemyWhite.png",
                                    center_x = self.body_pos.x + self.pos.x,
                                    center_y = self.body_pos.y + self.pos.x,
                                    image_width = 20,
                                    image_height = 24,
                                    scale = 1)

class EnemyRed(Character):
    ''' EnemyRed class. '''

    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)

        # EnemyRed body sprite
        self.body = arcade.Sprite(filename = "./graphics/EnemyRed.png",
                                    center_x = self.body_pos.x + self.pos.x,
                                    center_y = self.body_pos.y + self.pos.x,
                                    image_width = 20,
                                    image_height = 26,
                                    scale = 1)

class BoxHead(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """Initializer"""
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.wall_list = None

        # set up the player
        self.player_sprite = None

        # set up the enemy
        self.enemy_list = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

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
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.room_list = []

        # setup room background and player
        self.game_room = Room()
        for wall in self.game_room.walls:
            self.wall_list.append(wall.sprite)

        # set up the player
        self.player = Player(float(SCREEN_WIDTH / 2), float(SCREEN_HEIGHT / 2))

        self.physics_engine = arcade.PhysicsEngineSimple(self.player.box_collider, self.wall_list)

        self.enemy_test_1 = EnemyRed(200, 300)
        self.enemy_test_2 = EnemyWhite(200, 400)

        # set the most basic background color
        arcade.set_background_color(BLACK)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        # self.wall_list.draw()
        self.game_room.draw()
        self.player.draw()

        self.enemy_test_1.draw()
        self.enemy_test_2.draw()


        # Select the (unscrolled) camera for our GUI
        # self.camera_gui.use()

        # Render the GUI
        # arcade.draw_rectangle_filled(self.width // 2,
        #                              20,
        #                              self.width,
        #                              40,
        #                              arcade.color.ALMOND)
        # text = f"Scroll value: ({self.camera_sprites.position[0]:5.1f}, " \
        #        f"{self.camera_sprites.position[1]:5.1f})"
        # arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W:
            self.player.move_up = True
        elif key == arcade.key.S:
            self.player.move_down = True
        elif key == arcade.key.A:
            self.player.move_left = True
        elif key == arcade.key.D:
            self.player.move_right = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.W:
            self.player.move_up = False
        elif key == arcade.key.S:
            self.player.move_down = False
        elif key == arcade.key.A:
            self.player.move_left = False
        elif key == arcade.key.D:
            self.player.move_right = False

    def on_update(self, delta_time):
        self.player.update()
        self.enemy_test_1.update()
        self.enemy_test_2.update()

        # Scroll the screen to the player
        self.scroll_to_player()

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.

        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        position = Vec2(self.camera_sprites.position.x, self.camera_sprites.position.y)
        # limit the camera position within the room
        if self.player.pos.x > SCREEN_WIDTH / 2 - 15 \
            and self.game_room.width - self.player.pos.x > SCREEN_WIDTH / 2:
            position.x = self.player.pos.x - SCREEN_WIDTH / 2
        if self.player.pos.y > SCREEN_HEIGHT / 2 - 15 \
            and self.game_room.height - self.player.pos.y > SCREEN_HEIGHT / 2:
            position.y = self.player.pos.y - SCREEN_HEIGHT / 2

        self.camera_sprites.move_to(position, CAMERA_SPEED)

def main():
    """ Main function """
    window = BoxHead(SCREEN_WIDTH, SCREEN_HEIGHT, "BoxHead 2D")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
