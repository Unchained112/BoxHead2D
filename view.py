import arcade
import arcade.gui
import utils
import room
import character
from pyglet.math import Vec2
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

FADE_RATE = 8
CAMERA_SPEED = 0.6


class FadingView(arcade.View):
    """Fading transition between two views."""

    def __init__(self) -> None:
        super().__init__()
        self.fade_out = None
        self.fade_in = 255
        self.w, self.h = self.window.get_size()
        self.next_view = None

    def update_fade(self) -> None:
        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if (self.fade_out is not None and self.fade_out > 255 and
                    self.next_view is not None):
                view = self.next_view()
                view.setup()
                self.window.show_view(view)

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


class DefaultView(FadingView):
    """Default view displayed when game starts."""

    def setup(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.w, self.h = self.window.get_size()
        self.title = arcade.Sprite(filename="graphics/Title.png",
                                   scale=2,
                                   center_x=self.w / 2,
                                   center_y=self.h/2 - 20)
        self.text_alpha = 250
        self.text_fading = -5  # must be divisible by 250
        self.title_text = arcade.Text("Press any key to proceed...",
                                      self.w / 2, self.h/2 - 80,
                                      color=(0, 0, 0, 250),
                                      font_size=16, font_name="FFF Forward",
                                      anchor_x="center")

    def on_update(self, delta_time: float) -> None:
        self.update_fade()

        self.text_alpha += self.text_fading
        if self.text_alpha == 10 or self.text_alpha == 250:
            self.text_fading = -self.text_fading
        self.text_alpha %= 255
        self.title_text.color = (0, 0, 0, self.text_alpha)

    def on_draw(self) -> None:
        self.clear()
        self.title_text.draw()
        self.title.draw()
        self.draw_fading()

    def on_mouse_press(self, _x, _y, _button, _modifiers) -> None:
        self.next_view = StartView
        # NOTE: Always set the next view before set fade_out to 0
        if self.fade_out is None:
            self.fade_out = 0

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.next_view = StartView
        if self.fade_out is None:
            self.fade_out = 0


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
        self.character_sprites = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

        # track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.camera_sprites = arcade.Camera(self.w, self.h)

    def setup(self) -> None:
        # Create the physics engine
        damping = 0.01
        gravity = (0, 0)
        self.physics_engine = PymunkPhysicsEngine(damping=damping,
                                                  gravity=gravity)

        # GameObject lists
        self.player_bullet_list = arcade.SpriteList()

        # Set up room background and player
        self.room = room.StartRoom()

        # Set up the player
        self.player = character.Player(float(self.w / 2) - 80,
                                       float(self.h / 2) - 80,
                                       self.physics_engine)
        self.character_sprites = arcade.SpriteList()
        self.character_sprites.extend(self.player.parts)

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
        self.physics_engine.add_sprite_list(self.room.walls,
                                            friction=0,
                                            collision_type="wall",
                                            body_type=PymunkPhysicsEngine.STATIC)

        # Add insturctions
        self.start_sprite_list = arcade.SpriteList()
        self.start_sprite_list.append(
            arcade.Sprite(filename="graphics/MoveGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=200)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="graphics/ShootGuide.png",
                          scale=0.3,
                          center_x=self.w - 200,
                          center_y=200)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="graphics/PauseGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=self.h - 100)
        )
        self.start_sprite_list.append(
            arcade.Sprite(filename="graphics/WeaponChangeGuide.png",
                          scale=0.3,
                          center_x=200,
                          center_y=self.h - 200)
        )

        # Add UI elements
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.vertical_box = arcade.gui.UIBoxLayout(x=200)
        title = arcade.Sprite(filename="graphics/Title.png", scale=2)
        title_ui = arcade.gui.UISpriteWidget(
            sprite=title, width=400, height=300)
        self.vertical_box.add(title_ui.with_space_around(bottom=0))
        ui_flatbutton = arcade.gui.UIFlatButton(text="Flat Button",
                                                width=150,
                                                style=utils.Style.BUTTON_DEFAULT)
        self.vertical_box.add(ui_flatbutton.with_space_around(bottom=20))
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.vertical_box)
        )

    def on_draw(self) -> None:
        self.clear()
        self.camera_sprites.use()

        self.room.draw_ground()
        self.room.draw_walls()
        self.start_sprite_list.draw()
        self.character_sprites.draw()
        self.player.draw()
        self.player_bullet_list.draw()
        self.manager.draw()

    def on_update(self, delta_time: float) -> None:
        self.update_fade()

        self.physics_engine.step()
        self.player.update()

        self.scroll_to_player()

    def on_key_press(self, key, modifiers) -> None:
        """Called whenever a key is pressed."""

        if key == arcade.key.W:
            self.player.move_up = True
        elif key == arcade.key.S:
            self.player.move_down = True
        elif key == arcade.key.A:
            self.player.move_left = True
        elif key == arcade.key.D:
            self.player.move_right = True

    def on_key_release(self, key, modifiers) -> None:
        """Called when the user releases a key."""

        if key == arcade.key.W:
            self.player.move_up = False
        elif key == arcade.key.S:
            self.player.move_down = False
        elif key == arcade.key.A:
            self.player.move_left = False
        elif key == arcade.key.D:
            self.player.move_right = False

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        """Mouse movement."""

        self.mouse_x = x
        self.mouse_y = y
        self.mouse_pos.x = self.mouse_x + self.camera_sprites.position.x
        self.mouse_pos.y = self.mouse_y + self.camera_sprites.position.y
        self.mouse_sprite.center_x = self.mouse_x
        self.mouse_sprite.center_y = self.mouse_y
        self.player.aim(self.mouse_pos)

    def scroll_to_player(self) -> None:
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        position = Vec2(self.camera_sprites.position.x,
                        self.camera_sprites.position.y)
        # limit the camera position within the room
        if (self.player.pos.x > float(self.w / 2) - 5
                and self.room.width - self.player.pos.x > float(self.w / 2) - 5):
            position.x = self.player.pos.x - float(self.w / 2)
        if (self.player.pos.y > float(self.h / 2) - 5
                and self.room.height - self.player.pos.y > float(self.h / 2) - 5):
            position.y = self.player.pos.y - float(self.h / 2)

        self.camera_sprites.move_to(position, CAMERA_SPEED)


class SelectionView(FadingView):
    """Character and map selection."""


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
