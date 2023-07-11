import arcade
import utils
import room
import character
from pyglet.math import Vec2
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

FADE_RATE = 5


class DefaultView(arcade.View):
    """Default view displayed when game starts."""

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.w, self.h = self.window.get_size()
        self.title = arcade.Sprite(filename="graphics/Title.png",
                                   scale=2,
                                   center_x=self.w / 2,
                                   center_y=self.h/2 - 20)

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text("Press any key to proceed...", self.w / 2,
                         self.h/2 - 80, utils.Color.BLACK,
                         font_size=24, font_name="Kenney Future",
                         anchor_x="center")
        self.title.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers) -> None:
        start = StartView()
        start.setup()
        self.window.show_view(start)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        start = StartView()
        start.setup()
        self.window.show_view(start)


class FadingView(arcade.View):
    """Fading transiton between two views."""

    def __init__(self) -> None:
        super().__init__()
        self.fade_out = None
        self.fade_in = 255
        self.w, self.h = self.window.get_size()

    def update_fade(self, next_view: arcade.View =None) -> None:
        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if self.fade_out is not None and self.fade_out > 255 and next_view is not None:
                game_view = next_view()
                game_view.setup()
                self.window.show_view(game_view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self) -> None:
        if self.fade_out is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_out))

        if self.fade_in is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_in))


class StartView(FadingView):
    """Start menu."""

    def __init__(self) -> None:
        super().__init__()
        self.mouse_x = None
        self.mouse_y = None
        self.mouse_pos = Vec2(0, 0)
        self.mouse_sprite = arcade.Sprite("graphics/Cursor.png")

        # Sprite lists
        self.wall_list = None
        self.player = None
        self.player_bullet_list = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

        # track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Create the cameras. One for the GUI, one for the sprites.
        # scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.Camera(self.w, self.h)
        self.camera_gui = arcade.Camera(self.w, self.h)

    def setup(self) -> None:
        # Create the physics engine
        damping = 0.01
        gravity = (0, 0)
        self.physics_engine = PymunkPhysicsEngine(damping=damping,
                                                  gravity=gravity)
    
        # GameObject lists
        self.wall_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.player_object_list = arcade.SpriteList()

        # Set up room background and player
        self.room = room.StartRoom()
        for wall in self.room.walls:
            self.wall_list.append(wall)

        # Set up the player
        self.player = character.Player(float(self.w / 2), 
                                       float(self.h / 2), 
                                       self.physics_engine)

        # Set the most basic background color
        arcade.set_background_color(utils.Color.BLACK)

        # Add the player
        self.physics_engine.add_sprite(self.player,
                                       friction=0,
                                       moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
                                       damping=0.001,
                                       collision_type="player",
                                       elasticity=0.1,
                                       max_velocity=400)

        # Create the walls
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=0,
                                            collision_type="wall",
                                            body_type=PymunkPhysicsEngine.STATIC)

    def on_update(self, dt):
        self.update_fade(next_view=GameView)


class OptionView(FadingView):
    """Optional menu."""

    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def on_update(self, dt):
        self.update_fade(next_view=GameView)


class GameView(FadingView):
    """Main game view."""

    def __init__(self):
        super().__init__()
