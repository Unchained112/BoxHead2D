import arcade
import arcade.gui
import utils
import room
import character
import weapon
import item
import effect
import math
import random
from pyglet.math import Vec2
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

FADE_RATE = 8
CAMERA_SPEED = 1


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
                self.window.start_view = self.next_view()
                self.window.start_view.setup()
                self.window.show_view(self.window.start_view)

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
            filename="graphics/ui/TitleLogo.png",
            scale=1,
            center_x=self.w / 2,
            center_y=self.h / 2 + 20,
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

        self.camera_sprites = arcade.Camera(self.w, self.h)

    def setup(self) -> None:
        # Play start view BGM
        self.window.play_start_music(0)

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

        # Set the most basic background color
        arcade.set_background_color(utils.Color.BLACK)

        # Add the player
        self.physics_engine.add_sprite(
            self.player,
            friction=0,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            damping=0.001,
            collision_type="player",
            elasticity=0.1
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
                filename="graphics/ui/MoveGuide.png",
                scale=0.3,
                center_x=200,
                center_y=200
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/ui/ShootGuide.png",
                scale=0.3,
                center_x=self.w - 200,
                center_y=200,
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/ui/PauseGuide.png",
                scale=0.3,
                center_x=200,
                center_y=self.h - 100,
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/ui/WeaponChangeGuide.png",
                scale=0.3,
                center_x=200,
                center_y=self.h - 200,
            )
        )
        self.start_sprite_list.append(
            arcade.Sprite(
                filename="graphics/ui/ShopGuide.png",
                scale=0.3,
                center_x=self.w - 200,
                center_y=self.h - 100,
            )
        )
        self.about_text = arcade.Text("Created by Unchain.",
                                      self.w - 600,
                                      120,
                                      color=utils.Color.DARK_GRAY,
                                      font_size=14,
                                      font_name="FFF Forward",
                                      anchor_x="center")
        self.about_text_shadow = arcade.Text("Created by Unchain.",
                                      self.w - 602,
                                      120,
                                      color=utils.Color.LIGHT_GRAY,
                                      font_size=14,
                                      font_name="FFF Forward",
                                      anchor_x="center")

        # Add UI elements
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.vertical_box = arcade.gui.UIBoxLayout(x=200)
        title = arcade.Sprite(filename="graphics/ui/TitleLogo.png", scale=1)
        title_ui = arcade.gui.UISpriteWidget(
            sprite=title, width=400, height=200)
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
        self.player.draw()
        self.player_bullet_list.draw()
        self.manager.draw()
        self.about_text_shadow.draw()
        self.about_text.draw()

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
                self.player.energy -= self.player.current_weapon.cost
                bullets = self.player.attack()
                self.player.current_weapon.play_sound(
                    self.window.effect_volume)
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
        x = self.player.pos.x - float(self.w / 2)
        if self.player.pos.x < float(self.w / 2):
            x = 0
        elif self.player.pos.x > float(self.room.width - self.w / 2):
            x = float(self.room.width - self.w)

        y = self.player.pos.y - float(self.h / 2)
        if self.player.pos.y < float(self.h / 2):
            y = 0
        elif self.player.pos.y > float(self.room.height - self.h / 2):
            y = float(self.room.height - self.h)

        self.camera_sprites.move_to((x, y), CAMERA_SPEED)

    def resize_camera(self, width, height) -> None:
        self.w = width
        self.h = height
        self.setup()
        self.camera_sprites.resize(width, height)

    def on_click_start(self, event) -> None:
        utils.Utils.clear_ui_manager(self.manager)
        self.window.select_view.setup()
        self.window.show_view(self.window.select_view)

    def on_click_option(self, event) -> None:
        utils.Utils.clear_ui_manager(self.manager)
        self.window.option_view.setup(self)
        self.window.show_view(self.window.option_view)

    def on_click_quit(self, event) -> None:
        utils.Utils.save_settings(self.window)
        arcade.exit()


class SelectionView(FadingView):
    """Character and map selection."""

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)

    def setup(self) -> None:
        self.w = self.window.width
        self.h = self.window.height

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.selection_box = arcade.gui.UIBoxLayout(vertical=False)
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)

        # Characters
        self.char_sprites = arcade.SpriteList()
        self.char_list = [
            character.Player,
            character.Rambo
        ]
        self.cur_char_idx = 0
        self.cur_char = character.Character(
            float(self.w/2 - 240), float(self.h/2))
        self.set_character()

        # Maps
        self.map_list = [
            room.GameRoom0,
            room.GameRoom1
        ]
        self.cur_map_idx = 0
        self.cur_map = self.map_list[self.cur_map_idx]
        self.cur_map_sprite = arcade.Sprite()
        self.set_maps()

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
        self.selection_box.add(
            character_left_button.with_space_around(right=20))
        self.selection_box.add(
            character_right_button.with_space_around(right=300))
        self.selection_box.add(map_left_button.with_space_around(right=20))
        self.selection_box.add(map_right_button.with_space_around(right=0))
        character_left_button.on_click = self.on_click_last_char
        character_right_button.on_click = self.on_click_next_char
        map_left_button.on_click = self.on_click_last_map
        map_right_button.on_click = self.on_click_next_map

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
        next_button.on_click = self.on_click_next

        # Add box layouts
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_y=-100, child=self.selection_box)
        )
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=-200, child=self.rest_box))

    def set_character(self, idx: int = 0) -> None:
        self.cur_char_idx += idx
        self.cur_char_idx %= len(self.char_list)
        self.char_sprites.clear()
        self.cur_char.body.texture = self.char_list[self.cur_char_idx].body_texture
        self.char_sprites.extend(self.cur_char.parts)

    def set_maps(self, idx: int = 0) -> None:
        self.cur_map_idx += idx
        self.cur_map_idx %= len(self.map_list)
        self.cur_map = self.map_list[self.cur_map_idx]
        self.cur_map_sprite = self.cur_map.layout_sprite
        self.cur_map_sprite.center_x = float(self.w/2 + 220)
        self.cur_map_sprite.center_y = float(self.h/2 + 20)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.char_sprites.draw()
        self.cur_map_sprite.draw()

    def on_update(self, delta_time: float):
        self.cur_char.update()

    def on_click_back(self, event) -> None:
        utils.Utils.clear_ui_manager(self.manager)
        self.window.start_view.setup()
        self.window.start_view.resize_camera(
            self.window.width, self.window.height)
        self.window.show_view(self.window.start_view)
        self.window.play_button_sound()

    def on_click_last_char(self, event) -> None:
        self.set_character(-1)
        self.window.play_button_sound()

    def on_click_next_char(self, event) -> None:
        self.set_character(1)
        self.window.play_button_sound()

    def on_click_last_map(self, event) -> None:
        self.set_maps(-1)
        self.window.play_button_sound()

    def on_click_next_map(self, event) -> None:
        self.set_maps(1)
        self.window.play_button_sound()

    def on_click_next(self, event) -> None:
        utils.Utils.clear_ui_manager(self.manager)
        self.window.game_view = GameView()
        self.window.game_view.setup(
            self.char_list[self.cur_char_idx], self.cur_map)
        self.window.show_view(self.window.game_view)
        self.window.play_button_sound()


