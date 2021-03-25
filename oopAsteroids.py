######
## Version del tutorial de Real Python: https://realpython.com/asteroids-game-python/
import pygame


class Asteroids:
    SIZE = (800, 600)

    def __init__(self):
        pygame.init()
        # El _ (underscore) es para hacer el atributo protected
        self._screen = pygame.display.set_mode(self.SIZE)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.l:
                quit()

    def mainloop(self):
        while True:
            self._handle_input()
            # update
            # time sync
            # double buffer


if __name__ == '__main__':
    myAsteroids = Asteroids() # new Asteroids() en java
    myAsteroids.mainloop()
