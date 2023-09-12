import arcade
import math
import random
import utils

PARTICLE_FADE_RATE = 60
PARTICLE_MIN_SPEED = 6
PARTICLE_SPEED_RANGE = 1
PARTICLE_RADIUS = 3
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.COQUELICOT,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]


class Smoke(arcade.SpriteCircle):
    """ This represents a puff of smoke """

    def __init__(self, size: int) -> None:
        super().__init__(size, arcade.color.DARK_GRAY, soft=True)
        self.scale = 0.66  # smoke scale

    def update(self) -> None:
        """ Update this particle """
        if self.alpha <= PARTICLE_FADE_RATE:
            # Remove faded out particles
            self.remove_from_sprite_lists()
        else:
            # Update values
            self.alpha -= 42  # smoke fade rate
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.scale += 0.03  # smoke expansion rate


class Particle(arcade.SpriteCircle):
    """ Explosion particle """

    def __init__(self, my_list: arcade.SpriteList) -> None:
        # Choose a random color
        color = random.choice(PARTICLE_COLORS)

        # Make the particle
        super().__init__(PARTICLE_RADIUS, color)

        # Track normal particle texture, so we can 'flip' when we sparkle.
        self.normal_texture = self.texture

        # Keep track of the list we are in, so we can add a smoke trail
        self.my_list = my_list

        # Set direction/speed
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

        # Track original alpha. Used as part of 'sparkle' where we temp set the
        # alpha back to 255
        self.my_alpha = 255

        # Used for appending smoke particles
        self.my_list = my_list

    def update(self) -> None:
        """ Update the particle """
        if self.my_alpha <= PARTICLE_FADE_RATE:
            # Faded out, remove
            self.remove_from_sprite_lists()
        else:
            # Update
            self.my_alpha -= 36  # particle fade rate
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y

            # Whether a particle sparkles
            if random.random() <= 0.02:  # sparkle chance
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width),
                                                          arcade.color.WHITE)
            else:
                self.texture = self.normal_texture

            # Leave a smoke particle?
            if random.random() <= 0.25:  # smoke chance
                smoke = Smoke(5)
                smoke.position = self.position
                self.my_list.append(smoke)


class Blood(arcade.SpriteSolidColor):
    """Bleeding effect particle. """

    def __init__(self) -> None:
        color = (65, 100, 74)  # Dark green
        super().__init__(random.randint(4, 12), random.randint(4, 12), utils.Color.DARK_RED)
        self.my_alpha = 255
        # Set direction/speed
        speed = random.random() * 6
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

    def update(self):
        if self.my_alpha > 200:  # alpha threshold
            self.my_alpha -= 20  # blood particle fade rate
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
