import random
import arcade
from pyglet.math import Vec2

''' GLOBAL VARIABLE '''
# Color palette
GROUND_WHITE = (221, 230, 237)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (183, 4, 4)
LIGHT_GRAY = (207, 210, 207)
DARK_GRAY = (67, 66, 66)
LIGHT_BLACK = (34, 34, 34)

# Screen size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

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

        # wall collider
        self.sprite = arcade.Sprite(filename = None,
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
        # room background
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y,
                                     self.width, self.height, GROUND_WHITE)
        # walls
        for wall in self.walls:
            wall.draw()

class Player(GameObject):
    ''' Player game object. '''
    def __init__(self, x = 0, y = 0):
        # Perporties
        self.is_walking = False
        self.speed = 3
        # init position
    #     self.pos = pygame.Vector2(x, y)

    #     # Animation init
    #     self.walking_in = True  # feet move inside
    #     self.walking_frames_max = 6
    #     self.walking_frames = self.walking_frames_max
    #     self.foot_flag = True # change walking foot
    #     self.foot_flag_frames = 2 * self.walking_frames_max
    #     self.body_move_up = False
    #     self.body_move_frames_max = 20
    #     self.body_move_frames = self.body_move_frames_max
    #     self.velocity = pygame.Vector2(0, 0)

    #     # Visuals
    #     # body Rect
    #     self.body = pygame.Rect(self.pos.x, self.pos.y, 28, 24)
    #     # feet Rect
    #     self.foot_l = pygame.Rect(self.pos.x, self.pos.y + 26, 6, 4)
    #     self.foot_r = pygame.Rect(self.pos.x + 22, self.pos.y + 26, 6, 4)

    # def changeDir(self, x, y):
    #     self.velocity.x += x * self.speed
    #     self.velocity.y += y * self.speed
    #     if self.velocity.x != 0 or self.velocity.y != 0:
    #         self.is_walking = True
    #         self.velocity.normalize()
    #     else:
    #         self.is_walking = False

    # def move(self):
    #     self.pos.x += self.velocity.x
    #     self.pos.y += self.velocity.y

    #     # update visual
    #     self.body.topleft += self.velocity
    #     self.foot_l.topleft += self.velocity
    #     self.foot_r.topleft += self.velocity

    # def update(self):
    #     # player move
    #     self.move()

    #     # body animation
    #     if self.body_move_up:
    #         if self.body_move_frames < 4:
    #             self.body.y += 1
    #         self.body_move_frames -= 1
    #     else:
    #         if self.body_move_frames < 4:
    #             self.body.y -= 1
    #         self.body_move_frames -= 1

    #     if self.body_move_frames == 0:
    #         self.body_move_frames = self.body_move_frames_max
    #         self.body_move_up = not self.body_move_up

    #     # feet animation
    #     if self.is_walking:
    #         if self.walking_in:
    #             if self.walking_frames < 3:
    #                 if self.foot_flag:
    #                     self.foot_l.x += 2
    #                     self.foot_l.y -= 1
    #                 else:
    #                     self.foot_r.x -= 2
    #                     self.foot_r.y -= 1
    #         else:
    #             if self.walking_frames < 3:
    #                 if self.foot_flag:
    #                     self.foot_l.x -= 2
    #                     self.foot_l.y += 1
    #                 else:
    #                     self.foot_r.x += 2
    #                     self.foot_r.y += 1
    #         self.walking_frames -= 1
    #         self.foot_flag_frames -= 1
    #     else:
    #         # reset the walking animation
    #         self.foot_l.topleft = (self.pos.x, self.pos.y + 26)
    #         self.foot_r.topleft = (self.pos.x + 22, self.pos.y + 26)
    #         self.walking_frames = self.walking_frames_max
    #         self.walking_in = True
    #         self.foot_flag_frames = 2 * self.walking_frames_max
    #         self.foot_flag = not self.foot_flag

    #     if self.walking_frames == 0:
    #         self.walking_frames = self.walking_frames_max
    #         self.walking_in = not self.walking_in
    #     if self.foot_flag_frames == 0:
    #         self.foot_flag_frames = 2 * self.walking_frames_max
    #         self.foot_flag = not self.foot_flag

    # def draw(self, screen):
    #     pygame.draw.rect(screen, BLACK, player.body, 0)
    #     pygame.draw.rect(screen, BLACK, player.foot_r, 0)
    #     pygame.draw.rect(screen, BLACK, player.foot_l, 0)



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
        self.test_room = Room()

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

        # self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        arcade.set_background_color(BLACK)

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()


        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        self.player_list.draw()
        self.test_room.draw()
        # self.wall_list.draw() TODO: test whether collision detection will still be valid


        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()

        # Render the GUI
        # arcade.draw_rectangle_filled(self.width // 2,
        #                              20,
        #                              self.width,
        #                              40,
        #                              arcade.color.ALMOND)
        # text = f"Scroll value: ({self.camera_sprites.position[0]:5.1f}, " \
        #        f"{self.camera_sprites.position[1]:5.1f})"
        # arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)

    def on_update(self, delta_time):
        pass

def main():
    """ Main function """
    window = BoxHead(SCREEN_WIDTH, SCREEN_HEIGHT, "BoxHead 2D")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()