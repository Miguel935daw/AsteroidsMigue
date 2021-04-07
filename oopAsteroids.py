######
# Version del tutorial de Real Python: https://realpython.com/asteroids-game-python/
import pygame
from pygame.math import Vector2
from pygame.transform import rotozoom, smoothscale
from random import randrange, choice
from math import copysign


def load_image(filename, with_alpha=True):
    image = pygame.image.load("images/" + filename + ".png")
    return image.convert_alpha() if with_alpha else image.convert()


def print_text(surface, text, font, color=pygame.Color("tomato")):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    rect.center = Vector2(surface.get_size()) / 2
    surface.blit(text_surface, rect)


class GameObject:
    def __init__(self, screen_size, position, sprite, velocity):
        self.screen_size = screen_size
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = velocity
        self._disabled = False

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)  # (radius, radius)
        surface.blit(self.sprite, blit_position)

    def update(self):
        self.position = self.position + self.velocity
        # manage out of bounds
        if self.position.x < -self.radius:
            self.position.x += self.screen_size.x + self.radius * 2
        elif self.position.x > self.screen_size.x + self.radius:
            self.position.x -= self.screen_size.x + self.radius * 2
        elif self.position.y < -self.radius:
            self.position.y += self.screen_size.y + self.radius * 2
        elif self.position.y > self.screen_size.y + self.radius:
            self.position.y -= self.screen_size.y + self.radius * 2

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

    def disable(self):
        self._disabled = True
        return self

    def is_disabled(self):
        return self._disabled

    def is_out_of_bounds(self):
        return self.position.x < -self.radius or self.position.x > self.screen_size.x + self.radius or \
               self.position.y < -self.radius or self.position.y > self.screen_size.y + self.radius


class Asteroid(GameObject):
    SPEEDS = [-2, -1.5, -1, 0.5, 0.5, 1, 1.5, 2]
    MIN_DISTANCE = 20

    def __init__(self, screen_size, star_ship, position=None, velocity=None):
        while position is None:
            position = Vector2(randrange(0, screen_size.x), randrange(0, screen_size.y))
            if position.distance_to(star_ship.position) < star_ship.radius * self.MIN_DISTANCE:
                position = None
        super().__init__(screen_size,
                         position,
                         load_image("asteroid.v2"),
                         velocity if velocity is not None
                         else Vector2(choice(self.SPEEDS), choice(self.SPEEDS)))


class Bullet(GameObject):
    BULLET_SPEED = 6

    def __init__(self, star_ship):
        super().__init__(star_ship.screen_size,
                         star_ship.position + star_ship.direction * star_ship.radius,
                         load_image("bullet"),
                         star_ship.direction * self.BULLET_SPEED)

    def update(self):
        self.position = self.position + self.velocity

    def is_disabled(self):
        return self._disabled or self.is_out_of_bounds()


class StarShip(GameObject):
    MANEUVERABILITY = 3
    FORCE = 0.1
    SPEED_LIMIT = 3
    SPRITES = {"normal": "star_ship.v2",
               "thrust": "star_ship.v2.thrust",
               "brake": "star_ship.v2.brake",
               }

    def __init__(self, screen_size):
        super().__init__(screen_size,
                         screen_size // 2,
                         load_image(self.SPRITES.get("normal")),
                         Vector2(0))
        self.direction = Vector2(0, -1)
        self._thrust_sprite = load_image(self.SPRITES.get("thrust"))
        self._brake_sprite = load_image(self.SPRITES.get("brake"))
        self._acceleration = 0

    def rotate(self, clockwise=False):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def thrust(self, brake=False):
        self._acceleration = -1 if brake else 1
        self.velocity += self.direction * self.FORCE * self._acceleration
        if abs(self.velocity.x) >= self.SPEED_LIMIT:
            self.velocity.x = copysign(1, self.velocity.x) * self.SPEED_LIMIT
        if abs(self.velocity.y) >= self.SPEED_LIMIT:
            self.velocity.y = copysign(1, self.velocity.y) * self.SPEED_LIMIT

    def draw(self, surface):
        real_sprite = self.sprite
        if self._acceleration < 0:
            real_sprite = self._brake_sprite
        elif self._acceleration > 0:
            real_sprite = self._thrust_sprite
        angle = self.direction.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(real_sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)
        self._acceleration = 0


