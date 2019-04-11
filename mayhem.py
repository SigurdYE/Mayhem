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

        self.ObstacleGroup = pg.sprite.Group()
        self.PadGroup = pg.sprite.Group()
        self.ShipGroup = pg.sprite.Group()
        self.BulletGroup = pg.sprite.Group()

        self.p1 = Ship(self.display, P1_STARTPOS, 1)
        self.p2 = Ship(self.display, P2_STARTPOS, 2)
        self.ShipGroup.add(self.p1, self.p2)

        self.pad1 = Square(self.display, "pad.png", PAD1_POS)
        self.pad2 = Square(self.display, "pad.png", PAD2_POS)
        self.PadGroup.add(self.pad1, self.pad2)

        self.obstacle = Square(self.display, "obstacle.png", 
                                (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.ObstacleGroup.add(self.obstacle)


        global all_rects
        all_rects = [self.p1.rect, self.p2.rect,
                     self.pad1.rect, self.pad2.rect]


        self.game_loop()

    def game_loop(self):
        while self.running:
            clock.tick(TICKRATE)
            self.keystrokes()

            for ship in self.ShipGroup.sprites():
                ship.move()
            for bullet in self.BulletGroup.sprites():
                bullet.move()
            
            self.display.fill((0, 0, 0))

            self.check_collisions()

            self.ShipGroup.draw(self.display)
            self.PadGroup.draw(self.display)
            self.BulletGroup.draw(self.display)
            self.ObstacleGroup.draw(self.display)
            self.scoreboard()
            pg.display.update()

        pg.quit()
        quit()

    def check_collisions(self):
        for ship in self.ShipGroup:

            # check if player collided with the other ship, destory both if yes
            collidor_ship = pg.sprite.spritecollideany(ship, self.ShipGroup)
            if collidor_ship != None and collidor_ship != ship:
                self.p1.score_down()
                self.p2.score_down()

            # check if player is on fuel pad
            collidor_pad = pg.sprite.spritecollideany(ship, self.PadGroup)
            if collidor_pad != None:
                ship.gravity_bool = False
                ship.drift_bool = False
                if ship.fuel < MAX_FUEL:
                    ship.fuel += FUEL_REGEN
            else:
                ship.gravity_bool = True
                ship.drift_bool = True

            # check if player collide with obstacle
            collidor_obstacle = pg.sprite.spritecollideany(ship, self.ObstacleGroup)
            if collidor_obstacle != None:
                ship.score_down()

            # check if player collide with bullet, no friendly fire
            collidor_bullet = pg.sprite.spritecollideany(ship, self.BulletGroup)
            if collidor_bullet != None:
                if ship == self.p1:
                    if collidor_bullet.player == self.p2:
                        self.p1.score_down()
                        self.p2.score += 1
                else:
                    if collidor_bullet.player == self.p1:
                        self.p2.score_down()
                        self.p1.score += 1


    def shoot(self, player):
        bullet = Bullet(player.orientation, player.rect.center, self.display, player)
        bullet.thrust = BULLET_SPEED
        self.BulletGroup.add(bullet)

    def keystrokes(self):
        keys_pressed = pg.key.get_pressed()
        if pg.event.peek(pg.QUIT):
            self.running = False

        if keys_pressed[pg.K_w]:
            self.shoot(self.p1) # p1 shoot
        if keys_pressed[pg.K_s]:
            if self.p1.fuel != 0:
                self.p1.fuel -= FUEL_LOSS
            if self.p1.thrust+self.p1.driftspeed < MAX_SHIPSPEED:
                self.p1.thrust += 0.4  # p1 accel
                self.p1.driftspeed += 0.4
        if keys_pressed[pg.K_a]:
            self.p1.rotate(2)  # p1 rot l
        if keys_pressed[pg.K_d]:
            self.p1.rotate(-2)  # p1 rot r

        if keys_pressed[pg.K_UP]:
            self.shoot(self.p2) # p2 shoot
        if keys_pressed[pg.K_DOWN]:
            if self.p2.fuel != 0:
                self.p2.fuel -= FUEL_LOSS
            if self.p2.thrust < MAX_SHIPSPEED:
                self.p2.thrust += 0.5 # p2 accel
        if keys_pressed[pg.K_LEFT]:
            self.p2.rotate(2) # p2 rot l
        if keys_pressed[pg.K_RIGHT]:
            self.p2.rotate(-2) # p2 rot r

        pg.event.clear()

    def scoreboard(self):
        pg.draw.rect(self.display, WHITE, (0,0,SCREEN_WIDTH,SCREEN_HEIGHT/20))

        self.font1 = pg.font.Font(None, 30)
        
        self.p1text = self.font1.render(f'Player 1: fuel = {self.p1.fuel}   score = {self.p1.score}', False, RED)
        self.p2text = self.font1.render(f'Player 2: fuel = {self.p2.fuel}   score = {self.p2.score}', False, BLUE)

        self.display.blit(self.p1text,(50,0))
        self.display.blit(self.p2text,((SCREEN_WIDTH/2+50),0))


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

        self.gravity_bool = True
        self.drift_bool = True

    def forward(self):
        multip = 1
        if self.drift_bool == False:
            multip = 0
        self.heading %= 360
        heading_rad = radians(self.heading)
        orientation_rad = radians(self.orientation)
        x = cos(orientation_rad)*self.driftspeed*multip + cos(orientation_rad)*self.thrust
        y = sin(orientation_rad)*self.driftspeed*multip + sin(orientation_rad)*self.thrust
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

    def grav(self, boolean):
        '''Total acceleration if a sum of forces divided by mass, 
        don't care about mass here. This method gives total acceleration
        equal to gravitational acceleration + acceleration from thrust.
        Not a 1-to-1 replica of real physics, but it is satisfactory.'''
        if boolean == False:
            return

        if self.gravspeed < 70:
            self.gravspeed += sin(radians(self.heading))*self.driftspeed + GRAVITY

        self.newpos[0] += 0
        self.newpos[1] += self.gravspeed*0.05


class Ship(MovingObject, pg.sprite.Sprite):
    def __init__(self, display, pos, player):
        pg.sprite.Sprite.__init__(self)
        self.display = display
        self.other_rects = 0
        self.player = player

        if self.player == 1:
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

    def score_down(self):
        if self.score > 0:
            self.score -= 1
            self.pos = self.original_pos
            self.driftspeed = 0
            # RESET ORIENTATION/

    def shoot(self):
        bullet = Bullet(self.orientation, self.rect.center, self.display, self.player)
        bullet.thrust = BULLET_SPEED

    def bounds(self):
        '''Keep ship within screen bounds'''

        collided = False
        for corner in self.ship_corners:
            if corner[0] < 0: # clean up newpos assignments below
                self.newpos = [self.rect.center[0]+1, self.newpos[1]]
                if self.driftspeed > 4:
                    collided = True
            if corner[0] > SCREEN_WIDTH:
                self.newpos = [self.rect.center[0]-1, self.newpos[1]]
                if self.driftspeed > 4:
                    collided = True
            if corner[1] < 0:
                self.newpos = [self.newpos[0], self.rect.center[1]+1]
                if self.driftspeed > 4:
                    collided = True
            if corner[1] > SCREEN_HEIGHT:
                self.newpos = [self.newpos[0], self.rect.center[1]-1]
                if self.driftspeed > 4:
                    collided = True
        if collided == True:
            #self.reset()
            collided = False


    def move(self):
        self.ship_corners = [self.rect.topleft, self.rect.bottomleft, 
                    self.rect.topright, self.rect.bottomright]
        self.forward()
        self.grav(self.gravity_bool)
        self.bounds()

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

        if self.fuel == 0:
            self.thrust = 0

    def reset(self):

        self.driftspeed=0
        self.thrust=0
        self.heading = 90
        self.orientation = self.heading
        self.newpos = self.original_pos


class Bullet(MovingObject, pg.sprite.Sprite):
    def __init__(self, orientation, pos, display, player):
        pg.sprite.Sprite.__init__(self)

        self.player = player

        self.image = pg.image.load("bullet.png")
        self.image.convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.flight_time = 0

        MovingObject.__init__(self, display, orientation, self.image, self.rect)

    def move(self):
        if self.flight_time > 200:
            self.kill()
        self.flight_time += 1
        self.forward()
        self.pos = self.newpos
        self.rect.center = (self.pos[0], self.pos[1])


class Square(pg.sprite.Sprite):
    def __init__(self, display, filename, pos):
        pg.sprite.Sprite.__init__(self)
        self.display = display
        self.image = pg.image.load(filename)
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos


if __name__ == '__main__':
    Game()
