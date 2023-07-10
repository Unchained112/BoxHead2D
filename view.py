import arcade
import utils

FADE_RATE = 5


class DefaultView(arcade.View):
    """Default view displayed when game starts"""

    def on_show_view(self):
        arcade.set_background_color(utils.Color.GROUND_WHITE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Press any key to proceed...", 500, 320,
                         utils.Color.BLACK, font_size=24, font_name="Kenney Future",
                         anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        start = StartView()
        start.setup()
        self.window.show_view(start)
    
    def on_key_press(self, symbol: int, modifiers: int):
        start = StartView()
        start.setup()
        self.window.show_view(start)
        


class FadingView(arcade.View):
    """Fading transiton between two views."""

    def __init__(self):
        super().__init__()
        self.fade_out = None
        self.fade_in = 255

    def update_fade(self, next_view=None):
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

    def draw_fading(self):
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

    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def on_update(self, dt):
        self.update_fade(next_view=GameView)


class GameView(FadingView):

    def __init__(self):
        super().__init__()
