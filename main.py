
import pygame

'''
=======================================================================
GLOBAL VARIABLE
=======================================================================
'''
# Color palette
GROUND_WHITE = (221, 230, 237)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (183, 4, 4)
LIGHT_GRAY = (207, 210, 207)
DARK_GRAY = (67, 66, 66)
LIGHT_BLACK = (34, 34, 34)

# Screen size
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900

'''
=======================================================================
BASE CLASS
=======================================================================
'''
class GameObject:
    def __init__(self):
        self.pos = pygame.Vector2(0, 0)

    # update the GameObject logic
    def update():
        pass

    # render the GameObject
    def draw(self, screen):
        pass

'''
=======================================================================
UI ELEMENT
=======================================================================
'''

'''
=======================================================================
ENVIRONMENT
=======================================================================
'''
class FixedWall(GameObject):
    def __init__(self, x = 0, y = 0):
        self.pos = pygame.Vector2(x, y)
        self.grid_idx = (0, 0)

        # wall collider
        self.wallRect = pygame.Rect(self.pos.x, self.pos.y, 30, 30)
        self.points = [(self.pos.x, self.pos.y + 5), (self.pos.x, self.pos.y + 25),
                       (self.pos.x + 5, self.pos.y + 30), (self.pos.x + 25, self.pos.y + 30),
                       (self.pos.x + 30, self.pos.y + 25), (self.pos.x + 30, self.pos.y + 5),
                       (self.pos.x + 25, self.pos.y), (self.pos.x + 5, self.pos.y)]

    def draw(self, screen):
        pygame.draw.polygon(screen, WHITE, self.points, 0)
        pygame.draw.polygon(screen, BLACK, self.points, 3)


class Room:
    def __init__(self):
        self.walls = []

'''
=======================================================================
WEAPON
=======================================================================
'''

'''
=======================================================================
PLAYER
=======================================================================
'''
class Player(GameObject):
    def __init__(self, x = 0, y = 0):
        # Perporties
        self.is_walking = False
        self.speed = 3
        # init position
        self.pos = pygame.Vector2(x, y)

        # Animation init
        self.walking_in = True  # feet move inside
        self.walking_frames_max = 6
        self.walking_frames = self.walking_frames_max
        self.foot_flag = True # change walking foot
        self.foot_flag_frames = 2 * self.walking_frames_max
        self.body_move_up = False
        self.body_move_frames_max = 20
        self.body_move_frames = self.body_move_frames_max
        self.velocity = pygame.Vector2(0, 0)

        # Visuals
        # body Rect
        self.body = pygame.Rect(self.pos.x, self.pos.y, 28, 24)
        # feet Rect
        self.foot_l = pygame.Rect(self.pos.x, self.pos.y + 26, 6, 4)
        self.foot_r = pygame.Rect(self.pos.x + 22, self.pos.y + 26, 6, 4)

    def changeDir(self, x, y):
        self.velocity.x += x * self.speed
        self.velocity.y += y * self.speed
        if self.velocity.x != 0 or self.velocity.y != 0:
            self.is_walking = True
            self.velocity.normalize()
        else:
            self.is_walking = False

    def move(self):
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y

        # update visual
        self.body.topleft += self.velocity
        self.foot_l.topleft += self.velocity
        self.foot_r.topleft += self.velocity

    def update(self):
        # player move
        self.move()

        # body animation
        if self.body_move_up:
            if self.body_move_frames < 4:
                self.body.y += 1
            self.body_move_frames -= 1
        else:
            if self.body_move_frames < 4:
                self.body.y -= 1
            self.body_move_frames -= 1

        if self.body_move_frames == 0:
            self.body_move_frames = self.body_move_frames_max
            self.body_move_up = not self.body_move_up

        # feet animation
        if self.is_walking:
            if self.walking_in:
                if self.walking_frames < 3:
                    if self.foot_flag:
                        self.foot_l.x += 2
                        self.foot_l.y -= 1
                    else:
                        self.foot_r.x -= 2
                        self.foot_r.y -= 1
            else:
                if self.walking_frames < 3:
                    if self.foot_flag:
                        self.foot_l.x -= 2
                        self.foot_l.y += 1
                    else:
                        self.foot_r.x += 2
                        self.foot_r.y += 1
            self.walking_frames -= 1
            self.foot_flag_frames -= 1
        else:
            # reset the walking animation
            self.foot_l.topleft = (self.pos.x, self.pos.y + 26)
            self.foot_r.topleft = (self.pos.x + 22, self.pos.y + 26)
            self.walking_frames = self.walking_frames_max
            self.walking_in = True
            self.foot_flag_frames = 2 * self.walking_frames_max
            self.foot_flag = not self.foot_flag

        if self.walking_frames == 0:
            self.walking_frames = self.walking_frames_max
            self.walking_in = not self.walking_in
        if self.foot_flag_frames == 0:
            self.foot_flag_frames = 2 * self.walking_frames_max
            self.foot_flag = not self.foot_flag

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, player.body, 0)
        pygame.draw.rect(screen, BLACK, player.foot_r, 0)
        pygame.draw.rect(screen, BLACK, player.foot_l, 0)

'''
=======================================================================
ENEMY
=======================================================================
'''


'''
=======================================================================
GAME
=======================================================================
'''

player = Player(SCREEN_WIDTH / 2, SCREEN_WIDTH /2)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

test_wall = FixedWall(10, 20)
test_wall.wallRect.x = 10
test_wall.wallRect.y = 20

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.changeDir(-1, 0)
            if event.key == pygame.K_d:
                player.changeDir(1, 0)
            if event.key == pygame.K_w:
                player.changeDir(0, -1)
            if event.key == pygame.K_s:
                player.changeDir(0, 1)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.changeDir(1, 0)
            if event.key == pygame.K_d:
                player.changeDir(-1, 0)
            if event.key == pygame.K_w:
                player.changeDir(0, 1)
            if event.key == pygame.K_s:
                player.changeDir(0, -1)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(GROUND_WHITE)

    # game logic
    player.update()

    # RENDER YOUR GAME HERE
    # render room
    test_wall.draw(screen)

    # render player
    player.draw(screen)

    # flip() the display to put your work on screen
    # pygame.display.flip()
    pygame.display.update()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
