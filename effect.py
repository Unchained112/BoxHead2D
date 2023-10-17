import arcade
import math
import random
import utils


class Blood(arcade.SpriteSolidColor):
    """Bleeding effect particle. """

    def __init__(self) -> None:
        super().__init__(random.randint(4, 12), random.randint(4, 12), utils.Color.DARK_RED)
        self.my_alpha = 255
        self.counter = 600

        # Set direction/speed
        speed = random.random() * 8
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

    def update(self):
        if self.my_alpha > 200:  # alpha threshold
            self.my_alpha -= 50  # blood particle fade rate
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y

        if self.counter <= 0:
            self.remove_from_sprite_lists()
        self.counter -= 1


class ExplosionTrace(arcade.SpriteSolidColor):
    """Explosion traces particle. """

    def __init__(self) -> None:
        super().__init__(random.randint(6, 12), random.randint(6, 12), utils.Color.BLACK)
        self.my_alpha = 255
        self.counter = 600

        # Set direction/speed
        speed = random.random() * 12
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

    def update(self):
        if self.my_alpha > 200:  # alpha threshold
            self.my_alpha -= 50  # blood particle fade rate
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y

        if self.counter <= 0:
            self.remove_from_sprite_lists()
        self.counter -= 1
