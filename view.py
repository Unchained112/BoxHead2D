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
            self.window.cur_lang.PRESS_ANY_KEY,
            self.w / 2,
            self.h / 2 - 100,
            color=(0, 0, 0, 250),
            font_size=24,
            font_name="Cubic 11",
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
        self.player.register_mouse_pos(self.mouse_pos)

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
                                      font_name="Cubic 11",
                                      anchor_x="center")
        self.about_text_shadow = arcade.Text("Created by Unchain.",
                                             self.w - 602,
                                             120,
                                             color=utils.Color.LIGHT_GRAY,
                                             font_size=14,
                                             font_name="Cubic 11",
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
            text=self.window.cur_lang.START, width=150, style=utils.Style.BUTTON_DEFAULT
        )
        option_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.OPTION, width=150, style=utils.Style.BUTTON_DEFAULT
        )
        quit_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.QUIT, width=150, style=utils.Style.BUTTON_DEFAULT
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

        self.name_list = []
        self.describe_list = []
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.selection_box = arcade.gui.UIBoxLayout(vertical=False)
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)

        # Characters
        self.char_sprites = arcade.SpriteList()
        self.char_list = [
            character.Player,
            character.Rambo,
            character.Redbit,
        ]
        self.cur_char_idx = 0
        self.cur_char = character.Character(
            float(self.w/2 - 240), float(self.h/2 + 100))
        self.name_list.append(
            arcade.Text(
                text="",
                start_x=float(self.w/2 - 240),
                start_y=float(self.h/2 + 20),
                font_size=12,
                font_name="Cubic 11",
                anchor_x="center",
                align="center",
                width=120,
                color=utils.Color.BLACK,
            )
        )
        self.describe_list.append(
            arcade.Text(
                text="",
                start_x=float(self.w/2 - 240),
                start_y=float(self.h/2 - 10),
                font_size=12,
                font_name="Cubic 11",
                anchor_x="center",
                align="center",
                multiline=False,
                width=240,
                color=utils.Color.BLACK,
            )
        )
        self.set_character()

        # Maps
        self.map_list = [
            room.GameRoom0,
            room.GameRoom1,
            room.GameRoom2,
        ]
        self.cur_map_idx = 0
        self.cur_map = self.map_list[self.cur_map_idx]
        self.cur_map_sprite = arcade.Sprite()
        self.name_list.append(
            arcade.Text(
                text="",
                start_x=float(self.w/2 + 220),
                start_y=float(self.h/2 - 20),
                font_size=12,
                font_name="Cubic 11",
                anchor_x="center",
                align="center",
                width=120,
                color=utils.Color.BLACK,
            )
        )
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
            text=self.window.cur_lang.BACK, width=120, style=utils.Style.BUTTON_DEFAULT
        )
        next_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.NEXT, width=120, style=utils.Style.BUTTON_DEFAULT
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
        self.name_list[0].text = self.window.cur_lang.DescribeText[
            self.char_list[self.cur_char_idx].name]
        self.describe_list[0].text = self.window.cur_lang.DescribeText[
            self.char_list[self.cur_char_idx].description]

    def set_maps(self, idx: int = 0) -> None:
        self.cur_map_idx += idx
        self.cur_map_idx %= len(self.map_list)
        self.cur_map = self.map_list[self.cur_map_idx]
        self.cur_map_sprite = self.cur_map.layout_sprite
        self.cur_map_sprite.center_x = float(self.w/2 + 220)
        self.cur_map_sprite.center_y = float(self.h/2 + 70)
        self.name_list[1].text = self.window.cur_lang.DescribeText[
            self.map_list[self.cur_map_idx].name]

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.char_sprites.draw()
        self.cur_map_sprite.draw()
        for name in self.name_list:
            name.draw()
        for des in self.describe_list:
            des.draw()

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
        self.lang_box = arcade.gui.UIBoxLayout(vertical=False)
        self.effect_volume_box = arcade.gui.UIBoxLayout(vertical=False)
        self.music_volume_box = arcade.gui.UIBoxLayout(vertical=False)
        self.screen_box = arcade.gui.UIBoxLayout(vertical=False)
        self.resolution_box = arcade.gui.UIBoxLayout(vertical=False)
        self.rest_box = arcade.gui.UIBoxLayout(vertical=False)

        # Language settings
        lang_label = arcade.gui.UITextArea(
            text=self.window.cur_lang.LANG,
            width=200,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        lang_left_button = arcade.gui.UIFlatButton(
            text="<", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        lang_text = arcade.gui.UITextArea(
            text=self.window.cur_lang.CUR_LANG,
            width=120,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        lang_right_button = arcade.gui.UIFlatButton(
            text=">", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.lang_box.add(
            lang_label.with_space_around(right=20))
        self.lang_box.add(
            lang_left_button.with_space_around(right=20)
        )
        self.lang_box.add(
            lang_text.with_space_around(right=10))
        self.lang_box.add(
            lang_right_button.with_space_around(right=0))
        lang_left_button.on_click = self.on_click_lang_left
        lang_right_button.on_click = self.on_click_lang_right

        # Effect volume settings
        effect_volume_label = arcade.gui.UITextArea(
            text=self.window.cur_lang.EFFECT_VOLUME,
            width=300,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        effect_volume_down_button = arcade.gui.UIFlatButton(
            text="-", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.effect_volume_text = arcade.gui.UITextArea(
            text=str(self.window.effect_volume),
            width=40,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
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
            text=self.window.cur_lang.MUSIC_VOLUME,
            width=300,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        music_volume_down_button = arcade.gui.UIFlatButton(
            text="-", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.music_volume_text = arcade.gui.UITextArea(
            text=str(self.window.music_volume),
            width=40,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
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
            text=self.window.cur_lang.FULLSCREEN,
            width=200,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        self.fullscreen_text = arcade.gui.UITextArea(
            text=str(self.window.fullscreen),
            width=120,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        fullscreen_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.SWITCH, width=120, style=utils.Style.BUTTON_DEFAULT
        )
        self.screen_box.add(fullscreen_label.with_space_around(right=20))
        self.screen_box.add(self.fullscreen_text.with_space_around(right=20))
        self.screen_box.add(fullscreen_button.with_space_around(right=0))
        fullscreen_button.on_click = self.on_click_fullscreen

        # Resolution settings
        resolution_label = arcade.gui.UITextArea(
            text=self.window.cur_lang.RESOLUTION,
            width=200,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        resolution_down_button = arcade.gui.UIFlatButton(
            text="<", width=60, style=utils.Style.BUTTON_DEFAULT
        )
        self.resolution_text = arcade.gui.UITextArea(
            text="1280 x 720",
            width=200,
            height=40,
            font_size=24,
            text_color=utils.Color.BLACK,
            font_name="Cubic 11",
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
            self.resolution_text.text = self.window.cur_lang.FULLSCREEN
        else:
            self.resolution_text.text = str(
                self.window.w_scale[self.window.res_index]) + " x " + str(self.window.h_scale[self.window.res_index])
        self.resolution_box.add(
            resolution_up_button.with_space_around(right=0))
        resolution_up_button.on_click = self.on_click_resolution_up
        resolution_down_button.on_click = self.on_click_resolution_down

        # Rest buttons
        back_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.BACK, width=120, style=utils.Style.BUTTON_DEFAULT
        )
        start_view_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.START_MENU, width=180, style=utils.Style.BUTTON_DEFAULT
        )
        quit_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.QUIT, width=120, style=utils.Style.BUTTON_DEFAULT
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
                align_y=220, child=self.lang_box)
        )
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_y=140, child=self.effect_volume_box)
        )
        self.manager.add(
            arcade.gui.UIAnchorWidget(align_y=60, child=self.music_volume_box)
        )
        self.manager.add(arcade.gui.UIAnchorWidget(
            align_y=-20, child=self.screen_box))
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
            self.resolution_text.text = self.window.cur_lang.FULLSCREEN
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

    def on_click_lang_left(self, event) -> None:
        idx = self.window.lang_idx - 1
        idx = idx % len(self.window.lang)
        self.window.set_cur_lang(idx)
        self.setup(self.last_view)

    def on_click_lang_right(self, event) -> None:
        idx = self.window.lang_idx + 1
        idx = idx % len(self.window.lang)
        self.window.set_cur_lang(idx)
        self.setup(self.last_view)


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
        self.pool_size: int = 0
        self.round_text = arcade.Text("", self.w / 2,
                                      self.h - 50, utils.Color.BLACK,
                                      16, 2, "left", "Cubic 11")
        self.multiplier_text = arcade.Text("", self.w - 200,
                                           self.h - 140, utils.Color.MUL_GREEN,
                                           40, 2, "left", "FFF Forward")
        self.score_text = arcade.Text("Score: " + str(self.score), self.w - 240,
                                      self.h - 50, utils.Color.BLACK,
                                      16, 2, "left", "Cubic 11")

        self.window.set_mouse_visible(False)
        self.counter: int = -250  # assume 60 frames -> 60 = 1s
        self.total_time = 0
        self.last_kill_time = 0
        self.shop_enabled = False  # Enable if money_pool >= round * 100
        self.all_item_list = []

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
                                    14, 2, "left", "Cubic 11")
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
        self.money_pool_len = 0
        self.money_pool_x = 0

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

        self.on_damage_filter = arcade.SpriteSolidColor(self.w + 10,
                                                        self.h + 10,
                                                        utils.Color.RED_LIGHT_TRANS)
        self.on_damage_filter.center_x = self.w / 2
        self.on_damage_filter.center_y = self.h / 2
        self.on_damage_filter.visible = False
        self.on_explosion_filter = arcade.SpriteSolidColor(self.w + 10,
                                                           self.h + 10,
                                                           utils.Color.WHITE_TRANSPARENT)
        self.on_explosion_filter.center_x = self.w / 2
        self.on_explosion_filter.center_y = self.h / 2
        self.on_explosion_filter.visible = False
        self.ui_sprite_list.append(self.on_damage_filter)
        self.ui_sprite_list.append(self.on_explosion_filter)

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
        self.explosion_visual_list = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()
        self.boss_bullet_list = arcade.SpriteList()

        # Create the physics engine
        damping = 0.01
        gravity = (0, 0)
        self.physics_engine = PymunkPhysicsEngine(gravity, damping)

        # Game room setup
        self.room = map()
        self.wall_list = self.room.walls

        # Path-finding
        self.dir_field = dict()
        self.dist_grid = None
        if utils.Utils.IS_TESTING_PF:
            self.dir_field_visual = arcade.SpriteList()
            self.dir_visual_dict = dict()
            for pos in self.room.grid:
                self.dir_visual_dict[pos] = arcade.SpriteSolidColor(
                    30, 30, (0, 255, 0, 150))
                self.dir_visual_dict[pos].center_x = pos[0] * 30 + 15
                self.dir_visual_dict[pos].center_y = pos[1] * 30 + 15
                self.dir_field_visual.append(self.dir_visual_dict[pos])

        # Set up the player
        self.player = player(
            float(self.room.width / 2), float(self.room.height / 2), self.physics_engine)
        self.player.register_mouse_pos(self.mouse_pos)

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
        self.explosion_visual_list.draw()
        self.boss_bullet_list.draw()

        if utils.Utils.IS_TESTING_PF:
            self.dir_field_visual.draw()

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
        self.window.explosion_sound_cnt = max(
            self.window.explosion_sound_cnt - 1,
            0
        )

        # Update player
        self.player.update()
        self.update_player_attack()
        self.process_player_bullet()
        self.process_player_explosion()

        # Update level
        self.manage_level()
        self.enemy_sprite_list.update()
        self.update_enemy_attack()
        self.process_enemy_bullet()
        self.update_boss()

        self.explosions_list.update()
        self.blood_list.update()

        self.scroll_to_player()

        # Check game over
        if self.player.health <= 0:
            self.window.game_over_view.setup(self.all_item_list, self.score)
            self.window.show_view(self.window.game_over_view)
            self.window.play_game_over_sound()

        # Check player getting damage
        if self.player.get_damage_len > 0:
            self.on_damage_filter.visible = True
        else:
            self.on_damage_filter.visible = False

        # Check explosion
        if len(self.explosions_list) > 0:
            self.on_explosion_filter.visible = True
        else:
            self.on_explosion_filter.visible = False

            # Update path finding field (function still in testing)
        if self.counter % 30 == 0:
            self.dist_grid = utils.Utils.field_path_finding(self.player.center_x,
                                                            self.player.center_y,
                                                            self.room.grid,
                                                            self.room.grid_w,
                                                            self.room.grid_h,
                                                            self.dir_field)
        if utils.Utils.IS_TESTING_PF:
            for pos in self.dir_visual_dict:
                alpha = min(255, -self.dist_grid.get(pos, -255) * 3)
                self.dir_visual_dict[pos].alpha = alpha

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

        if utils.Utils.IS_TESTING:
            if key == arcade.key.B:
                self.window.shop_view.setup(self)
                self.window.show_view(self.window.shop_view)

            if key == arcade.key.X:
                self.window.game_over_view.setup(
                    self.all_item_list, self.score)
                self.window.show_view(self.window.game_over_view)

            if key == arcade.key.V:
                self.window.game_win_view.setup(self.all_item_list, self.score)
                self.window.show_view(self.window.game_win_view)

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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.is_attack = True
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.use_skill()

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
        shake_amplitude = 2
        # Calculate a vector based on that
        shake_vector = Vec2(
            math.cos(shake_direction) * shake_amplitude,
            math.sin(shake_direction) * shake_amplitude
        )
        # Frequency of the shake
        shake_speed = 1
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
        self.buy_text.x = self.w/2 + 340
        self.money_pool_x = self.w/2 - 297 + (self.money_pool_len/2)
        self.money_pool_ui.center_x = self.money_pool_x
        self.on_damage_filter.width = self.w + 10
        self.on_damage_filter.height = self.h + 10
        self.on_explosion_filter.width = self.w + 10
        self.on_explosion_filter.height = self.h + 10
        self.on_damage_filter.center_x = self.w / 2
        self.on_damage_filter.center_y = self.h / 2
        self.on_explosion_filter.center_x = self.w / 2
        self.on_explosion_filter.center_y = self.h / 2

    def draw_ui(self) -> None:
        # Health
        arcade.draw_text(text=int(self.player.health),
                         start_x=100,
                         start_y=self.h - 50,
                         color=utils.Color.HEALTH_RED,
                         font_size=16,
                         width=2,
                         align="left",
                         font_name="Cubic 11")

        # Energy
        arcade.draw_text(text=int(self.player.energy),
                         start_x=100,
                         start_y=self.h - 80,
                         color=utils.Color.ENERGY_BLUE,
                         font_size=16,
                         width=2,
                         align="left",
                         font_name="Cubic 11")

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

                    try:
                        self.room.grid[grid_x, grid_y]
                    except KeyError:
                        return

                    if self.room.grid[grid_x, grid_y] == 0:
                        object.center_x = grid_x * 30 + \
                            float(utils.Utils.HALF_WALL_SIZE)
                        object.center_y = grid_y * 30 + \
                            float(utils.Utils.HALF_WALL_SIZE)
                        object.grid_idx = (grid_x, grid_y)
                        if object.object_type != 2:  # not a mine
                            self.player_object_list.append(object)
                            self.physics_engine.add_sprite(object,
                                                           friction=0,
                                                           collision_type="object",
                                                           body_type=PymunkPhysicsEngine.STATIC)
                        else:
                            self.player_mine_list.append(object)

                        # Differentiate the number from the real wall
                        self.room.grid[grid_x, grid_y] = 2 + object.object_type
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

            if type(bullet) == weapon.ExplosionSeed:
                if bullet.life_span <= 0:
                    self.set_explosion(bullet.position)
                else:
                    continue

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
                    self.boss_list,
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
                    self.player.health_recover()
                    self.remove_enemy(enemy)

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    if self.player.is_rocket_multi:
                        self.set_multi_explosion(bullet.position)
                    else:
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
                        if self.player.is_barrel_multi:
                            self.set_multi_explosion(object.position)
                        else:
                            self.set_explosion(object.position)
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    if self.player.is_rocket_multi:
                        self.set_multi_explosion(bullet.position)
                    else:
                        self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()
                continue

            # Check hit with room walls
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                if type(bullet) == weapon.Missile:
                    if self.player.is_rocket_multi:
                        self.set_multi_explosion(bullet.position)
                    else:
                        self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()
                continue

            if bullet.life_span <= 0:
                if type(bullet) == weapon.Missile:
                    if self.player.is_rocket_multi:
                        self.set_multi_explosion(bullet.position)
                    else:
                        self.set_explosion(bullet.position)
                bullet.remove_from_sprite_lists()

    def process_player_explosion(self) -> None:
        # Update explosion visual
        self.explosion_visual_list.update()

        # Process explosion
        for explosion in self.explosions_list:
            if explosion.life_span == 5:
                hit_list = arcade.check_for_collision_with_lists(
                    explosion,
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
                    enemy.health -= self.player.explosion_damage
                    self.set_blood(enemy.position)
                    self.player.energy += (self.player.explosion_damage/10)
                    aim_x = (enemy.center_x - explosion.center_x) * \
                        utils.Utils.BULLET_FORCE
                    aim_y = (enemy.center_y - explosion.center_y) * \
                        utils.Utils.BULLET_FORCE
                    self.physics_engine.apply_force(enemy, (aim_x, aim_y))
                    enemy.get_damage_len = utils.Utils.GET_DAMAGE_LEN
                    if enemy.health <= 0:
                        self.player.health_recover()
                        self.remove_enemy(enemy)

                hit_list = arcade.check_for_collision_with_list(
                    explosion, self.player_object_list)

                for object in hit_list:
                    if object.object_type == 0:  # Wall object
                        object.health -= self.player.explosion_damage
                        if object.health <= 0:
                            self.room.grid[object.grid_idx[0],
                                           object.grid_idx[1]] = 0
                            object.remove_from_sprite_lists()
                    if object.object_type == 1:  # Barrel object
                        object.health -= self.player.explosion_damage
                        if object.health <= 0:
                            if self.player.is_barrel_multi:
                                self.set_multi_explosion(object.position)
                            else:
                                self.set_explosion(object.position)
                            self.room.grid[object.grid_idx[0],
                                           object.grid_idx[1]] = 0
                            object.remove_from_sprite_lists()

    def update_enemy_attack(self) -> None:
        # Enemy White
        for enemy in self.enemy_white_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            self.check_hit_wall(enemy)

        # Enemy Red
        for enemy in self.enemy_red_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            self.check_hit_wall(enemy)
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
            self.check_hit_wall(enemy)

        # Enemy Big Mouth
        for enemy in self.enemy_big_mouth_list:
            self.check_hit_player(enemy)
            self.check_trigger_mine(enemy)
            self.check_hit_wall(enemy)
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
            self.check_hit_wall(enemy)
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
            self.check_hit_wall(enemy)
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

            # Check hit with player
            chance = random.randrange(0, 100)
            if chance >= self.player.luck and arcade.check_for_collision(bullet, self.player):
                self.player.get_damage(bullet.damage)
                bullet.remove_from_sprite_lists()
                self.physics_engine.apply_force(
                    self.player, (bullet.aim.x * utils.Utils.BULLET_FORCE,
                                  bullet.aim.y * utils.Utils.BULLET_FORCE))
                self.player.get_damage_len = utils.Utils.GET_DAMAGE_LEN
                self.set_blood(self.player.position)
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
                        if self.player.is_barrel_multi:
                            self.set_multi_explosion(object.position)
                        else:
                            self.set_explosion(object.position)
                        self.room.grid[object.grid_idx[0],
                                       object.grid_idx[1]] = 0
                        object.remove_from_sprite_lists()

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                continue

            # Check hit with room walls
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                continue

            if bullet.life_span <= 0:
                bullet.remove_from_sprite_lists()

    def update_boss(self) -> None:
        # Update boss actions
        for boss in self.boss_list:
            if type(boss) == character.BossRed:
                self.check_hit_player(boss)
                self.check_trigger_mine(boss)
                self.check_hit_wall(boss)
                if boss.is_walking == False:  # only appear in phase 1
                    if boss.cd == boss.cd_max:
                        boss.cd = 0
                    if boss.cd < 40:
                        boss.dash()
                        if boss.cd % 15 == 0:
                            bullets = boss.shoot_ring()
                            self.enemy_bullet_list.extend(bullets)
                if boss.health <= 2100:  # phase 2
                    if boss.cd == boss.cd_max:
                        boss.cd = 0
                    if boss.cd == 0:
                        bullets = boss.shoot_around(self.room.width,
                                                    self.room.height)
                        self.boss_bullet_list.extend(bullets)

                boss.cd = min(boss.cd + 1, boss.cd_max)

        # Process boss bullets
        for bullet in self.boss_bullet_list:
            if bullet.life_span == 5:
                bullet.alpha = 255
                # Check hit with player
                chance = random.randrange(0, 100)
                if chance >= self.player.luck and arcade.check_for_collision(bullet, self.player):
                    self.player.get_damage(bullet.damage)
                    bullet.remove_from_sprite_lists()
                    self.player.get_damage_len = utils.Utils.GET_DAMAGE_LEN
                    self.set_blood(self.player.position)
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
                            if self.player.is_barrel_multi:
                                self.set_multi_explosion(object.position)
                            else:
                                self.set_explosion(object.position)
                            self.room.grid[object.grid_idx[0],
                                           object.grid_idx[1]] = 0
                            object.remove_from_sprite_lists()

                if len(hit_list) > 0:
                    bullet.remove_from_sprite_lists()
                    continue
            else:
                bullet.alpha = 150
            if bullet.life_span <= 1:
                bullet.remove_from_sprite_lists()
            bullet.life_span -= 1

    def remove_enemy(self, enemy: character.Character) -> None:
        enemy.physics_engines.clear()  # to avoid key error
        for part in enemy.parts:
            self.enemy_sprite_list.remove(part)
        self.physics_engine.remove_sprite(enemy)
        enemy.parts.clear()
        enemy.remove_from_sprite_lists()

        # Update score
        self.score += enemy.health_max * self.multiplier
        self.score_text.text = "Score: " + str(self.score)

        # Update money pool
        self.money_pool += int(enemy.health_max/10 + self.multiplier)
        self.money_pool_len = 594.0 * \
            float(self.money_pool) / float(self.pool_size)
        self.money_pool_len = min(594.0, self.money_pool_len)
        if self.money_pool_len > 1.0:
            self.money_pool_ui.visible = True
        self.money_pool_x = self.w/2 - 297 + (self.money_pool_len/2)
        self.money_pool_ui.width = self.money_pool_len
        self.money_pool_ui.center_x = self.money_pool_x
        if self.money_pool >= self.pool_size:
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
        if self.counter % 10 != 0:  # check every 1/6 s
            return

        # Check player luck
        chance = random.randrange(0, 100)
        if chance < self.player.luck:
            return

        # Check collision
        if arcade.check_for_collision(enemy, self.player):
            self.player.get_damage(enemy.hit_damage)
            push = enemy.force.normalize().scale(utils.Utils.ENEMY_FORCE)
            self.physics_engine.apply_force(self.player, (push.x, push.y))
            self.player.get_damage_len = utils.Utils.GET_DAMAGE_LEN
            self.set_blood(self.player.position)

    def check_trigger_mine(self, enemy: character.Character) -> None:
        hit_list = arcade.check_for_collision_with_list(
            enemy, self.player_mine_list)
        for mine in hit_list:
            if self.player.is_mine_multi:
                self.set_multi_explosion(mine.position)
            else:
                self.set_explosion(mine.position)
            mine.remove_from_sprite_lists()
            self.room.grid[mine.grid_idx[0],
                           mine.grid_idx[1]] = 0

    def check_hit_wall(self, enemy: character.Character) -> None:
        if self.counter % 20 != 0:  # check every 1/6 s
            return
        hit_list = arcade.check_for_collision_with_list(
            enemy, self.player_object_list)
        for obj in hit_list:
            if obj.object_type != 0:
                continue
            obj.health -= enemy.hit_damage
            if obj.health <= 0:
                self.room.grid[obj.grid_idx[0],
                               obj.grid_idx[1]] = 0
                obj.remove_from_sprite_lists()

    def set_explosion(self, position: arcade.Point) -> None:
        # Add explosion visual
        for _ in range(18):
            particle = effect.Particle(self.explosion_visual_list)
            particle.position = position
            self.explosion_visual_list.append(particle)

        # Add logic explosion
        explosion = weapon.Explosion(position[0], position[1])
        self.explosions_list.append(explosion)

        self.shake_camera()
        self.window.play_explosion_sound()

        # Set explosion traces
        for _ in range(12):
            blood = effect.ExplosionTrace()
            blood.position = position
            self.blood_list.append(blood)

    def set_multi_explosion(self, position: arcade.Point) -> None:
        self.set_explosion(position)
        for _ in range(3):
            speed = 2
            direction = random.randrange(360)
            change_x = math.sin(math.radians(direction)) * speed
            change_y = math.cos(math.radians(direction)) * speed
            explosion_seed = weapon.ExplosionSeed()
            explosion_seed.position = position
            explosion_seed.change_x = change_x
            explosion_seed.change_y = change_y
            explosion_seed.life_span = 20
            explosion_seed.damage = 0
            self.player_bullet_list.append(explosion_seed)

    def set_blood(self, position: arcade.Point) -> None:
        for _ in range(12):
            blood = effect.Blood()
            blood.position = position
            self.blood_list.append(blood)

    def manage_level(self) -> None:
        # Round
        if self.counter <= -190:
            self.round_text.text = "3"
        elif self.counter > -190 and self.counter <= -130:
            self.round_text.text = "2"
        elif self.counter > -130 and self.counter <= -70:
            self.round_text.text = "1"
        elif self.counter > -70 and self.counter < -10:
            self.round_text.text = "Start !!!"
        if self.counter == 0:
            self.spawn_cnt = 0
            self.pool_size = 80

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
            self.counter = 0  # reset the counter
            self.spawn_cnt = self.round * 8  # num of enemies: round * 8
            if self.round < 21:
                self.window.play_round_start_sound()
            if self.round == 21:  # Game win
                self.window.game_win_view.setup(self.all_item_list, self.score)
                self.window.show_view(self.window.game_win_view)
                self.window.play_game_win_sound()

        # Update enemies
        self.enemy_white_list.update()
        self.enemy_red_list.update()
        self.enemy_crack_list.update()
        self.enemy_big_mouth_list.update()
        self.enemy_crash_list.update()
        self.enemy_tank_list.update()
        self.boss_list.update()

    def spawn_enemy(self) -> None:
        """Spawn enemy with different rounds."""

        # Testing
        if utils.Utils.IS_TESTING:
            if self.spawn_cnt > 0:
                # self.set_boss(character.BossRed)
                self.generate_enemy(1, character.EnemyWhite,
                                    self.enemy_white_list)
                self.generate_enemy(1, character.EnemyWhite,
                                    self.enemy_white_list)
                self.generate_enemy(1, character.EnemyRed,
                                    self.enemy_red_list)
                self.generate_enemy(1, character.EnemyRed,
                                    self.enemy_red_list)
                self.generate_enemy(1, character.EnemyCrack,
                                    self.enemy_crack_list)
                self.generate_enemy(1, character.EnemyCrack,
                                    self.enemy_crack_list)
                self.generate_enemy(1, character.EnemyBigMouth,
                                    self.enemy_big_mouth_list)
                self.generate_enemy(1, character.EnemyBigMouth,
                                    self.enemy_big_mouth_list)
                self.generate_enemy(1, character.EnemyCrash,
                                    self.enemy_crash_list)
                self.generate_enemy(1, character.EnemyCrash,
                                    self.enemy_crash_list)
                self.generate_enemy(1, character.EnemyTank,
                                    self.enemy_tank_list)
                self.generate_enemy(1, character.EnemyTank,
                                    self.enemy_tank_list)
                self.spawn_cnt = 0
            return

        if self.round <= 2:
            if self.counter % 30 == 0:
                self.generate_enemy(1, character.EnemyWhite,
                                    self.enemy_white_list)

        if self.round > 2 and self.round <= 4:
            if self.counter % 30 == 0:
                if self.counter < 3600 and self.spawn_cnt > self.round:
                    self.generate_enemy(1, character.EnemyWhite,
                                        self.enemy_white_list)
                else:
                    self.generate_enemy(1, character.EnemyRed,
                                        self.enemy_red_list)

        if self.round == 5:
            if self.counter % 30 == 0:
                if self.counter < 3600 and self.spawn_cnt > 8:
                    self.generate_enemy(1, character.EnemyWhite,
                                        self.enemy_white_list)
                elif self.spawn_cnt > 2:
                    self.generate_enemy(1, character.EnemyRed,
                                        self.enemy_red_list)
                else:
                    self.set_mini_boss(character.EnemyBigMouth,
                                       self.enemy_big_mouth_list)

        if self.round > 5 and self.round <= 7:
            if self.counter % 30 == 0:
                if self.counter < 1800 and self.spawn_cnt > 20:
                    self.generate_enemy(1, character.EnemyWhite,
                                        self.enemy_white_list)
                else:
                    self.generate_enemy(
                        2, character.EnemyCrack, self.enemy_crack_list)
            if self.counter % 80 == 0:
                self.generate_enemy(1, character.EnemyRed,
                                    self.enemy_red_list)

        if self.round > 7 and self.round <= 9:
            if self.counter % 30 == 0 and self.spawn_cnt > 30:
                if self.counter < 1800:
                    self.generate_enemy(3, character.EnemyWhite,
                                        self.enemy_white_list)
                else:
                    self.generate_enemy(
                        3, character.EnemyCrack, self.enemy_crack_list)
            if self.counter % 80 == 0:
                self.generate_enemy(1, character.EnemyRed,
                                    self.enemy_red_list)
            if self.counter % 90 == 0:
                self.generate_enemy(
                    1, character.EnemyBigMouth, self.enemy_big_mouth_list)
                self.generate_enemy(
                    2, character.EnemyCrack, self.enemy_crack_list)

        if self.round == 10:
            if self.counter % 30 == 0:
                if self.counter < 3600 and self.spawn_cnt > 20:
                    self.generate_enemy(1, character.EnemyCrack,
                                        self.enemy_crack_list)
                elif self.spawn_cnt > 2:
                    self.generate_enemy(1, character.EnemyBigMouth,
                                        self.enemy_big_mouth_list)
                else:
                    self.set_mini_boss(character.EnemyTank,
                                       self.enemy_tank_list)

        if self.round > 10 and self.round <= 14:
            if self.counter % 30 == 0:
                if self.counter < 1800 and self.spawn_cnt > 39:
                    self.generate_enemy(1, character.EnemyCrack,
                                        self.enemy_crack_list)
                else:
                    self.generate_enemy(
                        1, character.EnemyCrash, self.enemy_crash_list)
            if self.counter % 100 == 0:
                self.generate_enemy(1, character.EnemyBigMouth,
                                    self.enemy_big_mouth_list)

        if self.round > 14 and self.round <= 19:
            if self.counter == 300:
                self.generate_enemy(3, character.EnemyWhite,
                                    self.enemy_white_list)
            if self.counter == 500:
                self.generate_enemy(3, character.EnemyRed, self.enemy_red_list)

            if self.counter % 30 == 0 and self.counter < 2000:
                if self.spawn_cnt > 60:
                    self.generate_enemy(
                        1, character.EnemyCrash, self.enemy_crash_list)
                elif self.spawn_cnt <= 100 and self.spawn_cnt > 70:
                    self.generate_enemy(2, character.EnemyCrack,
                                        self.enemy_crack_list)
            if self.counter % 100 == 0:
                self.generate_enemy(1, character.EnemyBigMouth,
                                    self.enemy_big_mouth_list)
            if self.counter % 100 == 0 and self.counter >= 2000:
                self.generate_enemy(3, character.EnemyTank,
                                    self.enemy_tank_list)

        if self.round == 20:
            if self.counter == 3000:
                self.set_boss(character.BossRed)
            if self.counter == 300:
                self.generate_enemy(3, character.EnemyWhite,
                                    self.enemy_white_list)
            if self.counter == 500:
                self.generate_enemy(3, character.EnemyRed, self.enemy_red_list)
            if self.counter % 30 == 0 and self.counter < 2000:
                if self.spawn_cnt > 60:
                    self.generate_enemy(
                        1, character.EnemyCrash, self.enemy_crash_list)
                elif self.spawn_cnt <= 100 and self.spawn_cnt > 70:
                    self.generate_enemy(2, character.EnemyCrack,
                                        self.enemy_crack_list)
            if self.counter % 100 == 0:
                self.generate_enemy(1, character.EnemyBigMouth,
                                    self.enemy_big_mouth_list)
            if self.counter % 100 == 0 and self.counter >= 2000:
                self.generate_enemy(3, character.EnemyTank,
                                    self.enemy_tank_list)

    def set_one_enemy(self, pos, enemy_type, enemy_list) -> None:
        """Set up a single enemy."""
        if self.spawn_cnt <= 0:
            return
        enemy = enemy_type(
            pos.x, pos.y, self.physics_engine, self.player)
        enemy.register_dir_field(self.dir_field)
        enemy_list.append(enemy)
        self.enemy_sprite_list.extend(enemy.parts)
        self.physics_engine.add_sprite(enemy,
                                       friction=0,
                                       moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                       damping=0.001,
                                       collision_type="enemy")
        self.spawn_cnt -= 1

    def generate_enemy(self, spawn_mode, enemy_type, enemy_list) -> None:
        if spawn_mode == 1:  # generate one enemy
            pos = random.choice(self.room.spawn_pos)
            self.set_one_enemy(pos, enemy_type, enemy_list)
        elif spawn_mode == 2:  # generate at random place
            pos = Vec2(0, 0)
            pos.x = random.randrange(60, self.room.width - 60)
            pos.y = random.randrange(60, self.room.height - 60)
            self.set_one_enemy(pos, enemy_type, enemy_list)
        else:  # generate one wave of enemies
            for pos in self.room.spawn_pos:
                self.set_one_enemy(pos, enemy_type, enemy_list)

    def set_mini_boss(self, enemy_type, enemy_list) -> None:
        """Set up a mini boss."""
        if self.spawn_cnt <= 0:
            return
        pos = random.choice(self.room.spawn_pos)
        enemy = enemy_type(
            pos.x, pos.y, self.physics_engine, self.player)
        enemy.register_dir_field(self.dir_field)
        enemy.health *= 5
        enemy.speed += 200
        enemy.cd_max -= 20
        enemy_list.append(enemy)
        self.enemy_sprite_list.extend(enemy.parts)
        self.physics_engine.add_sprite(enemy,
                                       friction=0,
                                       moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                       damping=0.001,
                                       collision_type="enemy")
        self.spawn_cnt -= 1

    def set_boss(self, enemy_type) -> None:
        self.spawn_cnt -= 1
        pos = random.choice(self.room.spawn_pos)
        boss = enemy_type(
            pos.x, pos.y, self.physics_engine, self.player)
        boss.register_dir_field(self.dir_field)
        self.enemy_sprite_list.extend(boss.parts)
        self.boss_list.append(boss)
        self.physics_engine.add_sprite(boss,
                                       friction=0,
                                       moment_of_intertia=PymunkPhysicsEngine.MOMENT_INF,
                                       damping=0.001,
                                       collision_type="enemy",
                                       mass=4)


class GameOverView(arcade.View):
    """Game over view."""

    def __init__(self):
        super().__init__()
        self.manager = None
        self.last_view = None

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.window.set_mouse_visible(True)

    def setup(self, item_list, score) -> None:
        self.w, self.h = self.window.get_size()
        self.item_list = item_list
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.mission_text = arcade.Text(
            text=self.window.cur_lang.MISSION_FAILED,
            start_x=self.w/2,
            start_y=self.h/2 + 100,
            width=300,
            font_size=30,
            align='center',
            color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        self.score_text = arcade.Text(
            text=self.window.cur_lang.SCORE + str(score),
            start_x=self.w/2,
            start_y=self.h/2,
            width=300,
            font_size=24,
            align='center',
            color=utils.Color.BLACK,
            font_name="Cubic 11",
        )
        continue_button = arcade.gui.UIFlatButton(text=self.window.cur_lang.CONTINUE,
                                                  width=200,
                                                  x=self.w/2 + 60,
                                                  y=self.h/2 - 150,
                                                  style=utils.Style.BUTTON_DEFAULT)
        continue_button.on_click = self.on_click_continue
        self.manager.add(continue_button)

        self.item_sprites = arcade.SpriteList()

        for idx, item in enumerate(self.item_list):
            x = idx % 10
            y = math.floor(idx / 10)
            if item[0] == -1:
                tmp_bg = arcade.Sprite("graphics/item/Special.png")
            elif item[0] == 1:
                tmp_bg = arcade.Sprite("graphics/item/Bronze.png")
            elif item[0] == 2:
                tmp_bg = arcade.Sprite("graphics/item/Sliver.png")
            else:
                tmp_bg = arcade.Sprite("graphics/item/Gold.png")
            tmp_bg.center_x = 100 + 50*x
            tmp_bg.center_y = self.h - 100 - 50*y
            self.item_sprites.append(tmp_bg)
            tmp_image = arcade.Sprite(item[1])
            tmp_image.center_x = 100 + 50*x
            tmp_image.center_y = self.h - 100 - 50*y
            self.item_sprites.append(tmp_image)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.mission_text.draw()
        self.score_text.draw()
        self.item_sprites.draw()

    def on_click_continue(self, event) -> None:
        utils.Utils.clear_ui_manager(self.manager)
        self.window.start_view.setup()
        self.window.start_view.resize_camera(
            self.window.width, self.window.height)
        self.window.show_view(self.window.start_view)
        self.window.play_button_sound()


class GameWinView(GameOverView):
    """Game win view."""

    def setup(self, item_list, score) -> None:
        super().setup(item_list, score)
        self.mission_text.text = self.window.cur_lang.MISSION_SUCCESS


class ShopView(arcade.View):
    """Shop view."""

    def __init__(self):
        super().__init__()
        self.manager = None
        self.last_view = None

    def on_show_view(self) -> None:
        arcade.set_background_color(utils.Color.GROUND_WHITE)
        self.window.set_mouse_visible(True)

    def setup(self, last_view: GameView) -> None:
        self.last_view = last_view
        self.player = last_view.player
        self.shop = last_view.shop
        self.cnt = 0
        self.refresh_cost = last_view.round * last_view.round
        self.last_view.pool_size = 110 * last_view.round + \
            5 * last_view.round * last_view.round
        self.player.money += self.last_view.money_pool

        # Reset money pool of the game view
        self.last_view.money_pool = 0
        self.last_view.money_ui.alpha = 0
        self.last_view.buy_text.text = ""
        self.last_view.money_pool_ui.visible = False

        # Add items based on the current round
        self.shop.update_item_list(self.last_view.round, self.player)

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
                                                 text_color=(0, 0, 0, 255),
                                                 font_name="Cubic 11",
                                                 font_size=16)
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
                                      font_size=16,
                                      font_name="Cubic 11",
                                      anchor_x="center")
        self.purchase_text = arcade.Text("",
                                         self.w/2,
                                         self.h/2 + 280,
                                         color=utils.Color.BLACK,
                                         font_size=12,
                                         font_name="Cubic 11",
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
            text=self.window.cur_lang.BUY, width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_1 = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.BUY, width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_2 = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.BUY, width=80, style=utils.Style.BUTTON_DEFAULT
        )
        item_button_3 = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.BUY, width=80, style=utils.Style.BUTTON_DEFAULT
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
                                             font_size=16,
                                             font_name="Cubic 11",
                                             anchor_x="center")
        refresh_button = arcade.gui.UIFlatButton(text=self.window.cur_lang.REFRESH + " [D]",
                                                 x=self.w/2 + 120,
                                                 y=self.h/2 - 170,
                                                 width=160,
                                                 style=utils.Style.BUTTON_DEFAULT)
        self.manager.add(refresh_button)
        refresh_button.on_click = self.on_click_refresh

        # Rest buttons
        start_view_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.START_MENU, width=180, style=utils.Style.BUTTON_DEFAULT
        )
        continue_button = arcade.gui.UIFlatButton(
            text=self.window.cur_lang.CONTINUE, width=120, style=utils.Style.BUTTON_DEFAULT
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
        # Update player weapon reference
        self.player.change_weapon(0)

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
        text = self.window.cur_lang.PLAYER_STATUS + "\n"
        text += self.window.cur_lang.HEALTH + str(self.player.health) + "\n"
        text += self.window.cur_lang.ENERGY + str(self.player.energy) + "\n"
        text += self.window.cur_lang.SPEED + str(self.player.speed) + "\n"
        text += self.window.cur_lang.KILL_RECOVER + \
            str(self.player.kill_recover) + "\n"
        text += self.window.cur_lang.LUCK + str(self.player.luck) + "\n"
        text += self.window.cur_lang.EXPLOSION_DAMAGE + \
            str(self.player.explosion_damage) + "\n"
        text += "\n"

        text += self.window.cur_lang.PISTOL + "\n"
        text += self.window.cur_lang.DAMAGE + \
            str(self.shop.pistol.damage) + "\n"
        text += self.window.cur_lang.CD + str(self.shop.pistol.cd_max) + "\n"
        text += self.window.cur_lang.CD_MIN + \
            str(self.shop.pistol.cd_min) + "\n"
        text += self.window.cur_lang.ATTACK_RANGE + \
            str(self.shop.pistol.life_span) + "\n"
        text += "\n"

        if self.player.weapons.count(self.shop.uzi) > 0:
            text += self.window.cur_lang.UZI + "\n"
            text += self.window.cur_lang.DAMAGE + \
                str(self.shop.uzi.damage) + "\n"
            text += self.window.cur_lang.CD + str(self.shop.uzi.cd_max) + "\n"
            text += self.window.cur_lang.CD_MIN + \
                str(self.shop.uzi.cd_min) + "\n"
            text += self.window.cur_lang.ATTACK_RANGE + \
                str(self.shop.uzi.life_span) + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.uzi.cost) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.shotgun) > 0:
            text += self.window.cur_lang.SHOTGUN + "\n"
            text += self.window.cur_lang.DAMAGE + \
                str(self.shop.shotgun.damage) + "\n"
            text += self.window.cur_lang.CD + \
                str(self.shop.shotgun.cd_max) + "\n"
            text += self.window.cur_lang.CD_MIN + \
                str(self.shop.shotgun.cd_min) + "\n"
            text += self.window.cur_lang.ATTACK_RANGE + \
                str(self.shop.shotgun.life_span) + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.shotgun.cost) + "\n"
            text += self.window.cur_lang.BULLET_NUMBER + \
                str(self.shop.shotgun.bullet_num) + "\n"
            text += self.window.cur_lang.MAX_BULLETS + \
                str(self.shop.shotgun.max_bullets) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.rocket) > 0:
            text += self.window.cur_lang.ROCKET + "\n"
            text += self.window.cur_lang.DAMAGE + \
                str(self.shop.rocket.damage) + "\n"
            text += self.window.cur_lang.CD + \
                str(self.shop.rocket.cd_max) + "\n"
            text += self.window.cur_lang.CD_MIN + \
                str(self.shop.rocket.cd_min) + "\n"
            text += self.window.cur_lang.ATTACK_RANGE + \
                str(self.shop.rocket.life_span) + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.rocket.cost) + "\n"
            text += self.window.cur_lang.BULLET_NUMBER + \
                str(self.shop.rocket.bullet_num) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.wall) > 0:
            text += self.window.cur_lang.WALL + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.wall.cost) + "\n"
            text += self.window.cur_lang.HEALTH + \
                str(self.shop.wall.health_max) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.barrel) > 0:
            text += self.window.cur_lang.BARREL + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.barrel.cost) + "\n"
            text += "\n"

        if self.player.weapons.count(self.shop.mine) > 0:
            text += self.window.cur_lang.MINE + "\n"
            text += self.window.cur_lang.ENERGY_COST + \
                str(self.shop.mine.cost) + "\n"
            text += "\n"

        self.player_text.text = text

    def get_items(self) -> None:
        self.items = self.shop.get_items(self.last_view.round,
                                         self.player,
                                         self.window.cur_lang)
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
            if self.items[i].image_path == "":
                logo.texture = arcade.load_texture(
                    "graphics/item/PlaceHolder.png")
            else:
                logo.texture = arcade.load_texture(self.items[i].image_path)
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
                font_size=12,
                font_name="Cubic 11",
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
                font_size=20,
                font_name="Cubic 11",
                anchor_x="center",
                align="center",
                multiline=True,
            )
            self.item_cost.append(cost)

    def update_purchase_text(self, sign: int) -> None:
        if sign == 0:  # purchase success
            self.purchase_text.text = self.window.cur_lang.BUY_SUCCESS
            self.purchase_text.color = utils.Color.BRIGHT_GREEN
        elif sign == 1:  # purchase failed
            self.purchase_text.text = self.window.cur_lang.BUY_FAIL
            self.purchase_text.color = utils.Color.HEALTH_RED
        elif sign == 2:  # refresh failed
            self.purchase_text.text = self.window.cur_lang.REFRESH_FAIL
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
            tmp_item = (int(self.items[index].quality),
                        str(self.items[index].image_path))
            self.last_view.all_item_list.append(tmp_item)
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

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.D:
            self.on_click_refresh(event=None)

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
