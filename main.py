# Example file showing a basic pygame "game loop"
import pygame

# Color palette
GROUND_WHITE = (221, 230, 237)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (183, 4, 4)
LIGHT_GRAY = (207, 210, 207)
DARK_GRAY = (67, 66, 66)
LIGHT_BLACK = (34, 34, 34)

# Screen size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


class Player():
 
    def __init__(self):
        self.is_walking = False
        self.body_move_up = False
        self.body_move_frames = 20
    
        # init position
        self.pos_x = SCREEN_WIDTH / 2 - 14
        self.pos_y = SCREEN_HEIGHT / 2 - 14

        # body Rect
        self.body = pygame.Rect(self.pos_x, self.pos_y, 28, 24)

    def update(self):
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
            self.body_move_frames = 20
            self.body_move_up = not self.body_move_up


player = Player()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(GROUND_WHITE)

    # game logic
    player.update()

    # RENDER YOUR GAME HERE
    pygame.draw.rect(screen, BLACK, player.body, 0)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
