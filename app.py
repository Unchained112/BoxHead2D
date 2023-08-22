import arcade
import view

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Box Head 2D: Invincible"


class BoxHead2d(arcade.Window):
    """ Main application class. """
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        self.effect_volume = 2
        self.music_volume = 2
        self.state = 0 # game state
        self.w_scale = [720, 1280, 1920]
        self.h_scale = [480, 720, 1080]
        self.res_index = 1

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.F:
            # User hits f. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Get the window coordinates. Match viewport to window coordinates
            # so there is a one-to-one mapping.
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)


def main():
    """ Main function """
    arcade.load_font("fonts/FFFFORWA.ttf")
    arcade.load_font("fonts/Minercraftory.ttf")
    game = BoxHead2d(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    default = view.DefaultView()
    default.setup()
    game.show_view(default)
    arcade.run()


if __name__ == "__main__":
    main()
