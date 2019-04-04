import pygame as pg
from math import cos, sin, radians
from config import *


class Game():
    def __init__(self):
        pg.init()
        self.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Mayhem!")
        clock = pg.time.Clock()
        clock.tick(TICKRATE)
        pause = False
        self.running = True

        self.ShipGroup = pg.sprite.Group()

        self.p1 = Ship(self.display, P1_STARTPOS, 1)
        self.p2 = Ship(self.display, P2_STARTPOS, 2)
        self.ShipGroup.add(self.p1, self.p2)

        self.game_loop()

    def game_loop(self):
        while self.running:
            self.keystrokes()
            self.display.fill((0, 0, 0))
            self.ShipGroup.draw(self.display)
            pg.display.update()
        pg.quit()
        quit()

    def keystrokes(self):
        if pg.event.peek(pg.QUIT):
            self.running = False
        pg.event.pump()
        keys_pressed = pg.key.get_pressed()
        '''
        if keys_pressed[pg.K_ESCAPE]:
            pause = True
        while pause == True:
            for event in pg.event.get():
                if event == pg.QUIT:
                    pg.quit()
                    quit()
                if event == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    pause = False
        '''
        if keys_pressed[pg.K_w]:
            pass # p1 shoot
        if keys_pressed[pg.K_s]:
            self.p1.forward(2)  # p1 accel
        if keys_pressed[pg.K_a]:
            self.p1.rotate(1)  # p1 rot l
        if keys_pressed[pg.K_d]:
            self.p1.rotate(-1)  # p1 rot r

        if keys_pressed[pg.K_UP]:
            pass # p2 shoot
        if keys_pressed[pg.K_DOWN]:
            self.p2.forward(2) # p2 accel
        if keys_pressed[pg.K_LEFT]:
            self.p2.rotate(1) # p2 rot l
        if keys_pressed[pg.K_RIGHT]:
            self.p2.rotate(-1) # p2 rot r


class MovingObject():
    def __init__(self, display, pos, heading, image):
        self.display = display
        self.pos = pos
        self.image = image
        self.original = image

        self.rect = self.original.get_rect()
        self.rect.center = self.pos

        self.heading = heading

    def forward(self, speed):
        angle = radians(self.heading)
        self.pos[0] -= sin(angle)*speed
        self.pos[1] -= cos(angle)*speed
        self.rect.center = self.pos

    def rotate(self, angle):
        self.heading += angle
        self.heading %= 360
        self.image = pg.transform.rotate(self.original, self.heading)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class Ship(MovingObject, pg.sprite.Sprite):
    def __init__(self, display, pos, team):
        pg.sprite.Sprite.__init__(self)
        if team == 1:
            self.image = pg.image.load("red_ship.png")
        else:
            self.image = pg.image.load("blue_ship.png")
        self.image.convert()
        self.image.set_colorkey((0, 0, 0))
        self.image = pg.transform.rotate(self.image, -90)
        MovingObject.__init__(self, display, pos, 0, self.image)
        self.health = 3
        self.score = 0


if __name__ == '__main__':
    Game()
