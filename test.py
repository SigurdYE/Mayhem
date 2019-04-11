import pygame as pg


pg.init()
display = pg.display.set_mode((180,180))
clock = pg.time.Clock()
clock.tick(60)
while(1):
    pg.event.pump()
    if pg.event.peek(pg.QUIT):
        pg.quit()
        quit()
    if pg.key.get_pressed()[pg.K_ESCAPE]:
        pg.quit()
        quit()
    if pg.key.get_pressed()[pg.K_UP]:
        print("up")