class OptionView(arcade.View):
    """Optional menu."""

    def __init__(self):
        super().__init__()
        self.manager = None
        self.last_view = None

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.window.set_mouse_visible(True)

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

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.ESCAPE:
            self.on_click_back(event=None)

    def on_click_effect_volume_up(self, event) -> None:
        self.window.effect_volume = min(20, self.window.effect_volume + 1)
        self.effect_volume_text.text = str(self.window.effect_volume)
        self.window.play_button_sound()

    def on_click_effect_volume_down(self, event) -> None:
        self.window.effect_volume = max(0, self.window.effect_volume - 1)
        self.effect_volume_text.text = str(self.window.effect_volume)
        self.window.play_button_sound()

    def on_click_music_volume_up(self, event) -> None:
        self.window.music_volume = min(20, self.window.music_volume + 1)
        self.music_volume_text.text = str(self.window.music_volume)
        self.window.play_button_sound()
        self.window.update_music_volume()

    def on_click_music_volume_down(self, event) -> None:
        self.window.music_volume = max(0, self.window.music_volume - 1)
        self.music_volume_text.text = str(self.window.music_volume)
        self.window.play_button_sound()
        self.window.update_music_volume()

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
        utils.Utils.clear_ui_manager(self.manager)
        if type(self.last_view) == StartView:
            self.last_view.setup()
        self.last_view.resize_camera(self.window.width, self.window.height)
        self.window.show_view(self.last_view)
        self.window.play_button_sound()

    def on_click_start_menu(self, event) -> None:
        self.last_view = None
        utils.Utils.clear_ui_manager(self.manager)
        self.window.start_view.setup()
        self.window.start_view.resize_camera(
            self.window.width, self.window.height)
        self.window.show_view(self.window.start_view)
        self.window.play_button_sound()

    def on_click_quit(self, event) -> None:
        self.window.play_button_sound()
        utils.Utils.save_settings(self.window)
        arcade.exit()


