import sys, pygame
from time import time

pygame.init()

size = width, height = 640, 480
speed = [1, 1]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("joker.png")
ballrect = ball.get_rect()
speed_counter = 20000
while 1:
    time_milis = round(time() * 1000)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    speed_counter += 1
    speed = [speed_value*speed_counter//20000 for speed_value in speed]

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
    # Bucle de espera
    while (round(time()*1000) - time_milis) < 1000//60:
        pass