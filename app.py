import arcade
import view
import pickle


class BoxHead2d(arcade.Window):
    """ Main application class. """

    def __init__(self):
        with open("data/settings.bin", "rb") as setting_file:
            settings = pickle.load(setting_file)
        self.effect_volume = settings.effect_volume
        self.music_volume = settings.music_volume
        self.res_index = settings.res_index
        self.w_scale = [1024, 1280, 1440, 1920]
        self.h_scale = [600, 720, 900, 1080]
        super().__init__(self.w_scale[self.res_index],
                         self.h_scale[self.res_index],
                         "Box Head 2D: Survivor")
        self.set_fullscreen(settings.fullscreen)
        self.start_view = None
        self.option_view = None
        self.select_view = None
        self.game_view = None

    def set_up(self) -> None:
        # Load sound and music
        self.button_sound = arcade.Sound("audio/ui_click.wav")
        self.explosion_sound = arcade.Sound("audio/explosion_2.wav")
        self.refresh_sound = arcade.Sound("audio/ui_refresh.wav")
        self.purchase_sound = arcade.Sound("audio/ui_purchase.wav")
        self.purchase_fail_sound = arcade.Sound("audio/ui_purchase_fail.wav")
        self.round_start_sound = arcade.Sound("audio/round_start.wav")

        self.start_music = arcade.Sound(
            "audio/the-best-jazz-club-in-new-orleans-164472.wav")
        self.game_music = arcade.Sound(
            "audio/electronic-rock-king-around-here-15045.wav")

        # Set game views
        self.option_view = view.OptionView()
        self.select_view = view.SelectionView()
        self.shop_view = view.ShopView()
        self.start_music_player = self.start_music.play(
            volume=self.music_volume/20, loop=True)
        self.start_music_player.pause()
        self.game_music_player = self.game_music.play(
            volume=self.music_volume/20, loop=True)
        self.game_music_player.pause()

    def play_button_sound(self) -> None:
        self.button_sound.play(volume=self.effect_volume/20)

    def play_explosion_sound(self) -> None:
        self.explosion_sound.play(volume=self.effect_volume/20)

    def play_refresh_sound(self) -> None:
        self.refresh_sound.play(volume=self.effect_volume/20)

    def play_purchase_sound(self) -> None:
        self.purchase_sound.play(volume=self.effect_volume/20)

    def play_purchase_fail_sound(self) -> None:
        self.purchase_fail_sound.play(volume=self.effect_volume/20)

    def play_round_start_sound(self) -> None:
        self.round_start_sound.play(volume=self.effect_volume/20)

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

    game = BoxHead2d()
    game.set_up()
    default = view.DefaultView()
    default.setup()
    game.show_view(default)
    arcade.run()


if __name__ == "__main__":
    main()
