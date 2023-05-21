import pygame
from player import Player

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
    # render player
    pygame.draw.rect(screen, BLACK, player.body, 0)
    pygame.draw.rect(screen, BLACK, player.foot_r, 0)
    pygame.draw.rect(screen, BLACK, player.foot_l, 0)

    # flip() the display to put your work on screen
    # pygame.display.flip()
    pygame.display.update()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