class GameView(FadingView):
    """Main game view."""

    def __init__(self):
        super().__init__()
        self.mouse_x = None
        self.mouse_y = None
        self.mouse_pos = Vec2(0, 0)
        self.mouse_sprite = arcade.Sprite("graphics/ui/Cursor.png")
        self.physics_engine = None
        self.manager = None

        # Sprite lists
        self.wall_list = None
        self.player = None
        self.player_bullet_list = None
        self.enemy_white_list = None
        self.enemy_red_list = None
        self.enemy_crack_list = None
        self.enemy_big_mouth_list = None
        self.enemy_crash_list = None
        self.enemy_tank_list = None
        self.enemy_sprite_list = None
        self.enemy_bullet_list = None
        self.explosions_list = None
        self.blood_list = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.camera_sprites = arcade.Camera(self.w, self.h)
        self.camera_gui = arcade.Camera(self.w, self.h)

    def setup(self, player: character.Player, map: room.Room) -> None:
        """Set up the game and initialize the variables."""

        # Play game BGM
        self.window.play_game_music(1)

        # Gameplay set up
        self.round: int = 0
        self.multiplier: int = 1
        self.score: int = 0
        self.money_pool: int = 0
        self.spawn_cnt: int = -1
        self.round_text = arcade.Text("", self.w / 2,
                                      self.h - 50, utils.Color.BLACK,
                                      15, 2, "left", "FFF Forward")
        self.multiplier_text = arcade.Text("", self.w - 200,
                                           self.h - 140, utils.Color.MUL_GREEN,
                                           30, 2, "left", "FFF Forward")
        self.score_text = arcade.Text("Score: " + str(self.score), self.w - 240,
                                      self.h - 50, utils.Color.BLACK,
                                      15, 2, "left", "FFF Forward")

        self.window.set_mouse_visible(False)
        self.counter: int = 0  # assume 60 frames -> 60 = 1s
        self.total_time = 0
        self.last_kill_time = 0
        self.shop_enabled = False  # Enable if money_pool >= round * 100

        # UI set up
        self.ui_sprite_list = arcade.SpriteList()
        self.health_sprite = arcade.Sprite(
            filename="graphics/ui/Health.png",
            center_x=72,
            center_y=self.h - 40,
            image_width=25,
            image_height=25,
            scale=1,
        )
        self.energy_sprite = arcade.Sprite(
            filename="graphics/ui/Energy.png",
            center_x=72,
            center_y=self.h - 70,
            image_width=25,
            image_height=25,
            scale=1,
        )
        self.weapon_slot_sprite = arcade.Sprite(
            filename="graphics/ui/WeaponSlot.png",
            center_x=150,
            center_y=self.h - 120,
            image_width=80,
            image_height=40,
            scale=1,
        )
        self.ui_sprite_list.append(self.health_sprite)
        self.ui_sprite_list.append(self.energy_sprite)
        self.ui_sprite_list.append(self.weapon_slot_sprite)
        # Money UI
        self.money_ui = arcade.Sprite(
            filename="graphics/ui/Coin.png",
            center_x=self.w/2 + 320,
            center_y=60,
            scale=1,
        )
        self.money_ui.alpha = 0
        self.buy_text = arcade.Text("", self.w/2 + 340,
                                    52, utils.Color.BLACK,
                                    10, 2, "left", "FFF Forward")
        self.money_container = arcade.SpriteSolidColor(
            600, 16, utils.Color.BLACK)
        self.money_container.center_x = self.w / 2
        self.money_container.center_y = 60
        self.money_fill = arcade.SpriteSolidColor(
            594, 10, utils.Color.DARK_GRAY)
        self.money_fill.center_x = self.w / 2
        self.money_fill.center_y = 60
        self.money_pool_ui = arcade.SpriteSolidColor(
            1, 10, utils.Color.YELLOW)
        self.money_pool_ui.center_x = self.w / 2 - 297
        self.money_pool_ui.center_y = 60
        self.money_pool_ui.visible = False

        self.ui_sprite_list.append(self.money_ui)
        self.ui_sprite_list.append(self.money_container)
        self.ui_sprite_list.append(self.money_fill)
        self.ui_sprite_list.append(self.money_pool_ui)

        self.cur_weapon_sprite = arcade.Sprite()
        self.cur_weapon_sprite.center_x = 150
        self.cur_weapon_sprite.center_y = self.h - 120
        self.last_weapon_sprite = arcade.Sprite()
        self.last_weapon_sprite.center_x = 70
        self.last_weapon_sprite.center_y = self.h - 120
        self.next_weapon_sprite = arcade.Sprite()
        self.next_weapon_sprite.center_x = 230
        self.next_weapon_sprite.center_y = self.h - 120
        self.ui_sprite_list.append(self.cur_weapon_sprite)
        self.ui_sprite_list.append(self.last_weapon_sprite)
        self.ui_sprite_list.append(self.next_weapon_sprite)

        # GameObject lists
        self.wall_list = arcade.SpriteList()
        self.enemy_white_list = arcade.SpriteList()
        self.enemy_crack_list = arcade.SpriteList()
        self.enemy_big_mouth_list = arcade.SpriteList()
        self.enemy_crash_list = arcade.SpriteList()
        self.enemy_tank_list = arcade.SpriteList()
        self.enemy_red_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.player_object_list = arcade.SpriteList()
        self.player_mine_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.blood_list = arcade.SpriteList()
        self.enemy_sprite_list = arcade.SpriteList()

        # Create the physics engine
        damping = 0.01
        gravity = (0, 0)
        self.physics_engine = PymunkPhysicsEngine(gravity, damping)

        # Game room setup
        self.room = map()
        self.wall_list = self.room.walls

        # Set up the player
        self.player = player(
            float(self.w / 2), float(self.h / 2), self.physics_engine)

        # Set up the shop
        self.shop = item.Shop(self.player)

        self.physics_engine.add_sprite(
            self.player,
            friction=0,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            damping=0.001,
            collision_type="player",
            elasticity=0.1
        )
        self.physics_engine.add_sprite_list(
            self.room.walls,
            friction=0,
            collision_type="wall",
            body_type=PymunkPhysicsEngine.STATIC,
        )

    def on_draw(self) -> None:
        self.clear()
        self.camera_sprites.use()

        self.room.draw_ground()
        self.blood_list.draw()
        self.player_mine_list.draw()
        self.room.draw_walls()
        self.player.draw()
        self.enemy_sprite_list.draw()
        self.player_bullet_list.draw()
        self.player_object_list.draw()
        self.enemy_bullet_list.draw()
        self.explosions_list.draw()

        # Select the (un-scrolled) camera for our GUI
        self.camera_gui.use()

        # Mouse cursor
        if self.mouse_x and self.mouse_y:
            self.mouse_sprite.draw()

        # Render the GUI
        self.draw_ui()

    def on_update(self, delta_time) -> None:
        self.physics_engine.step()
        self.total_time += delta_time
        self.counter += 1

        # Update player
        self.player.update()
        self.update_player_attack()
        self.process_player_bullet()

        # Update level
        self.manage_level()
        self.enemy_sprite_list.update()
        self.update_enemy_attack()
        self.process_enemy_bullet()

        self.explosions_list.update()
        self.blood_list.update()

        self.scroll_to_player()

    def on_show_view(self) -> None:
        self.window.set_mouse_visible(False)
        self.manager = None

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

        # Change weapon
        if key == arcade.key.Q:
            self.player.change_weapon_left = True
        if key == arcade.key.E:
            self.player.change_weapon_right = True

        # Pause game
        if key == arcade.key.ESCAPE:
            # pass self, the current view, to preserve this view's state
            self.window.option_view.setup(self)
            self.window.show_view(self.window.option_view)

        # Buy item
        if key == arcade.key.B and self.shop_enabled:
            self.window.shop_view.setup(self)
            self.window.show_view(self.window.shop_view)

    def on_key_release(self, key, modifiers) -> None:

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
        x = self.player.pos.x - float(self.w / 2)
        if self.player.pos.x < float(self.w / 2):
            x = 0
        elif self.player.pos.x > float(self.room.width - self.w / 2):
            x = float(self.room.width - self.w)

        y = self.player.pos.y - float(self.h / 2)
        if self.player.pos.y < float(self.h / 2):
            y = 0
        elif self.player.pos.y > float(self.room.height - self.h / 2):
            y = float(self.room.height - self.h)

        self.camera_sprites.move_to((x, y), CAMERA_SPEED)

    def shake_camera(self) -> None:
        # Pick a random direction
        shake_direction = random.random() * 2 * math.pi
        # How 'far' to shake
        shake_amplitude = 6
        # Calculate a vector based on that
        shake_vector = Vec2(
            math.cos(shake_direction) * shake_amplitude,
            math.sin(shake_direction) * shake_amplitude
        )
        # Frequency of the shake
        shake_speed = 1.6
        # How fast to damp the shake
        shake_damping = 0.9
        # Do the shake
        self.camera_sprites.shake(shake_vector,
                                  speed=shake_speed,
                                  damping=shake_damping)

    def resize_camera(self, width, height) -> None:
        self.w = width
        self.h = height
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)

        # update ui sprites position
        self.health_sprite.center_y = self.h - 40
        self.energy_sprite.center_y = self.h - 70
        self.weapon_slot_sprite.center_y = self.h - 120
        self.cur_weapon_sprite.center_y = self.h - 120
        self.last_weapon_sprite.center_y = self.h - 120
        self.next_weapon_sprite.center_y = self.h - 120
        self.round_text.x = self.w / 2
        self.round_text.y = self.h - 50
        self.multiplier_text.x = self.w - 200
        self.multiplier_text.y = self.h - 140
        self.score_text.x = self.w - 240
        self.score_text.y = self.h - 50
        self.money_container.center_x = self.w / 2
        self.money_fill.center_x = self.w / 2
        self.money_ui.center_x = self.w/2 + 320
        self.buy_text.center_x = self.w/2 + 340

    def draw_ui(self) -> None:
        # Health
        arcade.draw_text(text=int(self.player.health),
                         start_x=100,
                         start_y=self.h - 50,
                         color=utils.Color.HEALTH_RED,
                         font_size=12,
                         width=2,
                         align="left",
                         font_name="FFF Forward")

        # Energy
        arcade.draw_text(text=int(self.player.energy),
                         start_x=100,
                         start_y=self.h - 80,
                         color=utils.Color.ENERGY_BLUE,
                         font_size=12,
                         width=2,
                         align="left",
                         font_name="FFF Forward")

        # Weapon slot
        wp_size = len(self.player.weapons)
        self.cur_weapon_sprite.texture = self.player.current_weapon.texture_list[0]
        if self.player.current_weapon.is_gun:
            self.cur_weapon_sprite.scale = 2
        else:
            self.cur_weapon_sprite.scale = 0.8
        last_index = (self.player.weapon_index - 1) % wp_size
        self.last_weapon_sprite.texture = self.player.weapons[last_index].texture_list[0]
        if self.player.weapons[last_index].is_gun:
            self.last_weapon_sprite.scale = 2
        else:
            self.last_weapon_sprite.scale = 0.8
        next_index = (self.player.weapon_index + 1) % wp_size
        self.next_weapon_sprite.texture = self.player.weapons[next_index].texture_list[0]
        if self.player.weapons[next_index].is_gun:
            self.next_weapon_sprite.scale = 2
        else:
            self.next_weapon_sprite.scale = 0.8

        # Change weapon ui according to the number of weapons
        if wp_size == 1:
            self.last_weapon_sprite.alpha = 0
            self.next_weapon_sprite.alpha = 0
        elif wp_size == 2:
            self.last_weapon_sprite.alpha = 0
            self.next_weapon_sprite.alpha = 120
        else:
            self.last_weapon_sprite.alpha = 120
            self.next_weapon_sprite.alpha = 120

        self.ui_sprite_list.draw()

        # Round
        self.round_text.draw()

        # Score
        self.score_text.draw()
        self.multiplier_text.draw()

        # Money
        self.buy_text.draw()

    def update_player_attack(self) -> None:
        if self.player.is_attack:
            if self.player.cd == self.player.cd_max:
                self.player.cd = 0

            if self.player.cd == 0 and self.player.energy - self.player.current_weapon.cost >= 0:
                if self.player.current_weapon.is_gun:
                    self.player.energy = max(
                        0, self.player.energy - self.player.current_weapon.cost)
                    bullets = self.player.attack()
                    self.player.current_weapon.play_sound(
                        self.window.effect_volume)
                    for bullet in bullets:
                        bullet.change_x = bullet.aim.x
                        bullet.change_y = bullet.aim.y
                        self.player_bullet_list.append(bullet)
                else:
                    object = self.player.place()
                    place_point = self.player.pos + \
                        self.player.current_weapon.aim_pos.normalize().scale(30)
                    grid_x = math.floor(place_point.x / 30)
                    grid_y = math.floor(place_point.y / 30)
                    if self.room.grid[grid_x, grid_y] != 1:
                        object.center_x = grid_x * 30 + \
                            float(utils.Utils.HALF_WALL_SIZE)
                        object.center_y = grid_y * 30 + \
                            float(utils.Utils.HALF_WALL_SIZE)
                        object.grid_idx = (grid_x, grid_y)
                        if object.object_type != 2:
                            self.player_object_list.append(object)
                            self.physics_engine.add_sprite(object,
                                                           friction=0,
                                                           collision_type="object",
                                                           body_type=PymunkPhysicsEngine.STATIC)
                        else:
                            self.player_mine_list.append(object)
                        self.room.grid[grid_x, grid_y] = 1
                        self.player.current_weapon.play_sound(
                            self.window.effect_volume)
                        # Consume energy only when object is placed
                        self.player.energy = max(
                            0, self.player.energy - self.player.current_weapon.cost)

        self.player.cd = min(self.player.cd + 1, self.player.cd_max)

    def process_player_bullet(self) -> None:
        self.player_bullet_list.update()
        self.player_object_list.update()
        self.player_mine_list.update()

        for bullet in self.player_bullet_list:
            bullet.life_span -= 1

            # Check hit with enemy
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.enemy_white_list,
                    self.enemy_red_list,
                    self.enemy_crack_list,
                    self.enemy_big_mouth_list,
                    self.enemy_crash_list,
                    self.enemy_tank_list,
                ],
            )

            for enemy in hit_list:
                enemy.health -= bullet.damage
                self.set_blood(enemy.position)
                self.player.energy += (bullet.damage/10)
                self.physics_engine.apply_force(
                    enemy, (bullet.aim.x * utils.Utils.BULLET_FORCE, bullet.aim.y * utils.Utils.BULLET_FORCE))
                enemy.get_damage_len = utils.Utils.GET_DAMAGE_LEN
                if enemy.health <= 0:
                    self.player.health += self.player.kill_recover
                    self.remove_enemy(enemy)

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()
                continue

            # Check hit with player objects
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.player_object_list)

            for object in hit_list:
                if object.object_type == 0:  # Wall object
                    object.health -= bullet.damage
                    if object.health <= 0:
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()
                if object.object_type == 1:  # Barrel object
                    object.health -= bullet.damage
                    if object.health <= 0:
                        self.set_explosion(object.position)
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()
                continue

            # Check hit with room walls
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()
                continue

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def update_enemy_attack(self) -> None:
        # Enemy White
        for enemy in self.enemy_white_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)

        # Enemy Red
        for enemy in self.enemy_red_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            if enemy.is_walking == False:
                if enemy.cd == enemy.cd_max:
                    enemy.cd = 0
                if enemy.cd == 0:
                    bullet = enemy.attack()
                    self.enemy_bullet_list.append(bullet)
            enemy.cd = min(enemy.cd + 1, enemy.cd_max)

        # Enemy Crack
        for enemy in self.enemy_crack_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)

        # Enemy Big Mouth
        for enemy in self.enemy_big_mouth_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            if enemy.is_walking == False:
                if enemy.cd == enemy.cd_max:
                    enemy.cd = 0
                if enemy.cd == 0:
                    bullets = enemy.attack()
                    self.enemy_bullet_list.extend(bullets)
            enemy.cd = min(enemy.cd + 1, enemy.cd_max)

        # Enemy Crash
        for enemy in self.enemy_crash_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            if enemy.is_walking == False:
                if enemy.cd == enemy.cd_max:
                    enemy.cd = 0
                if enemy.cd < enemy.cd_max / 2:
                    enemy.dash()
            enemy.cd = min(enemy.cd + 1, enemy.cd_max)

        # Enemy Tank
        for enemy in self.enemy_tank_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            if enemy.is_walking == False:
                if enemy.cd == enemy.cd_max:
                    enemy.cd = 0
                if enemy.cd < enemy.cd_max * 2 / 3:
                    enemy.dash()
            enemy.cd = min(enemy.cd + 1, enemy.cd_max)

    def process_enemy_bullet(self) -> None:
        self.enemy_bullet_list.update()

        for bullet in self.enemy_bullet_list:
            bullet.life_span -= 1

            # check hit with player
            if arcade.check_for_collision(bullet, self.player):
                self.player.health = max(self.player.health - bullet.damage, 0)
                bullet.remove_from_sprite_lists()
                self.physics_engine.apply_force(
                    self.player, (bullet.aim.x * utils.Utils.BULLET_FORCE,
                                  bullet.aim.y * utils.Utils.BULLET_FORCE))
                self.player.get_damage_len = utils.Utils.GET_DAMAGE_LEN

            # check hit with player objects
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.player_object_list)

            for object in hit_list:
                if object.object_type == 0:  # Wall object
                    object.health -= bullet.damage
                    if object.health <= 0:
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()
                if object.object_type == 1:  # Barrel object
                    object.health -= bullet.damage
                    if object.health <= 0:
                        self.set_explosion(object.position)
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

             # check hit with room walls
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def remove_enemy(self, enemy: character.Character) -> None:
        enemy.physics_engines.clear()  # to avoid key error
        for part in enemy.parts:
            self.enemy_sprite_list.remove(part)
        self.physics_engine.remove_sprite(enemy)
        enemy.parts.clear()
        enemy.remove_from_sprite_lists()

        # Update score
        score_change = enemy.health_max * self.multiplier
        self.score += score_change
        self.score_text.text = "Score: " + str(self.score)

        # Update money pool
        self.money_pool += int(score_change / 10)
        money_pool_len = 594.0 * float(self.money_pool) / float(self.round*100)
        money_pool_len = min(594.0, money_pool_len)
        if money_pool_len > 1.0:
            self.money_pool_ui.visible = True
        money_pool_x = self.w/2 - 297 + (money_pool_len/2)
        self.money_pool_ui.width = money_pool_len
        self.money_pool_ui.center_x = money_pool_x
        if self.money_pool >= self.round * 100:
            self.shop_enabled = True
            self.money_ui.alpha = 255
            self.buy_text.text = "[B]"

        if self.last_kill_time == 0:
            self.last_kill_time = self.total_time
            return

        # Update score multiplier
        if self.total_time - self.last_kill_time < 1.0:
            self.multiplier = min(9, self.multiplier + 1)

        if self.multiplier > 1:
            self.multiplier_text.text = "x " + str(self.multiplier)
            self.multiplier_text.font_size = 30 + self.multiplier
            if self.multiplier < 4:
                self.multiplier_text.color = utils.Color.MUL_GREEN
            elif self.multiplier >= 4 and self.multiplier < 6:
                self.multiplier_text.color = utils.Color.MUL_YELLOW
            elif self.multiplier >= 6 and self.multiplier < 8:
                self.multiplier_text.color = utils.Color.MUL_ORANGE
            else:
                self.multiplier_text.color = utils.Color.MUL_RED

        self.last_kill_time = self.total_time

    def check_hit_player(self, enemy: character.Character) -> None:
        if arcade.check_for_collision(enemy, self.player):
            self.player.health = max(
                self.player.health - enemy.hit_damage, 0)
            push = enemy.last_force.normalize().scale(utils.Utils.ENEMY_FORCE)
            self.physics_engine.apply_force(self.player, (push.x, push.y))
            self.player.get_damage_len = utils.Utils.GET_DAMAGE_LEN

    def check_trigger_mine(self, enemy: character.Character) -> None:
        hit_list = arcade.check_for_collision_with_list(
            enemy, self.player_mine_list)
        for mine in hit_list:
            self.set_explosion(mine.position)
            mine.remove_from_sprite_lists()
            self.room.grid[mine.grid_idx[0],
                           mine.grid_idx[1]] = 0

    def set_explosion(self, position: arcade.Point) -> None:
        for _ in range(12):
            particle = effect.Particle(self.explosions_list)
            particle.position = position
            self.explosions_list.append(particle)

            bullet = weapon.ExplosionParticle()
            bullet.position = position
            bullet.life_span = 8
            bullet.change_x = particle.change_x
            bullet.change_y = particle.change_y
            bullet.damage = self.player.explosion_damage
            self.player_bullet_list.append(bullet)

        smoke = effect.Smoke(20)
        smoke.position = position
        self.explosions_list.append(smoke)

        self.shake_camera()
        self.window.play_explosion_sound()

        # Set explosion traces
        for _ in range(20):
            blood = effect.ExplosionTrace()
            blood.position = position
            self.blood_list.append(blood)

    def set_blood(self, position: arcade.Point) -> None:
        for _ in range(12):
            blood = effect.Blood()
            blood.position = position
            self.blood_list.append(blood)

    def manage_level(self) -> None:
        # Round
        if self.counter <= 60:
            self.round_text.text = "3"
        elif self.counter > 60 and self.counter <= 120:
            self.round_text.text = "2"
        elif self.counter > 120 and self.counter <= 180:
            self.round_text.text = "1"
        elif self.counter > 180 and self.counter < 240:
            self.round_text.text = "Start !!!"
        if self.counter == 250:
            self.round_text.text = "Round: 1"
            self.round = 1
            self.spawn_cnt = 1
            self.window.play_round_start_sound()

        # Score multiplier
        if self.total_time - self.last_kill_time > 1.0 and self.multiplier > 1:
            self.multiplier = 1
            self.multiplier_text.text = ""
            self.multiplier_text.font_size = 30
            self.multiplier_text.color = utils.Color.MUL_GREEN

        if self.total_time - self.last_kill_time < 1.0:
            if self.counter % 3 == 0:
                self.multiplier_text.font_size -= 1

        # Spawn enemy and round up
        self.spawn_enemy()
        if len(self.enemy_sprite_list) == 0 and self.spawn_cnt == 0:
            self.round += 1
            self.round_text.text = "Round: " + str(self.round)
            self.spawn_cnt = self.round
            self.window.play_round_start_sound()

        # Update enemies
        self.enemy_white_list.update()
        self.enemy_red_list.update()
        self.enemy_crack_list.update()
        self.enemy_big_mouth_list.update()
        self.enemy_crash_list.update()
        self.enemy_tank_list.update()

    def spawn_enemy(self) -> None:
        """Spawn enemy with different rounds."""

        # Limit the number of enemies for performance issue
        # TODO: Optimized the performance
        if len(self.enemy_sprite_list) >= 800:
            return

        if self.spawn_cnt > 0 and self.round <= 3:
            if self.counter % 60 == 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1

        if self.round > 3 and self.round <= 6:
            if self.counter % 60 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1
            if self.counter % 60 == 30 and self.spawn_cnt > 0:
                self.spawn_enemy_red()
                self.spawn_cnt -= 1

        if self.round > 6 and self.round <= 9:
            if self.counter % 60 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1
            if self.counter % 60 == 30 and self.spawn_cnt > 0:
                self.spawn_enemy_crack()
                self.spawn_cnt -= 1
            if self.counter % 120 == 1 and self.spawn_cnt > 0:
                self.spawn_enemy_red()
                self.spawn_cnt -= 1

        if self.round > 9 and self.round <= 12:
            if self.counter % 40 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_crack()
                self.spawn_cnt -= 1
            if self.counter % 60 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_big_mouth()
                self.spawn_cnt -= 1
            if self.counter % 120 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1
            if self.counter % 120 == 50 and self.spawn_cnt > 0:
                self.spawn_enemy_red()
                self.spawn_cnt -= 1

        if self.round > 12 and self.round <= 15:
            if self.counter % 40 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_crack()
                self.spawn_cnt -= 1
            if self.counter % 60 == 32 and self.spawn_cnt > 0:
                self.spawn_enemy_crash()
                self.spawn_cnt -= 1
            if self.counter % 60 == 50 and self.spawn_cnt > 0:
                self.spawn_enemy_big_mouth()
                self.spawn_cnt -= 1
            if self.counter % 150 == 5 and self.spawn_cnt > 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1
            if self.counter % 180 == 10 and self.spawn_cnt > 0:
                self.spawn_enemy_red()
                self.spawn_cnt -= 1

        if self.round > 15:
            if self.counter % 40 == 0 and self.spawn_cnt > 0:
                self.spawn_enemy_crack()
                self.spawn_cnt -= 1
            if self.counter % 60 == 32 and self.spawn_cnt > 0:
                self.spawn_enemy_crash()
                self.spawn_cnt -= 1
            if self.counter % 60 == 56 and self.spawn_cnt > 0:
                self.spawn_enemy_big_mouth()
                self.spawn_cnt -= 1
            if self.counter % 90 == 3 and self.spawn_cnt > 0:
                self.spawn_enemy_tank()
                self.spawn_cnt -= 2
            if self.counter % 150 == 5 and self.spawn_cnt > 0:
                self.spawn_enemy_white()
                self.spawn_cnt -= 1
            if self.counter % 180 == 10 and self.spawn_cnt > 0:
                self.spawn_enemy_red()
                self.spawn_cnt -= 1

        # if self.round > 15 and self.round <= 18:
        #     # Add boss
        #     pass

    def spawn_enemy_white(self) -> None:
        # Enemy white
        for pos in self.room.spawn_pos:
            enemy = character.EnemyWhite(
                pos.x, pos.y, self.physics_engine, self.player)
            self.enemy_white_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.001,
                                           collision_type="enemy")

    def spawn_enemy_red(self) -> None:
        # Enemy Red
        for pos in self.room.spawn_pos:
            enemy = character.EnemyRed(
                pos.x, pos.y, self.physics_engine, self.player)
            self.enemy_red_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.001,
                                           collision_type="enemy")

    def spawn_enemy_crack(self) -> None:
        # Enemy Crack
        for _ in range(0, 16):
            pos_x = random.randrange(60, self.room.width - 60)
            pos_y = random.randrange(60, self.room.height - 60)
            enemy = character.EnemyCrack(
                pos_x, pos_y, self.physics_engine, self.player)
            self.enemy_crack_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.001,
                                           collision_type="enemy")

    def spawn_enemy_big_mouth(self) -> None:
        # Enemy Big Mouth
        for pos in self.room.spawn_pos:
            enemy = character.EnemyBigMouth(
                pos.x, pos.y, self.physics_engine, self.player)
            self.enemy_big_mouth_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.001,
                                           collision_type="enemy")

    def spawn_enemy_crash(self) -> None:
        # Enemy Crash
        for pos in self.room.spawn_pos:
            enemy = character.EnemyCrash(
                pos.x, pos.y, self.physics_engine, self.player)
            self.enemy_crash_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.05,
                                           collision_type="enemy")

    def spawn_enemy_tank(self) -> None:
        # Enemy Tank
        for pos in self.room.spawn_pos:
            enemy = character.EnemyTank(
                pos.x, pos.y, self.physics_engine, self.player)
            self.enemy_tank_list.append(enemy)
            self.enemy_sprite_list.extend(enemy.parts)
            self.physics_engine.add_sprite(enemy,
                                           friction=0,
                                           moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                           damping=0.001,
                                           collision_type="enemy")


