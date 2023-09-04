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
            if (
                self.fade_out is not None
                and self.fade_out > 255
                and self.next_view is not None
            ):
                view = self.next_view()
                view.setup()
                self.window.show_view(view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self) -> None:
        if self.fade_out is not None:
            arcade.draw_rectangle_filled(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height,
                (0, 0, 0, self.fade_out),
            )

        if self.fade_in is not None:
            arcade.draw_rectangle_filled(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height,
                (0, 0, 0, self.fade_in),
            )


class DefaultView(FadingView):
    """Default view displayed when game starts."""

    def setup(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.w, self.h = self.window.get_size()
        self.title = arcade.Sprite(
            filename="graphics/Title.png",
            scale=2,
            center_x=self.w / 2,
            center_y=self.h / 2 - 20,
        )
        self.text_alpha = 250
        self.text_fading = -5  # must be divisible by 250
        self.title_text = arcade.Text(
            "Press any key to proceed...",
            self.w / 2,
            self.h / 2 - 80,
            color=(0, 0, 0, 250),
            font_size=16,
            font_name="FFF Forward",
            anchor_x="center",
        )

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
        self.physics_engine = PymunkPhysicsEngine(
            damping=damping, gravity=gravity)

        # GameObject lists
        self.player_bullet_list = arcade.SpriteList()

        # Set up room background and player
        room_w = utils.Utils.round_to_multiple(self.w, 30)
        room_h = utils.Utils.round_to_multiple(self.h, 30)
        self.room = room.StartRoom(room_w, room_h)
        self.wall_list = self.room.walls

        # Set up the player
        self.player = character.Player(
            float(self.w / 2), float(self.h / 2) + 20, self.physics_engine
        )
        self.character_sprites = arcade.SpriteList()
        self.character_sprites.extend(self.player.parts)

        # Set the most basic background color
        arcade.set_background_color(utils.Color.BLACK)

        # Add the player
        self.physics_engine.add_sprite(
            self.player,
            friction=0,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            damping=0.001,
            collision_type="player",
            elasticity=0.1,
            max_velocity=400,
        )

        # Create the walls
        self.physics_engine.add_sprite_list(
            self.room.walls,
            friction=0,
            collision_type="wall",
            body_type=PymunkPhysicsEngine.STATIC,
        )

        # Add instructions
        self.start_sprite_list = arcade.SpriteList()
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/MoveGuide.png", scale=0.3, center_x=200, center_y=200
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/ShootGuide.png",
                scale=0.3,
                center_x=self.w - 200,
                center_y=200,
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/PauseGuide.png",
                scale=0.3,
                center_x=200,
                center_y=self.h - 100,
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/WeaponChangeGuide.png",
                scale=0.3,
                center_x=200,
                center_y=self.h - 200,
            )
        )

        # Add UI elements
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.vertical_box = arcade.gui.UIBoxLayout(x=200)
        title = arcade.Sprite(filename="graphics/Title.png", scale=2)
        title_ui = arcade.gui.UISpriteWidget(
            sprite=title, width=400, height=300)
        self.vertical_box.add(title_ui.with_space_around(bottom=0))

        start_button = arcade.gui.UIFlatButton(
            text="Start", width=150, style=utils.Style.BUTTON_DEFAULT
        )
        option_button = arcade.gui.UIFlatButton(
            text="Option", width=150, style=utils.Style.BUTTON_DEFAULT
        )
        quit_button = arcade.gui.UIFlatButton(
            text="Quit", width=150, style=utils.Style.BUTTON_DEFAULT
        )

        self.vertical_box.add(start_button.with_space_around(bottom=20))
        self.vertical_box.add(option_button.with_space_around(bottom=20))
        self.vertical_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_click_start
        option_button.on_click = self.on_click_option
        quit_button.on_click = self.on_click_quit

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.vertical_box
            )
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
        self.update_player_attack()
        self.process_player_bullet()

        self.scroll_to_player()

    def update_player_attack(self) -> None:
        if self.player.is_attack:
            if self.player.cd == self.player.cd_max:
                self.player.cd = 0

            if self.player.cd == 0 and self.player.energy - self.player.current_weapon.cost >= 0:
                self.player.energy = max(
                    0, self.player.energy - self.player.current_weapon.cost)
                bullets = self.player.attack()
                self.player.current_weapon.play_sound(self.window.effect_volume)
                for bullet in bullets:
                    bullet.change_x = bullet.aim.x
                    bullet.change_y = bullet.aim.y
                    self.player_bullet_list.append(bullet)

        self.player.cd = min(self.player.cd + 1, self.player.cd_max)

    def process_player_bullet(self) -> None:
        self.player_bullet_list.update()

        for bullet in self.player_bullet_list:
            bullet.life_span -= 1

            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.is_attack = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.is_attack = False

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
        if (
            self.player.pos.x > float(self.w / 2) - 5
            and self.room.width - self.player.pos.x > float(self.w / 2) - 5
        ):
            position.x = self.player.pos.x - float(self.w / 2)
        if (
            self.player.pos.y > float(self.h / 2) - 5
            and self.room.height - self.player.pos.y > float(self.h / 2) - 5
        ):
            position.y = self.player.pos.y - float(self.h / 2)

        self.camera_sprites.move_to(position, CAMERA_SPEED)

    def resize_camera(self, width, height) -> None:
        self.w = width
        self.h = height
        self.setup()
        self.camera_sprites.resize(width, height)

    def on_click_start(self, event) -> None:
        selection_view = SelectionView()
        selection_view.setup()
        self.window.show_view(selection_view)

    def on_click_option(self, event) -> None:
        option_view = OptionView()
        option_view.setup(self)
        self.window.show_view(option_view)

    def on_click_quit(self, event) -> None:
        arcade.exit()


