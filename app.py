import arcade
import view
import utils
import pickle


class BoxHead2d(arcade.Window):
    """ Main application class. """

    def __init__(self):
        # Load settings
        try:
            settings = pickle.load(open("data/settings.bin", "rb"))
        except (OSError) as e:
            settings = utils.Setting(e_volume=2,
                                     m_volume=2,
                                     r_idx=0,
                                     fullscreen=True,
                                     lang_idx=0)
            pickle.dump(settings, open("data/settings.bin", "wb"))
        self.effect_volume = settings.effect_volume
        self.music_volume = settings.music_volume
        self.res_index = settings.res_index
        self.lang = [utils.Language.EN, utils.Language.CN]
        self.lang_idx = settings.lang_idx
        self.cur_lang = self.lang[self.lang_idx]
        self.w_scale = [1024, 1280, 1440, 1920]
        self.h_scale = [600, 720, 900, 1080]
        super().__init__(self.w_scale[self.res_index],
                         self.h_scale[self.res_index],
                         self.cur_lang.TITLE)
        self.set_fullscreen(settings.fullscreen)

        self.start_view = None
        self.option_view = None
        self.select_view = None
        self.game_view = None
        self.game_over_view = None
        self.game_win_view = None

    def set_up(self) -> None:
        # Load fonts
        arcade.load_font("fonts/FFFFORWA.ttf")
        arcade.load_font("fonts/Cubic_11_1.013_R.ttf")

        # Load sound and music
        self.button_sound = arcade.Sound("audio/ui_click.wav")
        self.explosion_sound = arcade.Sound("audio/explosion_2.wav")
        self.explosion_sound_cnt: int = 0
        self.refresh_sound = arcade.Sound("audio/ui_refresh.wav")
        self.purchase_sound = arcade.Sound("audio/ui_purchase.wav")
        self.purchase_fail_sound = arcade.Sound("audio/ui_purchase_fail.wav")
        self.round_start_sound = arcade.Sound("audio/round_start.wav")
        self.game_over_sound = arcade.Sound("audio/game_over.wav")
        self.game_win_sound = arcade.Sound("audio/mission_complete.wav")

        self.start_music = arcade.Sound(
            "audio/the-best-jazz-club-in-new-orleans-164472.wav")
        self.game_music = arcade.Sound(
            "audio/zapsplat_game_music_medium_action_electronic_techno.wav")

        # Set game views
        self.option_view = view.OptionView()
        self.select_view = view.SelectionView()
        self.shop_view = view.ShopView()
        self.game_over_view = view.GameOverView()
        self.game_win_view = view.GameWinView()
        self.start_music_player = self.start_music.play(
            volume=self.music_volume/20, loop=True)
        self.start_music_player.pause()
        self.game_music_player = self.game_music.play(
            volume=self.music_volume/20, loop=True)
        self.game_music_player.pause()

    def play_button_sound(self) -> None:
        self.button_sound.play(volume=self.effect_volume/20)

    def play_explosion_sound(self) -> None:
        if self.explosion_sound_cnt == 0:
            # Avoid too many explosion noisy
            self.explosion_sound.play(volume=self.effect_volume/20)
            self.explosion_sound_cnt = 18

    def play_refresh_sound(self) -> None:
        self.refresh_sound.play(volume=self.effect_volume/20)

    def play_purchase_sound(self) -> None:
        self.purchase_sound.play(volume=self.effect_volume/20)

    def play_purchase_fail_sound(self) -> None:
        self.purchase_fail_sound.play(volume=self.effect_volume/20)

    def play_round_start_sound(self) -> None:
        self.round_start_sound.play(volume=self.effect_volume/20)

    def play_game_over_sound(self) -> None:
        self.game_over_sound.play(volume=self.effect_volume/20)

    def play_game_win_sound(self) -> None:
        self.game_win_sound.play(volume=self.effect_volume/20)

    def update_music_volume(self) -> None:
        self.start_music_player.volume = self.music_volume/20
        self.game_music_player.volume = self.music_volume/20

    def play_start_music(self, music_idx: int) -> None:
        self.game_music_player.pause()
        self.start_music_player.play()

    def play_game_music(self, music_idx: int) -> None:
        self.start_music_player.pause()
        self.game_music_player.play()

    def set_cur_lang(self, lang_idx: int) -> None:
        self.lang_idx = lang_idx
        self.cur_lang = self.lang[self.lang_idx]


def main():
    """ Main function """

    game = BoxHead2d()
    game.set_up()
    default = view.DefaultView()
    default.setup()
    game.show_view(default)
    arcade.run()


if __name__ == "__main__":
    main()
