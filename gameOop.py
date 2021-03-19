import pygame
import sys
from time import time


class Game:
    # Default values
    size = width, height = 640, 480
    speed = [1, 1]
    black = 0, 0, 0

    ###
    # Constructor
    # self == this (java)
    def __init__(self, width, height):
        self.size = self.width, self.height = width, height
        pygame.init()
        self.ball = self.resources()
        self.ball_rect = self.ball.get_rect()
        self.screen = pygame.display.set_mode(self.size)
        self.play()

    def resources(self):
        return pygame.image.load("joker.png")

    def play(self):
        while True:
            initial_time = self.time_millis()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.ball_rect = self.ball_rect.move(self.speed)
            if self.ball_rect.left < 0 or self.ball_rect.right > self.width:
                self.speed[0] = -self.speed[0]
            if self.ball_rect.top < 0 or self.ball_rect.bottom > self.height:
                self.speed[1] = -self.speed[1]

            self.screen.fill(self.black)
            self.screen.blit(self.ball, self.ball_rect)
            pygame.display.flip()
            # Bucle de espera
            while (self.time_millis() - initial_time) < 1000 // 60:
                pass

    def time_millis(self):
        return round(time() * 1000)
###
# public static void main(String[] args)
if __name__ == '__main__':
    Game(800, 600)
