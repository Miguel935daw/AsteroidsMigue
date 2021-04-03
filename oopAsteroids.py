######
## Version del tutorial de Real Python: https://realpython.com/asteroids-game-python/
import pygame
from pygame.math import Vector2
from pygame.transform import rotozoom
from random import randrange, choice
from time import time
from math import copysign


def load_image(filename, with_alpha=True):
    image = pygame.image.load("images/"+filename+".png")
    return image.convert_alpha() if with_alpha else image.convert()


class GameObject:
    def __init__(self, screen_size, position, sprite, velocity):
        self._screen_size = screen_size
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = velocity

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)  # (radius, radius)
        surface.blit(self.sprite, blit_position)

    def update(self):
        self.position = self.position + self.velocity
        if self.position.x < -self.radius:
            self.position.x += self._screen_size[0] + self.radius
        elif self.position.x > self._screen_size[0] + self.radius:
            self.position.x -= self._screen_size[0] + self.radius
        elif self.position.y < -self.radius:
            self.position.y += self._screen_size[1] + self.radius
        elif self.position.y > self._screen_size[1] + self.radius:
            self.position.y -= self._screen_size[1] + self.radius
        # TODO: Control asteroid collision
        # for other_asteroid in all_asteroids:
        #     if other_asteroid.position != self.position:
        #         if self.collides_with(other_asteroid):
        #             self.velocity = - self.velocity

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Asteroid(GameObject):
    SPEEDS = [-2, -1.5, -1, 0.5, 0.5, 1, 1.5, 2]

    def __init__(self, screen_size, position=None, velocity=None):
        super().__init__(screen_size,
                         position if position is not None else Vector2(randrange(0, screen_size[0]), randrange(0, screen_size[1])),
                         load_image("asteroid"),
                         velocity if velocity is not None else Vector2(choice(self.SPEEDS), choice(self.SPEEDS)))


class Bullet(GameObject):
    BULLET_SPEED = 6

    def __init__(self, starship):
        super().__init__(starship._screen_size,
                         starship.position + starship.direction * starship.radius,
                         load_image("bullet"),
                         starship.direction * self.BULLET_SPEED)
        self._disabled = False

    def update(self):
        self.position = self.position + self.velocity

    def disable(self):
        self._disabled = True
        return self

    def is_disabled(self):
        return self._disabled or self.is_outbounds()


class Starship(GameObject):
    MANEUVERABILITY = 3
    FORCE = 0.1
    SPEED_LIMIT = 3

    def __init__(self, screen_size):
        super().__init__(screen_size, screen_size//2, load_image("starship"), Vector2(0))
        self.direction = Vector2(0, -1)

    def rotate(self, clockwise=False):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def thrust(self, brake=False):
        accel = -1 if brake else 1
        self.velocity += self.direction * self.FORCE * accel
        if abs(self.velocity.x) >= self.SPEED_LIMIT:
            self.velocity.x = copysign(1, self.velocity.x) * self.SPEED_LIMIT
        if abs(self.velocity.y) >= self.SPEED_LIMIT:
            self.velocity.y = copysign(1, self.velocity.y) * self.SPEED_LIMIT

    def draw(self, surface):
        angle = self.direction.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Asteroids:
    SIZE = Vector2(800, 600) # Display (width, height)
    MAX_ASTEROIDS = 6

    def __init__(self): # public Asteroids() { ... } en Java - Constructor
        self._init_game()

    def _init_game(self):
        pygame.init()
        pygame.display.set_caption("Rocas caleteras")
        # El _ (underscore) es para hacer el atributo protected
        self._screen = pygame.display.set_mode([int(value) for value in self.SIZE.xy])
        self._background = load_image("background")
        self._starship = Starship(self.SIZE)
        self._bullets = []
        self._asteroids = [Asteroid(self.SIZE)
                           for _ in range(self.MAX_ASTEROIDS)]

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._bullets.append(Bullet(self._starship))

        is_key_pressed = pygame.key.get_pressed()

        if is_key_pressed[pygame.K_RIGHT]:
            self._starship.rotate(clockwise=True)
        elif is_key_pressed[pygame.K_LEFT]:
            self._starship.rotate(clockwise=False)
        elif is_key_pressed[pygame.K_UP]:
            self._starship.thrust()
        elif is_key_pressed[pygame.K_DOWN]:
            self._starship.thrust(brake=True)

    def _draw(self):
        self._screen.blit(self._background, (0, 0))
        for asteroid in self._asteroids:
            asteroid.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        self._starship.draw(self._screen)
        pygame.display.flip()

    def _update(self):
        for asteroid in self._asteroids:
            asteroid.update()
        for bullet in self._bullets:
            bullet.update()
        self._starship.update( )

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
