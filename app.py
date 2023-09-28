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
        self.cur_music_idx = 0
        self.start_music = arcade.Sound(
            "audio/the-best-jazz-club-in-new-orleans-164472.wav")
        self.game_music = arcade.Sound(
            "audio/electronic-rock-king-around-here-15045.wav")
        self.start_view = None
        self.option_view = None
        self.select_view = None
        self.game_view = None

    def set_up(self) -> None:
        self.option_view = view.OptionView()
        self.select_view = view.SelectionView()
        self.shop_view = view.ShopView()
        self.start_music_player = self.start_music.play(
            volume=self.effect_volume/20, loop=True)
        self.start_music_player.pause()
        self.game_music_player = self.game_music.play(
            volume=self.effect_volume/20, loop=True)
        self.game_music_player.pause()

    def play_button_sound(self) -> None:
        self.button_sound.play(volume=self.effect_volume/20)

    def play_explosion_sound(self) -> None:
        self.explosion_sound.play(volume=self.effect_volume/20)

    def update_music_volume(self) -> None:
        self.start_music_player.volume = self.music_volume/20
        self.game_music_player.volume = self.music_volume/20

    def play_start_music(self, music_idx: int) -> None:
        self.game_music_player.pause()
        self.start_music_player.play()

    def play_game_music(self, music_idx: int) -> None:
        self.start_music_player.pause()
        self.game_music_player.play()


def main():
    """ Main function """
    arcade.load_font("fonts/FFFFORWA.ttf")
    arcade.load_font("fonts/Minercraftory.ttf")
    arcade.load_font("fonts/DottedSongtiSquareRegular.otf")
    arcade.load_font("fonts/SourceHanSansOLD-Normal-2.otf")

    game = BoxHead2d(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.set_up()
    default = view.DefaultView()
    default.setup()
    game.show_view(default)
    arcade.run()


if __name__ == "__main__":
    main()