class SelectionView(FadingView):
    """Character and map selection."""

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)

    def setup(self) -> None:
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.selection_box = arcade.gui.UIBoxLayout(vertical=False)
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)

        # Selection buttons
        character_left_button = arcade.gui.UIFlatButton(
            text="<", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        character_right_button = arcade.gui.UIFlatButton(
            text=">", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        map_left_button = arcade.gui.UIFlatButton(
            text="<", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        map_right_button = arcade.gui.UIFlatButton(
            text=">", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        self.selection_box.add(character_left_button.with_space_around(right=20))
        self.selection_box.add(character_right_button.with_space_around(right=300))
        self.selection_box.add(map_left_button.with_space_around(right=20))
        self.selection_box.add(map_right_button.with_space_around(right=0))

        # Rest buttons
        back_button = arcade.gui.UIFlatButton(
            text="Back", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        next_button = arcade.gui.UIFlatButton(
            text="Next", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        self.rest_box.add(back_button.with_space_around(right=200))
        self.rest_box.add(next_button.with_space_around(right=0))
        back_button.on_click = self.on_click_back

         # Add box layouts
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_y=-100, child=self.selection_box)
        )
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=-200, child=self.rest_box))

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()

    def on_click_back(self, event) -> None:
        start_view = StartView()
        start_view.setup()
        start_view.resize_camera(self.window.width, self.window.height)
        self.window.show_view(start_view)
        self.window.play_button_sound()

class OptionView(arcade.View):
    """Optional menu."""

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)

    def setup(self, last_view) -> None:
        self.last_view = last_view

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.effect_volume_box = arcade.gui.UIBoxLayout(vertical=False)
        self.music_volume_box = arcade.gui.UIBoxLayout(vertical=False)
        self.screen_box = arcade.gui.UIBoxLayout(vertical=False)
        self.resolution_box = arcade.gui.UIBoxLayout(vertical=False)
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)

        # Effect volume settings
        effect_volume_label = arcade.gui.UITextArea(
            text="Effect Volume",
            width=300,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        effect_volume_down_button = arcade.gui.UIFlatButton(
            text="-", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.effect_volume_text = arcade.gui.UITextArea(
            text=str(self.window.effect_volume),
            width=40,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        effect_volume_up_button = arcade.gui.UIFlatButton(
            text="+", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.effect_volume_box.add(
            effect_volume_label.with_space_around(right=20))
        self.effect_volume_box.add(
            effect_volume_down_button.with_space_around(right=20)
        )
        self.effect_volume_box.add(
            self.effect_volume_text.with_space_around(right=10))
        self.effect_volume_box.add(
            effect_volume_up_button.with_space_around(right=0))
        effect_volume_up_button.on_click = self.on_click_effect_volume_up
        effect_volume_down_button.on_click = self.on_click_effect_volume_down

        # Music volume settings
        music_volume_label = arcade.gui.UITextArea(
            text="Music Volume",
            width=300,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        music_volume_down_button = arcade.gui.UIFlatButton(
            text="-", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.music_volume_text = arcade.gui.UITextArea(
            text=str(self.window.music_volume),
            width=40,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        music_volume_up_button = arcade.gui.UIFlatButton(
            text="+", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.music_volume_box.add(
            music_volume_label.with_space_around(right=20))
        self.music_volume_box.add(
            music_volume_down_button.with_space_around(right=20))
        self.music_volume_box.add(
            self.music_volume_text.with_space_around(right=10))
        self.music_volume_box.add(
            music_volume_up_button.with_space_around(right=0))
        music_volume_up_button.on_click = self.on_click_music_volume_up
        music_volume_down_button.on_click = self.on_click_music_volume_down

        # Screen settings
        fullscreen_label = arcade.gui.UITextArea(
            text="Fullscreen: ",
            width=200,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        self.fullscreen_text = arcade.gui.UITextArea(
            text=str(self.window.fullscreen),
            width=120,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        fullscreen_button = arcade.gui.UIFlatButton(
            text="Switch", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        self.screen_box.add(fullscreen_label.with_space_around(right=20))
        self.screen_box.add(self.fullscreen_text.with_space_around(right=20))
        self.screen_box.add(fullscreen_button.with_space_around(right=0))
        fullscreen_button.on_click = self.on_click_fullscreen

        # Resolution settings
        resolution_label = arcade.gui.UITextArea(
            text="Resolution",
            width=200,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        resolution_down_button = arcade.gui.UIFlatButton(
            text="<", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.resolution_text = arcade.gui.UITextArea(
            text="1280 x 720",
            width=200,
            height=40,
            font_size=20,
            text_color=utils.Color.BLACK,
            font_name="FFF Forward",
        )
        resolution_up_button = arcade.gui.UIFlatButton(
            text=">", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.resolution_box.add(resolution_label.with_space_around(right=20))
        self.resolution_box.add(
            resolution_down_button.with_space_around(right=40))
        self.resolution_box.add(
            self.resolution_text.with_space_around(right=0))
        if self.window.fullscreen:
            self.resolution_text.text = "Fullscreen"
        else:
            self.resolution_text.text = str(
            self.window.w_scale[self.window.res_index]) + " x " + str(self.window.h_scale[self.window.res_index])
        self.resolution_box.add(
            resolution_up_button.with_space_around(right=0))
        resolution_up_button.on_click = self.on_click_resolution_up
        resolution_down_button.on_click = self.on_click_resolution_down

        # Rest buttons
        back_button = arcade.gui.UIFlatButton(
            text="Back", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        start_view_button = arcade.gui.UIFlatButton(
            text="Start Menu", width=180, style=utils.Style.BUTTON_DEFAULT
        )
        quit_button = arcade.gui.UIFlatButton(
            text="Quit", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        self.rest_box.add(back_button.with_space_around(right=100))
        self.rest_box.add(start_view_button.with_space_around(right=100))
        self.rest_box.add(quit_button.with_space_around(right=0))
        back_button.on_click = self.on_click_back
        start_view_button.on_click = self.on_click_start_menu
        quit_button.on_click = self.on_click_quit

        # Add box layouts
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_y=200, child=self.effect_volume_box)
        )
        self.manager.add(
            arcade.gui.UIAnchorWidget(align_y=100, child=self.music_volume_box)
        )
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=0, child=self.screen_box))
        self.manager.add(
            arcade.gui.UIAnchorWidget(align_y=-100, child=self.resolution_box)
        )
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=-240, child=self.rest_box))

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()

    def on_click_effect_volume_up(self, event) -> None:
        self.window.effect_volume = min(10, self.window.effect_volume + 1)
        self.effect_volume_text.text = str(self.window.effect_volume)
        self.window.play_button_sound()

    def on_click_effect_volume_down(self, event) -> None:
        self.window.effect_volume = max(0, self.window.effect_volume - 1)
        self.effect_volume_text.text = str(self.window.effect_volume)
        self.window.play_button_sound()

    def on_click_music_volume_up(self, event) -> None:
        self.window.music_volume = min(10, self.window.music_volume + 1)
        self.music_volume_text.text = str(self.window.music_volume)
        self.window.play_button_sound()

    def on_click_music_volume_down(self, event) -> None:
        self.window.music_volume = max(0, self.window.music_volume - 1)
        self.music_volume_text.text = str(self.window.music_volume)
        self.window.play_button_sound()

    def on_click_fullscreen(self, event) -> None:
        self.window.set_fullscreen(not self.window.fullscreen)
        self.fullscreen_text.text = str(self.window.fullscreen)
        width, height = self.window.get_size()
        self.window.set_viewport(0, width, 0, height)
        if self.window.fullscreen:
            self.resolution_text.text = "Fullscreen"
        else:
            self.resolution_text.text = str(
            self.window.w_scale[self.window.res_index]) + " x " + str(self.window.h_scale[self.window.res_index])
        self.window.play_button_sound()

    def on_click_resolution_up(self, event) -> None:
        if self.window.fullscreen:
            return
        self.window.res_index += 1
        self.window.res_index %= 4
        self.window.set_size(self.window.w_scale[self.window.res_index],
                             self.window.h_scale[self.window.res_index])
        width, height = self.window.get_size()
        self.window.set_viewport(0, width, 0, height)
        self.resolution_text.text = str(
            self.window.w_scale[self.window.res_index]) + " x " + str(self.window.h_scale[self.window.res_index])
        self.window.play_button_sound()

    def on_click_resolution_down(self, event) -> None:
        if self.window.fullscreen:
            return
        self.window.res_index -= 1
        self.window.res_index %= 4
        self.window.set_size(self.window.w_scale[self.window.res_index],
                             self.window.h_scale[self.window.res_index])
        width, height = self.window.get_size()
        self.window.set_viewport(0, width, 0, height)
        self.resolution_text.text = str(
            self.window.w_scale[self.window.res_index]) + " x " + str(self.window.h_scale[self.window.res_index])
        self.window.play_button_sound()

    def on_click_back(self, event) -> None:
        self.last_view.resize_camera(self.window.width, self.window.height)
        self.window.show_view(self.last_view)
        self.window.play_button_sound()

    def on_click_start_menu(self, event) -> None:
        start_view = StartView()
        start_view.setup()
        start_view.resize_camera(self.window.width, self.window.height)
        self.window.show_view(start_view)
        self.window.play_button_sound()

    def on_click_quit(self, event) -> None:
        self.window.play_button_sound()
        arcade.exit()

class GameView(FadingView):
    """Main game view."""

    def __init__(self):
        super().__init__()


class GameOverView(arcade.View):
    """Game over view."""

    def __init__(self):
        super().__init__()