class Asteroids:
    SIZE = Vector2(1024, 768)  # Display (width, height)
    MAX_ASTEROIDS = 15
    MUSIC = "music/tota_pop.ogg"
    WINDOW_TITLE = "Albert[A]steroids"
    BACKGROUND = "class_diagram"
    VICTORY_TEXT = "Victory!!!!!!!!!"
    GAME_OVER_TEXT = "Game Over"

    def __init__(self):  # public Asteroids() { ... } en Java - Constructor
        self._init_game()

    def _init_game(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(self.MUSIC)
        # loops=-1 for infinite playing
        pygame.mixer.music.play(loops=-1)
        pygame.display.set_caption(self.WINDOW_TITLE)
        # when attribute name starts with _ (underscore), marks that attribute as protected
        self._font = pygame.font.Font(None, 64)
        # set window size
        self._screen = pygame.display.set_mode([int(value) for value in self.SIZE.xy])
        self._background = load_image(self.BACKGROUND)
        # Background scale
        self._background = smoothscale(self._background, [int(value) for value in self.SIZE.xy])
        self._init_objects()

    def _init_objects(self):
        self._star_ship = StarShip(self.SIZE)
        self._bullets = []
        self._asteroids = [Asteroid(self.SIZE, self._star_ship)
                           for _ in range(self.MAX_ASTEROIDS)]

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            # shoot when press space
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._bullets.append(Bullet(self._star_ship))

        is_key_pressed = pygame.key.get_pressed()

        # control star ship movement
        if is_key_pressed[pygame.K_RIGHT]:
            self._star_ship.rotate(clockwise=True)
        elif is_key_pressed[pygame.K_LEFT]:
            self._star_ship.rotate(clockwise=False)
        elif is_key_pressed[pygame.K_UP]:
            self._star_ship.thrust()
        elif is_key_pressed[pygame.K_DOWN]:
            self._star_ship.thrust(brake=True)

    def _draw(self):
        self._screen.blit(self._background, (0, 0))
        for asteroid in self._asteroids:
            asteroid.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        self._star_ship.draw(self._screen)
        pygame.display.flip()

    def _update(self):
        for asteroid in self._asteroids:
            asteroid.update()
        for bullet in self._bullets:
            bullet.update()
        self._star_ship.update()
        # collisions
        for asteroid in self._asteroids[:]:
            destroyed = False
            for bullet in self._bullets[:]:
                if bullet.collides_with(asteroid):
                    self._asteroids.remove(asteroid)
                    self._bullets.remove(bullet)
                    destroyed = True
                    break
            if not destroyed and asteroid.collides_with(self._star_ship):
                self._star_ship.disable()
                break
        # clear out of bounds bullets
        for bullet in self._bullets[:]:
            if bullet.is_out_of_bounds():
                self._bullets.remove(bullet)

    def mainloop(self):
        clock = pygame.time.Clock()
        while True:
            while True:
                # manage input from keyboard
                self._handle_input()
                # update
                self._update()
                # draw (double buffer by PyGame)
                self._draw()
                # time sync 60fps
                clock.tick(60)
                # when self._asteroids is empty, self._asteroids == False
                if self._star_ship.is_disabled() or not self._asteroids:
                    break
            # process endgame or restart
            message = self.GAME_OVER_TEXT if self._star_ship.is_disabled() else self.VICTORY_TEXT
            print_text(self._screen, message, self._font)
            while True:
                pygame.display.flip()
                clock.tick(60)
                restart = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self._init_objects()
                        restart = True
                if restart:
                    break


if __name__ == '__main__':
    myAsteroids = Asteroids()  # new Asteroids() en java
    myAsteroids.mainloop()