class GameOverView(arcade.View):
    """Game over view."""

    def __init__(self):
        super().__init__()


class GameWinView(arcade.View):
    """Game win view."""

    def __init__(self):
        super().__init__()


class ShopView(arcade.View):
    """Shop view."""

    def __init__(self):
        super().__init__()
        self.manager = None
        self.last_view = None

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.window.set_mouse_visible(True)

    def setup(self, last_view) -> None:
        self.last_view = last_view
        self.player = last_view.player
        self.shop = last_view.shop
        self.cnt = 0
        self.refresh_cost = self.last_view.round + 4
        self.player.money += self.last_view.money_pool

        # Reset money pool of the game view
        self.last_view.money_pool = 0
        self.last_view.money_ui.alpha = 0
        self.last_view.buy_text.text = ""
        self.last_view.money_pool_ui.visible = False

        # UI
        self.w, self.h = self.window.get_size()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)
        self.item_box = arcade.gui.UIBoxLayout(x=self.w/2 + 50,
                                               y=self.h/2 - 50,
                                               vertical=False)

        # Status text
        back_ground = arcade.load_texture("graphics/ui/StatusText.png")
        self.player_text = arcade.gui.UITextArea(x=self.w/2 - 480,
                                                 y=self.h/2 - 160,
                                                 width=250,
                                                 height=400,
                                                 text="",
                                                 text_color=(0, 0, 0, 255))
        self.get_player_text()

        self.manager.add(
            arcade.gui.UITexturePane(
                self.player_text.with_space_around(right=20),
                tex=back_ground,
                padding=(10, 10, 10, 10)
            )
        )

        # Money
        self.coin = arcade.Sprite(filename="graphics/ui/Coin.png",
                                  center_x=self.w/2 - 480,
                                  center_y=self.h/2 + 280,
                                  scale=1)
        self.money_text = arcade.Text(str(self.player.money),
                                      self.w/2 - 420,
                                      self.h/2 + 270,
                                      color=utils.Color.BLACK,
                                      font_size=12,
                                      font_name="FFF Forward",
                                      anchor_x="center")
        self.purchase_text = arcade.Text("",
                                         self.w/2,
                                         self.h/2 + 280,
                                         color=utils.Color.BLACK,
                                         font_size=12,
                                         font_name="FFF Forward",
                                         anchor_x="center")

        # Items
        self.ref_pos = Vec2(self.w/2 - 80, self.h/2 + 100)
        self.item_bg_list = arcade.SpriteList()
        self.item_logo_list = arcade.SpriteList()
        self.item_text = []
        self.item_cost = []
        self.items = None
        self.get_items()

        # Item buttons
        self.item_button_enables = [True, True, True, True]
        item_button_0 = arcade.gui.UIFlatButton(
            text="Buy", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_1 = arcade.gui.UIFlatButton(
            text="Buy", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_2 = arcade.gui.UIFlatButton(
            text="Buy", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_3 = arcade.gui.UIFlatButton(
            text="Buy", width=80, style=utils.Style.BUTTON_DEFAULT
        )
        self.item_box.add(item_button_0.with_space_around(left=80, right=80))
        self.item_box.add(item_button_1.with_space_around(right=80))
        self.item_box.add(item_button_2.with_space_around(right=80))
        self.item_box.add(item_button_3.with_space_around(right=80))
        item_button_0.on_click = self.on_click_item_0
        item_button_1.on_click = self.on_click_item_1
        item_button_2.on_click = self.on_click_item_2
        item_button_3.on_click = self.on_click_item_3

        # Refresh button
        self.refresh_cost_text = arcade.Text(str(self.refresh_cost),
                                             start_x=self.w/2 + 100,
                                             start_y=self.h/2 - 160,
                                             color=utils.Color.BLACK,
                                             font_size=12,
                                             font_name="FFF Forward",
                                             anchor_x="center")
        refresh_button = arcade.gui.UIFlatButton(text="Refresh (D)",
                                                 x=self.w/2 + 120,
                                                 y=self.h/2 - 170,
                                                 width=120,
                                                 style=utils.Style.BUTTON_DEFAULT)
        self.manager.add(refresh_button)
        refresh_button.on_click = self.on_click_refresh

        # Rest buttons
        start_view_button = arcade.gui.UIFlatButton(
            text="Start Menu", width=180, style=utils.Style.BUTTON_DEFAULT
        )
        continue_button = arcade.gui.UIFlatButton(
            text="Continue", width=120, style=utils.Style.BUTTON_DEFAULT
        )
        self.rest_box.add(start_view_button.with_space_around(right=280))
        self.rest_box.add(continue_button.with_space_around(right=0))
        continue_button.on_click = self.on_click_continue
        start_view_button.on_click = self.on_click_start_menu

        # Add box layout
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_x=160, align_y=-80, child=self.item_box))
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=-240, child=self.rest_box))

    def on_update(self, delta_time: float) -> None:
        self.item_bg_list.update()
        self.item_logo_list.update()
        self.get_player_text()
        self.money_text.text = str(self.player.money)
        if self.cnt > 0:
            self.cnt -= 1
        elif self.cnt == 0:
            self.purchase_text.text = ""
        self.refresh_cost_text.text = str(self.refresh_cost)

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()
        self.coin.draw()
        self.purchase_text.draw()
        self.money_text.draw()
        self.item_bg_list.draw()
        self.item_logo_list.draw()
        for description in self.item_text:
            description.draw()
        for cost in self.item_cost:
            cost.draw()
        self.refresh_cost_text.draw()

    def on_click_continue(self, event) -> None:
        # Clear the game view reference
        self.player = None
        self.shop = None
        utils.Utils.clear_ui_manager(self.manager)
        self.last_view.resize_camera(self.window.width, self.window.height)
        self.window.show_view(self.last_view)
        self.window.play_button_sound()

    def on_click_start_menu(self, event) -> None:
        # Clear the game view reference
        self.player = None
        self.shop = None
        self.last_view = None
        utils.Utils.clear_ui_manager(self.manager)
        self.window.start_view.setup()
        self.window.start_view.resize_camera(
            self.window.width, self.window.height)
        self.window.show_view(self.window.start_view)
        self.window.play_button_sound()

    def get_player_text(self) -> None:
        text = "Player status:\n"
        text += "- Health: " + str(self.player.health) + "\n"
        text += "- Energy: " + str(self.player.energy) + "\n"
        text += "- Recover after kill: " + str(self.player.kill_recover) + "\n"
        text += "- Luck: " + str(self.player.luck) + "\n"
        text += "- Explosion damage: " + \
            str(self.player.explosion_damage) + "\n"
        text += "\n"

        text += "Pistol:\n"
        text += "- Damage: " + str(self.shop.pistol.damage) + "\n"
        text += "- CD: " + str(self.shop.pistol.cd_max) + "\n"
        text += "- Attack range: " + str(self.shop.pistol.life_span) + "\n"
        text += "\n"

        if self.player.weapons.count(self.shop.uzi) > 0:
            text += "Uzi:\n"
            text += "- Damage: " + str(self.shop.uzi.damage) + "\n"
            text += "- CD: " + str(self.shop.uzi.cd_max) + "\n"
            text += "- Attack range: " + str(self.shop.uzi.life_span) + "\n"
            text += "- Energy cost: " + str(self.shop.uzi.cost) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.shotgun) > 0:
            text += "Shotgun:\n"
            text += "- Damage: " + str(self.shop.shotgun.damage) + "\n"
            text += "- CD: " + str(self.shop.shotgun.cd_max) + "\n"
            text += "- Attack range: " + \
                str(self.shop.shotgun.life_span) + "\n"
            text += "- Energy cost: " + str(self.shop.shotgun.cost) + "\n"
            text += "- Bullet numbers: " + \
                str(self.shop.shotgun.bullet_num) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.rocket) > 0:
            text += "Rocket:\n"
            text += "- Damage: " + str(self.shop.rocket.damage) + "\n"
            text += "- CD: " + str(self.shop.rocket.cd_max) + "\n"
            text += "- Attack range: " + str(self.shop.rocket.life_span) + "\n"
            text += "- Energy cost: " + str(self.shop.rocket.cost) + "\n"
            text += "- Bullet numbers: " + \
                str(self.shop.rocket.bullet_num) + "\n"
            text += "\n"

        self.player_text.text = text

    def get_items(self) -> None:
        self.items = self.shop.get_items(self.last_view.round, self.player)
        for i in range(0, 4):
            # Item background
            bg = arcade.Sprite()
            bg.center_x = self.ref_pos.x + i*160
            bg.center_y = self.ref_pos.y + 20
            if self.items[i].quality == 1:
                bg.texture = arcade.load_texture("graphics/ui/BronzeTier.png")
            elif self.items[i].quality == 2:
                bg.texture = arcade.load_texture("graphics/ui/SliverTier.png")
            elif self.items[i].quality == 3:
                bg.texture = arcade.load_texture("graphics/ui/GoldTier.png")
            else:
                bg.texture = arcade.load_texture("graphics/ui/SpecialTier.png")
            bg.scale = 1.5
            self.item_bg_list.append(bg)

            # Item logo
            logo = arcade.Sprite()
            logo.texture = arcade.load_texture("graphics/item/PlaceHolder.png")
            logo.center_x = self.ref_pos.x + i*160
            logo.center_y = self.ref_pos.y + 120
            self.item_logo_list.append(logo)

            # Item text
            description = arcade.Text(
                self.items[i].description,
                self.ref_pos.x + i*160,
                self.ref_pos.y + 60,
                width=120,
                color=utils.Color.BLACK,
                font_size=14,
                font_name="Source Han Sans Old Style Normal",
                anchor_x="center",
                align="center",
                multiline=True,
            )
            self.item_text.append(description)

            # Item cost
            cost_text = self.items[i].cost if self.items[i].cost > 0 \
                else -self.items[i].cost
            cost_color = utils.Color.DARK_GRAY if self.items[i].cost > 0 \
                else utils.Color.BRIGHT_GREEN
            cost = arcade.Text(
                str(cost_text),
                self.ref_pos.x + i*160,
                self.ref_pos.y - 60,
                width=120,
                color=cost_color,
                font_size=12,
                font_name="FFF Forward",
                anchor_x="center",
                align="center",
                multiline=True,
            )
            self.item_cost.append(cost)

    def update_purchase_text(self, sign: int) -> None:
        if sign == 0:  # purchase success
            self.purchase_text.text = "Purchase succeeded."
            self.purchase_text.color = utils.Color.BRIGHT_GREEN
        elif sign == 1:  # purchase failed
            self.purchase_text.text = "Purchase failed."
            self.purchase_text.color = utils.Color.HEALTH_RED
        elif sign == 2:  # refresh failed
            self.purchase_text.text = "Refresh failed."
            self.purchase_text.color = utils.Color.HEALTH_RED

        self.cnt = 60

    def purchase_item(self, index: int) -> None:
        if self.player.money < self.items[index].cost:
            # Not enough money
            self.update_purchase_text(1)
            self.window.play_purchase_fail_sound()
            return

        if self.items[index].equip(self.items[index], self.player):
            # Deal with the button

            # Remove item visuals
            self.item_bg_list[index].alpha = 0
            self.item_logo_list[index].alpha = 0
            self.item_text[index].text = ""
            self.item_cost[index].text = ""

            # Purchase succeed
            self.player.money -= self.items[index].cost
            self.update_purchase_text(0)
            self.item_button_enables[index] = False
            self.window.play_purchase_sound()
        else:
            # Purchase failed
            self.update_purchase_text(1)
            self.window.play_purchase_fail_sound()

    def on_click_refresh(self, event) -> None:
        if self.player.money < self.refresh_cost:
            self.update_purchase_text(2)
            self.window.play_purchase_fail_sound()
            return
        self.player.money -= self.refresh_cost
        self.refresh_cost += self.last_view.round
        self.window.play_refresh_sound()

        # Clear item list
        self.item_bg_list.clear()
        self.item_logo_list.clear()
        self.item_text.clear()
        self.item_cost.clear()
        self.item_button_enables = [True, True, True, True]

        self.get_items()

    def on_click_item_0(self, event) -> None:
        if self.item_button_enables[0]:
            self.purchase_item(0)

    def on_click_item_1(self, event) -> None:
        if self.item_button_enables[1]:
            self.purchase_item(1)

    def on_click_item_2(self, event) -> None:
        if self.item_button_enables[2]:
            self.purchase_item(2)

    def on_click_item_3(self, event) -> None:
        if self.item_button_enables[3]:
            self.purchase_item(3)
