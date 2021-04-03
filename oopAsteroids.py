######
## Version del tutorial de Real Python: https://realpython.com/asteroids-game-python/
import pygame
from pygame.math import Vector2
from pygame.transform import rotozoom
from random import randrange, choice
from time import time


def load_image(filename, with_alpha=True):
    image = pygame.image.load("images/"+filename+".png")
    return image.convert_alpha() if with_alpha else image.convert()


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = velocity

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)  # (radius, radius)
        surface.blit(self.sprite, blit_position)

    def update(self, screen_size):
        self.position = self.position + self.velocity
        if self.position.x < -self.radius:
            self.position.x += screen_size[0] + self.radius
        elif self.position.x > screen_size[0] + self.radius:
            self.position.x -= screen_size[0] + self.radius
        elif self.position.y < -self.radius:
            self.position.y += screen_size[1] + self.radius
        elif self.position.y > screen_size[1] + self.radius:
            self.position.y -= screen_size[1] + self.radius
        # TODO: Control asteroid collision
        # for other_asteroid in all_asteroids:
        #     if other_asteroid.position != self.position:
        #         if self.collides_with(other_asteroid):
        #             self.velocity = - self.velocity

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Starship(GameObject):
    MANEUVERABILITY = 3

    def __init__(self, position):
        super().__init__(position, load_image("starship"), Vector2(0))
        self.direction = Vector2(0, -1)

    def rotate(self, clockwise=False):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Asteroids:
    SIZE = (800, 600) # Display (width, height)
    MAX_ASTEROIDS = 10
    SPEEDS = [-3, -2, -1, 1, 2, 3]

    def __init__(self): # public Asteroids() { ... } en Java - Constructor
        self._init_game()

    def _init_game(self):
        pygame.init()
        pygame.display.set_caption("Rocas caleteras")
        # El _ (underscore) es para hacer el atributo protected
        self._screen = pygame.display.set_mode(self.SIZE)
        self._background = load_image("background")
        self._asteroid_image = load_image("asteroid")
        self._starship = Starship(Vector2(self.SIZE[0]//2, self.SIZE[1]//2))
        self._asteroids = [GameObject(Vector2(randrange(0, self.SIZE[0]), randrange(0, self.SIZE[1])),
                                      self._asteroid_image,
                                      Vector2(choice(self.SPEEDS), choice(self.SPEEDS)))
                           for _ in range(self.MAX_ASTEROIDS)]

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

        is_key_pressed = pygame.key.get_pressed()

        if is_key_pressed[pygame.K_RIGHT]:
            self._starship.rotate(clockwise=True)
        elif is_key_pressed[pygame.K_LEFT]:
            self._starship.rotate(clockwise=False)

    def _draw(self):
        self._screen.blit(self._background, (0, 0))
        for asteroid in self._asteroids:
            asteroid.draw(self._screen)
        self._starship.draw(self._screen)
        pygame.display.flip()

    def _update(self):
        for asteroid in self._asteroids:
            asteroid.update(self.SIZE)
        self._starship.update(self.SIZE)

    def mainloop(self):
        clock = pygame.time.Clock()
        while True:
            self._handle_input()
            # update
            self._update()
            # draw (double buffer by PyGame)
            self._draw()
            # time sync 60fps
            clock.tick(60)


if __name__ == '__main__':
    myAsteroids = Asteroids() # new Asteroids() en java
    myAsteroids.mainloop()
