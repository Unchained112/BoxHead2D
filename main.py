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
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.6

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
    ''' Fixed wall for background in the room scene. '''

    def __init__(self, x = 0, y = 0):
        self.pos = Vec2(x, y)
        self.grid_idx = (0, 0)
        self.len = 30

        # Wall collider
        self.sprite = arcade.Sprite(filename = ":resources:images/tiles/boxCrate_double.png",
                                    center_x = self.pos.x,
                                    center_y = self.pos.y,
                                    image_width = 30,
                                    image_height = 30)

    def draw(self):
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y,
                                     self.len, self.len, DARK_GRAY)

class Room:
    ''' Room as a background in the game scene. '''

    def __init__(self, width = 1500, height = 900):
        self.pos = Vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.width = width
        self.height = height
        self.walls = [FixedWall(50, 50),
                      FixedWall(50, 100),
                      FixedWall(100, 100)]

    def draw(self):
        # Room background
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y,
                                     self.width, self.height, GROUND_WHITE)
        # Walls
        for wall in self.walls:
            wall.draw()

class Player(GameObject):
    ''' Player game object. '''
    def __init__(self, x = 0, y = 0):
        # Perporties
        self.is_walking = False
        self.speed = 3

        # init position
        self.pos = Vec2(x, y)

        # Animation init
        self.body_move_up = False
        self.body_move_frames_max = 20
        self.body_move_frames = self.body_move_frames_max
        self.walking_frames_max = 12
        self.walking_frames = self.walking_frames_max
        self.velocity = Vec2(0, 0)

        # Visuals
        # Body Rect: [x, y, w, h]
        self.body = [self.pos.x, self.pos.y, 20, 24]
        # Feet Rect: [x, y, w, h]
        self.foot_l = [self.pos.x - 8, self.pos.y - 18, 4, 4]
        self.foot_r = [self.pos.x + 8, self.pos.y - 18, 4, 4]
        # Feet walk animation
        self.l_walk_x = [-1,-1,-1, 1, 1, 1, 1, 1, 1,-1,-1,-1]
        self.l_walk_y = [-1,-1,-1, 1, 1, 1,-1,-1,-1, 1, 1, 1]
        self.r_walk_x = [ 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1, 1]
        self.r_walk_y = [-1,-1,-1, 1, 1, 1,-1,-1,-1, 1, 1, 1]

        # Body Collider
        self.sprite = arcade.Sprite(filename = ":resources:images/tiles/boxCrate_double.png",
                                    center_x = self.pos.x,
                                    center_y = self.pos.y,
                                    image_width = 20,
                                    image_height = 26)

    def changeDir(self, x, y):
        self.velocity.x += x * self.speed
        self.velocity.y += y * self.speed
        if self.velocity.x != 0 or self.velocity.y != 0:
            self.is_walking = True
            self.velocity.normalize()
        else:
            self.is_walking = False

    def move(self):
        self.sprite.center_x += self.velocity.x
        self.sprite.center_y += self.velocity.y
        
        # update collider
        self.pos.x = self.sprite.center_x
        self.pos.y = self.sprite.center_y

        # self.sprite.center_x = self.pos.x
        # self.sprite.center_y = self.pos.y

        # update visual
        self.body[0] = self.sprite.center_x
        self.body[1] = self.sprite.center_y
        self.foot_l[0] += self.velocity.x
        self.foot_l[1] += self.velocity.y
        self.foot_r[0] += self.velocity.x
        self.foot_r[1] += self.velocity.y

    def update(self):
        self.move()

        # Body animation
        if self.body_move_frames == 0: # reset frames
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up
            self.body[0] = self.sprite.center_x
            self.body[1] = self.sprite.center_y

        self.body_move_frames -= 1

        if self.body_move_up:
            if self.body_move_frames < 3:
                self.body[1] += 0.5
        else:
            if self.body_move_frames < 3:
                self.body[1] -= 0.5

        # feet animation
        if self.walking_frames == 0: # reset frames
            self.walking_frames = self.walking_frames_max

        self.walking_frames -= 1

        if self.is_walking:
            self.foot_l[0] += self.l_walk_x[self.walking_frames]
            self.foot_l[1] += self.l_walk_y[self.walking_frames]
            self.foot_r[0] += self.r_walk_x[self.walking_frames]
            self.foot_r[1] += self.r_walk_y[self.walking_frames]
        else:
            # reset the walking animation
            self.foot_l[0] += self.velocity.x
            self.foot_l[1] += self.velocity.y
            self.foot_r[0] += self.velocity.x
            self.foot_r[1] += self.velocity.y
            self.walking_frames = self.walking_frames_max

    def draw(self):
        arcade.draw_rectangle_filled(self.body[0], self.body[1],
                                     self.body[2], self.body[3], BLACK)
        arcade.draw_rectangle_filled(self.foot_l[0], self.foot_l[1],
                                     self.foot_l[2], self.foot_l[3], BLACK)
        arcade.draw_rectangle_filled(self.foot_r[0], self.foot_r[1],
                                     self.foot_r[2], self.foot_r[3], BLACK)


class BoxHead(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """Initializer"""
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.player_list = None
        self.wall_list = None

        # Set up the player
        self.player_sprite = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

        # Track the current state of what key is pressed
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
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # setup room background and player
        self.test_room = Room()
        for wall in self.test_room.walls:
            self.wall_list.append(wall.sprite)

        self.player = Player()
        self.player_list.append(self.player.sprite)     

        # Set up the player
        # self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
        #                                    scale=0.4)
        # self.player_sprite.center_x = 256
        # self.player_sprite.center_y = 512
        # self.player_list.append(self.player_sprite)

        # -- Set up several columns of walls
        # for x in range(200, 1650, 210):
        #     for y in range(0, 1600, 64):
        #         # Randomly skip a box so the player can find a way through
        #         if random.randrange(5) > 0:
        #             wall = arcade.Sprite(":resources:images/tiles/grassCenter.png", SPRITE_SCALING)
        #             wall.center_x = x
        #             wall.center_y = y
        #             self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player.sprite, self.wall_list)

        # set the most basic background color
        arcade.set_background_color(LIGHT_BLACK)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw() # TODO: test whether collision detection will still be valid
        self.test_room.draw()
        for wall in self.wall_list:
            wall.draw_hit_box()
        self.player.draw()
        self.player.sprite.draw_hit_box(DARK_RED)

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
            self.player.changeDir(0, 1)
        elif key == arcade.key.S:
            self.player.changeDir(0, -1)
        elif key == arcade.key.A:
            self.player.changeDir(-1, 0)
        elif key == arcade.key.D:
            self.player.changeDir(1, 0)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.W:
            self.player.changeDir(0, -1)
        elif key == arcade.key.S:
            self.player.changeDir(0, 1)
        elif key == arcade.key.A:
            self.player.changeDir(1, 0)
        elif key == arcade.key.D:
            self.player.changeDir(-1, 0)

    def on_update(self, delta_time):
        self.player.update()

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

        position = Vec2(self.player.pos.x - SCREEN_WIDTH / 2,
                        self.player.pos.y - SCREEN_HEIGHT / 2)

        self.camera_sprites.move_to(position, CAMERA_SPEED)

def main():
    """ Main function """
    window = BoxHead(SCREEN_WIDTH, SCREEN_HEIGHT, "BoxHead 2D")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
