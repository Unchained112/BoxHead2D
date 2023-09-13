import arcade
import view

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Box Head 2D: Survivor"


class BoxHead2d(arcade.Window):
    """ Main application class. """

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        self.effect_volume = 2
        self.music_volume = 2
        self.state = 0  # game state
        self.w_scale = [1024, 1280, 1440, 1920]
        self.h_scale = [600, 720, 900, 1080]
        self.res_index = 1
        self.button_sound = arcade.Sound("audio/ui_click.wav")
        self.explosion_sound = arcade.Sound("audio/explosion_2.wav")

        self.start_view = None
        self.option_view = None
        self.select_view = None
        self.game_view = None

    def set_up(self) -> None:
        self.option_view = view.OptionView()
        self.select_view = view.SelectionView()

    def play_button_sound(self) -> None:
        self.button_sound.play(volume=self.effect_volume/20)

    def play_explosion_sound(self) -> None:
        self.explosion_sound.play(volume=self.effect_volume/20)


def main():
    """ Main function """
    arcade.load_font("fonts/FFFFORWA.ttf")
    arcade.load_font("fonts/Minercraftory.ttf")
    game = BoxHead2d(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.set_up()
    default = view.DefaultView()
    default.setup()
    game.show_view(default)
    arcade.run()


if __name__ == "__main__":
    main()
