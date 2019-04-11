import pygame as pg
from math import cos, sin, radians
from config import *
from copy import deepcopy


class Game():
    def __init__(self):
        pg.init()
        self.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Mayhem!")
        global clock
        clock = pg.time.Clock()

        self.running = True

        self.ShipGroup = pg.sprite.Group()
        global BulletGroup
        BulletGroup = pg.sprite.Group()

        self.p1 = Ship(self.display, P1_STARTPOS, 1)
        self.p2 = Ship(self.display, P2_STARTPOS, 2)
        self.ShipGroup.add(self.p1, self.p2)

        self.pad1 = FuelPad(self.display, PAD1_RECT, RED)
        self.pad2 = FuelPad(self.display, PAD2_RECT, BLUE)

        global all_rects
        all_rects = [self.p1.rect, self.p2.rect,
                     self.pad1.rect, self.pad2.rect]

        self.game_loop()

    def game_loop(self):
        global dt
        while self.running:
            dt = clock.tick(TICKRATE)
            self.keystrokes()
            #self.p1.move()
            for ship in self.ShipGroup.sprites():
                ship.move()
            for bullet in BulletGroup.sprites():
                bullet.bullet_move()
            
            self.display.fill((0, 0, 0))
            self.pad1.draw()
            self.pad2.draw()
            self.ShipGroup.draw(self.display)
            BulletGroup.draw(self.display)
            pg.display.update()

        pg.quit()
        quit()

    def keystrokes(self):
        keys_pressed = pg.key.get_pressed()
        if pg.event.peek(pg.QUIT):
            self.running = False

        if keys_pressed[pg.K_w]:
            self.p1.shoot() # p1 shoot
        if keys_pressed[pg.K_s]:
            if self.p1.thrust+self.p1.driftspeed < MAX_SHIPSPEED:
                self.p1.thrust += 0.4  # p1 accel
                self.p1.driftspeed += 0.4
        if keys_pressed[pg.K_a]:
            self.p1.rotate(2)  # p1 rot l
        if keys_pressed[pg.K_d]:
            self.p1.rotate(-2)  # p1 rot r

        if keys_pressed[pg.K_UP]:
            pass # p2 shoot
        if keys_pressed[pg.K_DOWN]:
            if self.p2.thrust < MAX_SHIPSPEED:
                self.p2.thrust += 0.5 # p2 accel
        if keys_pressed[pg.K_LEFT]:
            self.p2.rotate(2) # p2 rot l
        if keys_pressed[pg.K_RIGHT]:
            self.p2.rotate(-2) # p2 rot r

        pg.event.clear()


class MovingObject():
    def __init__(self, display, heading, image, rect):
        self.display = display
        self.image = image
        self.original = image
        self.rect = rect

        self.pos = list(self.rect.center)
        self.newpos = self.pos
        self.heading = heading      # Direction of movement, 
                                    #   changes with forward() and gravity().
        self.orientation = heading  # Orientation of ship

        self.thrust = 0             # Speed in direction of orientation
        self.driftspeed = 0         # Speed in direction of heading
        self.gravspeed = 0          # Speed due to gravity
        self.transf()

    def forward(self):
        #if self.heading != self.orientation:
        #    self.heading += (self.orientation - self.heading)*10
        self.heading %= 360
        heading_rad = radians(self.heading)
        orientation_rad = radians(self.orientation)
        x = cos(orientation_rad)*self.driftspeed + cos(orientation_rad)*self.thrust
        y = sin(orientation_rad)*self.driftspeed + sin(orientation_rad)*self.thrust
        self.newpos[0] += x
        self.newpos[1] -= y


    def rotate(self, angle):
        self.orientation += angle
        self.orientation %= 360
        self.transf()

    def transf(self):
        self.image = pg.transform.rotate(self.original, self.orientation)
        x, y = self.rect.center             # Keep sprite center 
        self.rect = self.image.get_rect()   # constant.
        self.rect.center = (x, y)           #

    def grav(self):
        '''Total acceleration if a sum of forces divided by mass, 
        don't care about mass here. This method gives total acceleration
        equal to gravitational acceleration + acceleration from thrust.
        Not a 1-to-1 replica of real physics, but it is satisfactory.'''
        if self.gravspeed < 70:
            self.gravspeed += sin(radians(self.heading))*self.driftspeed + GRAVITY

        self.newpos[0] += 0
        self.newpos[1] += self.gravspeed*0.05


