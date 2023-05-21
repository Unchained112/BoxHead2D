import pygame

class Player():

    def __init__(self):
        self.is_walking = False
        self.walking_in = True  # feet move inside
        self.walking_frames = 8
        self.body_move_up = False
        self.body_move_frames = 20
        self.speed = 3
        self.velocity = pygame.Vector2(0, 0)

        # init position
        self.pos_x = 1280 / 2 - 14
        self.pos_y = 720 / 2 - 14

        # body Rect
        self.body = pygame.Rect(self.pos_x, self.pos_y, 28, 24)

        # feet Rect
        self.foot_l = pygame.Rect(self.pos_x, self.pos_y + 26, 6, 4)
        self.foot_r = pygame.Rect(self.pos_x + 22, self.pos_y + 26, 6, 4)

    def changeDir(self, x, y):
        self.velocity.x += x * self.speed
        self.velocity.y += y * self.speed
        if self.velocity.x != 0 or self.velocity.y != 0:
            self.is_walking = True
        else:
            self.is_walking = False
            

    def move(self):
        self.pos_x += self.velocity.x
        self.pos_y += self.velocity.y

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
            self.body_move_frames = 20
            self.body_move_up = not self.body_move_up

        # feet animation
        if self.is_walking:
            if self.walking_in:
                if self.walking_frames < 4:
                    self.foot_l.x += 2
                    self.foot_r.x -= 2
                self.walking_frames -= 1
            else:
                if self.walking_frames < 4:
                    self.foot_l.x -= 2
                    self.foot_r.x += 2
                self.walking_frames -= 1
        else:
            self.foot_l.x = self.pos_x
            self.foot_r.x = self.pos_x + 22
            self.walking_frames = 8
            self.walking_in = True

        if self.walking_frames == 0:
            self.walking_frames = 8
            self.walking_in = not self.walking_in
