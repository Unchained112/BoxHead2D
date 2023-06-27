import arcade
import math
import utils
from pyglet.math import Vec2

WALL_SIZE = 30
HALF_WALL_SIZE = 15


class Wall(arcade.Sprite):
    """Basic wall."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.pos = Vec2(x, y)
        self.grid_idx = (math.floor(x / 30),
                         math.floor(y / 30))

        super().__init__(
            filename=None,
            center_x=self.pos.x,
            center_y=self.pos.y,
            image_width=WALL_SIZE,
            image_height=WALL_SIZE,
        )


class WallCorner(Wall):
    """Wall at the corner."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("graphics/WallCorner.png")
        self.shadow = arcade.Sprite(
            center_x=self.pos.x - 3,
            center_y=self.pos.y - 3,
            scale=1,
        )
        self.shadow.texture = arcade.make_soft_square_texture(
            30, utils.Color.LIGHT_BLACK, 150, 150)

    def draw(self) -> None:
        self.shadow.draw()
        super().draw()


class WallSideHorizontal(Wall):
    """Wall along the horizontal side."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("graphics/WallSide.png")
        self.shadow = arcade.Sprite(
            center_x=self.pos.x,
            center_y=self.pos.y - 3,
            scale=1,
        )
        self.shadow.texture = arcade.make_soft_square_texture(
            30,  utils.Color.LIGHT_BLACK, 150, 150)

    def draw(self) -> None:
        self.shadow.draw()
        super().draw()


class WallSideVertical(Wall):
    """Wall along the vertical side."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self.texture = arcade.load_texture("graphics/WallSide.png")
        self.angle = -90
        self.shadow = arcade.Sprite(
            center_x=self.pos.x - 3,
            center_y=self.pos.y,
            scale=1,
        )
        self.shadow.texture = arcade.make_soft_square_texture(
            30, utils.Color.LIGHT_BLACK, 150, 150)

    def draw(self) -> None:
        self.shadow.draw()
        super().draw()


class Room:
    """Room base class."""

    def __init__(self, width: float = 2100, height: float = 1200) -> None:
        """width and height should be multiple of the wall size"""
        self.width = width
        self.height = height
        self.pos = Vec2(self.width / 2, self.height / 2)

        self.grid_w = int(self.width / WALL_SIZE)
        self.grid_h = int(self.height / WALL_SIZE)
        self.grid = {(i, j): 0 for i in range(self.grid_w)
                     for j in range(self.grid_h)}

        self.walls = []

    def draw_ground(self) -> None:
        pass

    def draw_walls(self) -> None:
        pass


class StartRoom(Room):
    """Room for start menu."""

    def __init__(self, width: float = 2100, height: float = 1200) -> None:
        super().__init__(width, height)
        # set boundary corner walls
        self.walls = [WallCorner(HALF_WALL_SIZE, HALF_WALL_SIZE), WallCorner(HALF_WALL_SIZE, self.height - HALF_WALL_SIZE), WallCorner(
            self.width - HALF_WALL_SIZE, HALF_WALL_SIZE), WallCorner(self.width - HALF_WALL_SIZE, self.height - HALF_WALL_SIZE)]

        # set bottom and top walls
        for i in range(1, self.grid_w - 1):
            self.walls.append(WallSideHorizontal(
                HALF_WALL_SIZE + i * WALL_SIZE, HALF_WALL_SIZE))
            self.walls.append(WallSideHorizontal(
                HALF_WALL_SIZE + i * WALL_SIZE, self.height - HALF_WALL_SIZE))

        # set left and right walls
        for i in range(1, self.grid_h - 1):
            self.walls.append(WallSideVertical(
                HALF_WALL_SIZE, HALF_WALL_SIZE + i * WALL_SIZE))
            self.walls.append(WallSideVertical(
                self.width - HALF_WALL_SIZE, HALF_WALL_SIZE + i * WALL_SIZE))

    def draw_ground(self) -> None:
        arcade.draw_rectangle_filled(
            self.pos.x, self.pos.y, self.width, self.height, utils.Color.GROUND_WHITE
        )

    def draw_walls(self) -> None:
        for wall in self.walls:
            wall.draw()