class Ship(MovingObject, pg.sprite.Sprite):
    def __init__(self, display, pos, player):
        pg.sprite.Sprite.__init__(self)

        self.expl_img = pg.image.load("explosion.png")
        self.expl_img.convert()
        self.expl_img.set_colorkey((0, 0, 0))

        self.other_rects = 0
        
        if player == 1:
            self.image = pg.image.load("red_ship.png")
            self.player = 'p1'
        else:
            self.image = pg.image.load("blue_ship.png")
            self.player = 'p2'

        # Convert ship sprite and put it in the right place:
        # (note: important that ship points to right in original image)
        self.image.convert()
        self.image.set_colorkey((0, 0, 0))
        self.original = self.image

        self.original_pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.own_index = 0

        MovingObject.__init__(self, display, 90, self.image, self.rect)

        self.ship_corners = [self.rect.topleft, self.rect.bottomleft, 
                    self.rect.topright, self.rect.bottomright]
        self.fuel = MAX_FUEL
        self.score = 0

    def shoot(self):
        bullet = Bullet(self.orientation, self.rect.center)
        bullet.thrust = BULLET_SPEED

    def bounds(self): # rewrite to take any rectangle instead of just display
        '''Keep ship within screen bounds'''
        
        collided = False
        for corner in self.ship_corners:
            if corner[0] < 0:
                self.newpos = [self.rect.center[0]+1, self.newpos[1]]
                if self.driftspeed > 6:
                    collided = True
            if corner[0] > SCREEN_WIDTH:
                self.newpos = [self.rect.center[0]-1, self.newpos[1]]
                if self.driftspeed > 6:
                    collided = True
            if corner[1] < 0:
                self.newpos = [self.newpos[0], self.rect.center[1]+1]
                if self.driftspeed > 6:
                    collided = True
            if corner[1] > SCREEN_HEIGHT:
                self.newpos = [self.newpos[0], self.rect.center[1]-1]
                if self.driftspeed > 6:
                    collided = True
        if collided == True:
            self.reset()
            collided = False

    def collisions(self):
        ''' '''
        # Set up list of rects of fuel pads and opponent player ship
        if self.other_rects == 0:
            self.other_rects = deepcopy(all_rects)
            if self.player == 'p1':
                self.own_index = 0                   # index with own rect in all_rects.
                del self.other_rects[self.own_index] # remove own rect from list.
            elif self.player == 'p2':   
                self.own_index = 1                   # index with own rect in all_rects
                del self.other_rects[self.own_index] # remove own rect from list.

        collidor = all_rects[self.own_index].collidelist(self.other_rects)

        x = self.other_rects[collidor].center[0] - self.rect.center[0]
        y = self.other_rects[collidor].center[1] - self.rect.center[1]
        self.rect.center


    def move(self):
        self.forward()
        self.grav()
        self.bounds()
        self.collisions()
        self.pos = self.newpos
        self.rect.center = (self.pos[0], self.pos[1])

        if self.thrust > 0:
            self.thrust -= 0.1
        else:
            self.thrust = 0

        if self.driftspeed > 0:
            self.driftspeed -= 0.1
        else:
            self.driftspeed = 0

    def reset(self):

        self.driftspeed=0
        self.thrust=0
        self.heading = 90
        self.orientation = self.heading
        self.newpos = self.original_pos


class Bullet(MovingObject, pg.sprite.Sprite):
    def __init(self, orientation, pos):
        print("1")
        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load("bullet.png")
        self.image.convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos

        flight_time = 0

        #MovingObject.__init__(self, display, 90, self.image, self.rect)

        BulletGroup.add(self)

    def bullet_move():
        if flight_time > 60:
            self.kill()
        flight_time += 1
        self.forward()
        self.pos = self.newpos
        self.rect.center = (self.pos[0], self.pos[1])


class FuelPad():
    def __init__(self, display, rect, color):
        self.display = display
        self.rect = pg.Rect(rect)
        self.color = color

    def draw(self):
        pg.draw.rect(self.display, self.color, self.rect)
        pg.draw.rect(self.display, WHITE, self.rect, 2)


if __name__ == '__main__':
    Game()
