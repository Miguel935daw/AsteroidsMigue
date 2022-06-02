######
# Version del tutorial de Real Python: https://realpython.com/asteroids-game-python/
import pygame
from pygame.math import Vector2
from pygame.transform import rotozoom, smoothscale
from random import randrange, choice
from math import copysign

def buscar_escudo(bulletsEnemigos, escudo): #Esta funcion comprueba si el escudo iterador coincide con el escudo desde el que se disparó la bala iteradora, de manera que 
    for bullet in bulletsEnemigos: #la bala siempre es disparada por el mismo escudo
        if bullet.LAUNCHER == escudo:
            return False
    return True

def load_image(filename, with_alpha=True):
    image = pygame.image.load("images/" + filename + ".png")
    return image.convert_alpha() if with_alpha else image.convert()


def print_text(surface, text, font, color=pygame.Color("tomato")): #Esta función se encarga de mostrar Game Over o Victory al final de la partida
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    rect.center = Vector2(surface.get_size()) / 2
    surface.blit(text_surface, rect)


class GameObject: #Clase padre para el resto de clases para el juego
    def __init__(self, screen_size, position, sprite, velocity): #Constructor de la clase
        self.screen_size = screen_size
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = velocity
        self._disabled = False

    def draw(self, surface): #Se encarga de mostrar pintar en pantalla el sprite del objeto
        blit_position = self.position - Vector2(self.radius)  # (radius, radius)
        surface.blit(self.sprite, blit_position)

    def update(self): #Se encarga de actualizar la posición del objeto en cuestión
        if type(self) == Boss: #En caso de que la clase que esté usando el método sea Boss
            if self.position == Vector2(512,200) and self.fight: #Cuando llegue a la posición indicada su velocidad cambia y comienza la batalla
                self.velocity = Vector2(-1,0)
                self.fight = False
            if self.position == Vector2(512,200) - Vector2(312,0)  or self.position == Vector2(512,200) + Vector2(312,0):
                self.velocity = self.velocity * -1
        if type(self) == Escudos: #En caso de que la clase que esté usando el método sea Escudos, invertirá la velocidad al llegar al final de la pantalla
            if self.position == self.POSICION_ORIGINAL - Vector2(312,0) or self.position == self.POSICION_ORIGINAL + Vector2(312,0):
                self.velocity = self.velocity * -1
        self.position = self.position + self.velocity #Genera el movimiento del objeto en pantalla, actualizando la posicion mediante la velocidad
        #Esta cadena de condicionales gestiona los objetos cuando salen de la pantalla 
        if self.position.x < -self.radius:
            self.position.x += self.screen_size.x + self.radius * 2
        elif self.position.x > self.screen_size.x + self.radius:
            self.position.x -= self.screen_size.x + self.radius * 2
        elif self.position.y < -self.radius:
            self.position.y += self.screen_size.y + self.radius * 2
        elif self.position.y > self.screen_size.y + self.radius:
            self.position.y -= self.screen_size.y + self.radius * 2
        

    def collides_with(self, other_obj): #Comprueba si un objeto está colisionando con otro
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

    def disable(self):
        self._disabled = True
        return self

    def is_disabled(self):
        return self._disabled

    def is_out_of_bounds(self): #Comprueba si el objeto está fuera de la pantalla
        return self.position.x < -self.radius or self.position.x > self.screen_size.x + self.radius or \
            self.position.y < -self.radius or self.position.y > self.screen_size.y + self.radius

'''***************************************************************************
   *****                    TIPOS DE ASTEROIDE                          ******
   ***************************************************************************'''
class Asteroid(GameObject):
    SPEEDS = [-2, -1.5, -1, 0.5, 0.5, 1, 1.5, 2]
    MIN_DISTANCE = 20
    SPRITE = None
    CATEGORY = None
    def __init__(self, screen_size, star_ship, category, position=None, velocity=None):
        self.CATEGORY = category
        if category == 1:
            self.SPRITE = load_image("asteroid.v2") #Asteroide Grande
        elif category == 2:
             self.SPRITE = load_image("asteroid.v3") #Asteroide Mediano
        elif category == 3:
            self.SPRITE = load_image("asteroid.v4") #Asteroide Pequeño
        while position is None:
            position = Vector2(randrange(0, screen_size.x), randrange(0, screen_size.y))
            if position.distance_to(star_ship.position) < star_ship.radius * self.MIN_DISTANCE:
                position = None
        super().__init__(screen_size, #Llama al constructor de la clase padre
                         position,
                         self.SPRITE,
                         velocity if velocity is not None
                         else Vector2(choice(self.SPEEDS), choice(self.SPEEDS)))

'''****************************************************************
   *****                    JUGADOR                          ******
   ****************************************************************'''
class StarShip(GameObject): #Nave del Jugador
    LIVES = 3 #Vidas del jugador
    MANEUVERABILITY = 3
    FORCE = 0.1
    SPEED_LIMIT = 3 #Velocidad máxima que puede alcanzar
    SPRITES = {"normal": "star_ship.v2", #Sprite base
               "thrust": "star_ship.v2.thrust", #Sprite motor trasero
               "brake": "star_ship.v2.brake", #Sprite motor delantero
               "inmunity thrust": "invulnerable2", #Sprite motor trasero mientras es inmune
               "inmunity brake": "invulnerable1", #Sprite motor delantero mientras es inmune
               "inmunity": "invulnerable"} #Sprite mientras es inmune
    INMUNITY = 0 #Este atributo indica si la nave está siendo inmune o no, mientras sea 0 significa que la nave puede recibir daño, en caso contrario no

    def __init__(self, screen_size): #Se llama al constructor de la clase Padre
        super().__init__(screen_size,
                         screen_size // 2,
                         load_image(self.SPRITES.get("normal")),
                         Vector2(0))
        self.direction = Vector2(0, -1)
        self._thrust_sprite = load_image(self.SPRITES.get("thrust")) #Atributos con los Sprites ya cargados
        self._brake_sprite = load_image(self.SPRITES.get("brake"))
        self._thrust_inmunity = load_image(self.SPRITES.get("inmunity thrust"))
        self._brake_inmunity = load_image(self.SPRITES.get("inmunity brake"))
        self._inmunity = load_image(self.SPRITES.get("inmunity"))
        self._acceleration = 0

    def rotate(self, clockwise=False): #Permite girar la nave del jugador
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def thrust(self, brake=False): #Este método hace que la nave a diferencia del resto de objetos se mueva por propulsión
        self._acceleration = -1 if brake else 1
        self.velocity += self.direction * self.FORCE * self._acceleration
        if abs(self.velocity.x) >= self.SPEED_LIMIT:
            self.velocity.x = copysign(1, self.velocity.x) * self.SPEED_LIMIT
        if abs(self.velocity.y) >= self.SPEED_LIMIT:
            self.velocity.y = copysign(1, self.velocity.y) * self.SPEED_LIMIT

    def draw(self, surface): #Se hace override del método de la lase padre para añadir las rotaciones, y los cambios de sprite según la situación de la nave
        real_sprite = self.sprite
        if self.INMUNITY > 0:
            real_sprite = self._inmunity
        if self._acceleration < 0 and self.INMUNITY > 0:
            real_sprite = self._brake_inmunity
        if self._acceleration < 0 and self.INMUNITY == 0:
            real_sprite = self._brake_sprite
        if self._acceleration > 0 and self.INMUNITY > 0:
            real_sprite = self._thrust_inmunity
        if self._acceleration > 0 and self.INMUNITY == 0:
            real_sprite = self._thrust_sprite
        angle = self.direction.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(real_sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)
        self._acceleration = 0

class Bullet(GameObject): #Bala disparada por el jugador
    PLAYER_BULLET_SPEED = 6
    ENEMY_BULLET_SPEED = 3
    LAUNCHER = None
    def __init__(self, launcher, enemy: bool):
        self.LAUNCHER = launcher #El parámetro launcher debe ser o bien un objeto StarShip o bien un objeto Escudos, ya que son los únicos que disparan
        if not enemy: #El parámetro enemy indicará si la bala será disparada por el jugador, o los enemigos
            super().__init__(launcher.screen_size,
                            launcher.position + launcher.direction * launcher.radius, #Posicion desde la que se dispara
                            load_image("bullet"),
                            launcher.direction * self.PLAYER_BULLET_SPEED)
        else:
            super().__init__(launcher.screen_size,
                         launcher.position + Vector2(0,1) * launcher.radius,
                         load_image("bulletenemigo"),
                         Vector2(0,1) * self.ENEMY_BULLET_SPEED)

    def update(self): #Se hace override a este metodo para que la bala se elimine al salir de la pantalla, es decir no se gestione como el resto de objetos
        self.position = self.position + self.velocity

    def is_disabled(self):
        return self._disabled or self.is_out_of_bounds()

class PlayerLifes(GameObject): #Vidas del Jugador
    SPRITES = {3 : "PlayerLife3",
               2 : "PlayerLife2",
               1 : "PlayerLife1",
               0 : "PlayerLife0"
               }
    player: StarShip #Este atributo almacena la nave creada en la partida para tener acceso a sus atributos, principalmente al atributo INMUNITY y al atributo LIVES
    def __init__(self, screen_size, player):
        self.player = player
        super().__init__(screen_size,
                          Vector2(70,80),
                         load_image(self.SPRITES.get(3)),
                         Vector2(0))
    def update(self): #Se hace override al método de la clase padre *update* para adaptarla al objeto
        if self.player.LIVES == 2: 
            self.sprite = load_image(self.SPRITES.get(2))
        if self.player.LIVES == 1:
           self.sprite = load_image(self.SPRITES.get(1))
        if self.player.LIVES == 0:
           self.sprite = load_image(self.SPRITES.get(0))

'''************************************************************
   ********            FINAL BOSS                   ***********
   ************************************************************'''

class Escudos(GameObject): #Escudos del Boss
    POSICION_ORIGINAL = None #Guarda la primera posición del objeto
    IDENTIFICADOR = 4 #Esta variable identificador será usada más tarde para crear un canal por cada disparo de estos objetos, de esta manera se evita el solapamiento del sonido
    def __init__(self, screen_size, position, velocity=None):
        self.IDENTIFICADOR+=1
        if self.IDENTIFICADOR ==20: #Cuando llega a 20 se resetea para no crear canales infinitos sino reutilizar los que ya han reproducido el sonido y por lo tanto se pueden reutilizar
            self.IDENTIFICADOR=4
        self.POSICION_ORIGINAL = position
        super().__init__(screen_size,
                         position,
                         load_image("escudopng"),
                         velocity if velocity is not None
                         else Vector2(-1, 0))

class Boss(GameObject): #Boss Final
    LIVES = 6
    fight = True #Este atributo lo usaremos para saber si ya ha comenzado la batalla y por tanto ya puede recibir daño el boss
    def __init__(self, screen_size, position, velocity=None):
        super().__init__(screen_size,
                         position,
                         load_image("Boss"),
                         velocity if velocity is not None
                         else Vector2(0, 0.5))

class BossLife(GameObject): #Mismo funcionamiento que la clase PlayerLifes
    SPRITES = {6 : "BossLife6",
               5 : "BossLife5",
               4 : "BossLife4",
               3 : "BossLife3",
               2 : "BossLife2",
               1 : "BossLife1",
               0 : "BossLife0"
               }
    boss:Boss
    
    def __init__(self, screen_size, boss):
        self.boss = boss
        super().__init__(screen_size,
                          Vector2(512,650),
                         load_image(self.SPRITES.get(6)),
                         Vector2(0))

    def update(self): #Se hace override al método de la clase padre *update* para adaptarla al objeto
        if self.boss.LIVES == 5:
            self.sprite = load_image(self.SPRITES.get(5))
        if self.boss.LIVES == 4:
           self.sprite = load_image(self.SPRITES.get(4))
        if self.boss.LIVES == 3:
           self.sprite = load_image(self.SPRITES.get(3))
        if self.boss.LIVES == 2:
            self.sprite = load_image(self.SPRITES.get(2))
        if self.boss.LIVES == 1:
           self.sprite = load_image(self.SPRITES.get(1))
        if self.boss.LIVES == 0:
           self.sprite = load_image(self.SPRITES.get(0))

''' ******************************************************
    ********                JUEGO                 ********
    ******************************************************'''
class Asteroids:
    SIZE = Vector2(1024, 768)  # Display (width, height)
    MAX_ASTEROIDS = 10
    MUSIC = "music/tota_pop.ogg"
    WINDOW_TITLE = "ASTEROIDS MIGUEL VERSION"
    BACKGROUND = "background"
    VICTORY_TEXT = "Victory!!!!!!!!!"
    GAME_OVER_TEXT = "Game Over"

    def __init__(self):  # public Asteroids() { ... } en Java - Constructor
        self._init_game()

    def _init_game(self):
        pygame.init() #Comienza el Juego
        pygame.mixer.init() #Comienza el reproductor de sonido de pygame
        pygame.mixer.set_num_channels(21) #Se establece el número de canales en 21
        pygame.mixer.Channel(1).set_volume(0.1) #Se establece el volumen de los canales para que no sea demasiado alto
        pygame.mixer.Channel(2).set_volume(0.1)
        pygame.mixer.Channel(3).set_volume(0.1)
        pygame.mixer.Channel(1).play(pygame.mixer.Sound(self.MUSIC),-1) #Se comienza a reproducir el canal 1, con la cancion de fondo
        pygame.display.set_caption(self.WINDOW_TITLE)
        # when attribute name starts with _ (underscore), marks that attribute as protected
        self._font = pygame.font.Font(None, 64)
        # set window size
        self._screen = pygame.display.set_mode([int(value) for value in self.SIZE.xy])
        self._background = load_image(self.BACKGROUND)
        # Background scale
        self._background = smoothscale(self._background, [int(value) for value in self.SIZE.xy])
        self._init_objects()

    def _init_objects(self): #Crea los atributos para alamcenar los objetos que se van a usar en la partida
        self._star_ship = StarShip(self.SIZE) #Nave del jugador
        self._playerLife = PlayerLifes(self.SIZE,player = self._star_ship) #Vidas del jugador   
        self._bullets = [] #Balas disparadas por el jugador
        self._asteroids = [] #Asteroides en pantalla
        self._boss = None #Boss
        self._bossLife = None #Vida del Boss
        self._escudos = [] #Escudos del Boss
        self._bulletsEnemigos = [] #Balas disparadas por los escudos

        for _ in range(self.MAX_ASTEROIDS):
            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, category = 1))

    def _handle_input(self): #Método para que el programa entienda las pulsaciones de las teclas durante la partida
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            # shoot when press space
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/PlayerShot.ogg'))
                self._bullets.append(Bullet(self._star_ship,False))

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

    def _draw(self): #Método para dibujar en pantalla los objetos 
        self._screen.blit(self._background, (0, 0))
        for asteroid in self._asteroids: 
            asteroid.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        self._playerLife.draw(self._screen)
        self._playerLife.update()
        self._star_ship.draw(self._screen)
        if self._boss is not None: #Dado que el boss solo aparece en el tercer nivel, este se dibuja cuando es almacenado en el atributo
            self._boss.draw(self._screen)
        if self._bossLife is not None: #Solo se dibuja en pantalla cuando ya ha comenzado la batalla con el boss
            self._bossLife.draw(self._screen)
            self._bossLife.update()
        if len(self._escudos) != 0:
            for escudo in self._escudos:
                escudo.draw(self._screen)
            for disparo in self._bulletsEnemigos:
                disparo.draw(self._screen)
            
        pygame.display.flip()

    def phase1(self):
        for asteroid in self._asteroids: #Actualiza cada uno de los asteroides en pantalla
            asteroid.update()
        for bullet in self._bullets: #Actuliza cada bala en pantalla
            bullet.update()
            if bullet.is_out_of_bounds():#Se borran las balas que salen de la pantalla
                self._bullets.remove(bullet)
        self._star_ship.update()  #Actuliza la nave del jugador
        #Este bucle comprueba si alguna bala del jugador colisiona con un asteroide, en ese caso lo elimina de la pantalla
        for asteroid in self._asteroids[:]:
            destroyed = False
            for bullet in self._bullets[:]:
                if bullet.collides_with(asteroid):
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/AsteroidSound.ogg')) #Reproduce sonido de destrucción
                    self._asteroids.remove(asteroid)
                    self._bullets.remove(bullet)
                    destroyed = True
                    break
            if not destroyed and asteroid.collides_with(self._star_ship) and self._star_ship.INMUNITY==0: #En caso de que un asteroide colisione con la nave y ésta no este en modo inmune pierde una vida, y activa el modo inmune
                self._star_ship.LIVES-=1
                self._star_ship.INMUNITY+=1 #Comienza la inmunidad del jugador
                if self._star_ship.LIVES==0: #Cuando la vida del jugaro sea 0 se acaba la partida
                    self._star_ship.disable()
                    break
            if self._star_ship.INMUNITY>0: #Se entiende que el jugador es inmune mientras el atributo inmune sea mayor de 0, la inmunidad dura 999 vueltas del bucle
                self._star_ship.INMUNITY+=1
                if self._star_ship.INMUNITY==1000:
                    self._star_ship.INMUNITY=0

    def phase2(self):
        for asteroid in self._asteroids: #Actualiza cada uno de los asteroides en pantalla
            asteroid.update()
        for bullet in self._bullets: #Actuliza cada bala en pantalla
            bullet.update()
            if bullet.is_out_of_bounds():#Se borran las balas que salen de la pantalla
                self._bullets.remove(bullet)
        self._star_ship.update() #Actuliza la nave del jugador
        #El bucle tiene la misma función que en la phase1, pero esta vez al destruir un asteroide comprueba su gategoria y según ésta, aparecerán asteroides más pequeños o no
        for asteroid in self._asteroids[:]:
            destroyed = False
            for bullet in self._bullets[:]:
                if bullet.collides_with(asteroid):
                        posicion = asteroid.position
                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/AsteroidSound.ogg')) #Reproduce sonido de destrucción
                        if asteroid.CATEGORY == 1:
                            self._asteroids.remove(asteroid)
                            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, position = posicion, category = 2)) #Aparecen Asteroides medianos
                            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, position = posicion, category = 2))
                            self._bullets.remove(bullet)
                            destroyed = True
                        elif asteroid.CATEGORY == 2:
                            self._asteroids.remove(asteroid)
                            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, position = posicion, category = 3)) #Aparecen Asteroides pequeños
                            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, position = posicion, category = 3))           
                            self._bullets.remove(bullet)
                            destroyed = True
                        else:
                            self._asteroids.remove(asteroid)
                            self._bullets.remove(bullet)
                            destroyed = True
                            break
            if not destroyed and asteroid.collides_with(self._star_ship) and self._star_ship.INMUNITY==0: #Sistema de inmunidad explicado en la phase1
                self._star_ship.LIVES-=1
                self._star_ship.INMUNITY+=1
                if self._star_ship.LIVES==0:
                    self._star_ship.disable()
                    break
            if self._star_ship.INMUNITY>0:
                self._star_ship.INMUNITY+=1
                if self._star_ship.INMUNITY==1000:
                    self._star_ship.INMUNITY=0
        

    
    def boss_phase(self):
        for bullet in self._bullets: #Actuliza cada bala del jugador en pantalla
            bullet.update()
            if bullet.is_out_of_bounds():
                self._bullets.remove(bullet)
        for bullet in self._bulletsEnemigos: #Actualiza cada bala del enemigo en pantalla
            bullet.update()
            if bullet.collides_with(self._star_ship) and self._star_ship.INMUNITY==0: #Comprueba si alguna bala enemiga colisiona con el jugador y sigue el procedimiento correspondiente
                self._star_ship.LIVES-=1
                self._star_ship.INMUNITY+=1
                if self._star_ship.LIVES==0:
                    self._star_ship.disable()
                    break
            if self._star_ship.INMUNITY>0:
                self._star_ship.INMUNITY+=1
                if self._star_ship.INMUNITY==1000:
                    self._star_ship.INMUNITY=0

            if bullet.is_out_of_bounds():
                self._bulletsEnemigos.remove(bullet)

        self._star_ship.update() #Actualiza la nave del jugador
        escudos = [Escudos(self.SIZE, position=Vector2(512,50), velocity=None), #Escudos del Boss
                    Escudos(self.SIZE, position=Vector2(512,300), velocity=None),
                    Escudos(self.SIZE, position=Vector2(452,70), velocity=None),
                    Escudos(self.SIZE, position=Vector2(452,280), velocity=None),
                    Escudos(self.SIZE, position=Vector2(392,110), velocity=None),
                    Escudos(self.SIZE, position=Vector2(392,240), velocity=None),
                    Escudos(self.SIZE, position=Vector2(332,150), velocity=None),
                    Escudos(self.SIZE, position=Vector2(332,200), velocity=None),
                    Escudos(self.SIZE, position=Vector2(572,70), velocity=None),
                    Escudos(self.SIZE, position=Vector2(572,280), velocity=None),
                    Escudos(self.SIZE, position=Vector2(632,110), velocity=None),
                    Escudos(self.SIZE, position=Vector2(632,240), velocity=None),
                    Escudos(self.SIZE, position=Vector2(692,150), velocity=None),
                    Escudos(self.SIZE, position=Vector2(692,200), velocity=None)]
        
        for escudo in self._escudos:
            escudo.update() #Actualiza los escudos
            if escudo.position.y>=200 and len(self._bulletsEnemigos)-1<7: #Solo disparan los escudos delanteros, y disparan una nueva bala cada vez que la que ya está en pantalla sale de la misma
                if buscar_escudo(self._bulletsEnemigos,escudo):
                    pygame.mixer.Channel(escudo.IDENTIFICADOR).set_volume(0.1)
                    pygame.mixer.Channel(escudo.IDENTIFICADOR).play(pygame.mixer.Sound('music/BossShot.ogg'))
                    self._bulletsEnemigos.append(Bullet(escudo,True))
            destroyed = False
            for bullet in self._bullets[:]: #Comprueba si alguna bala del jugador colisiona con algún escudo, en ese caso lo elimina
                if bullet.collides_with(escudo):
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/AsteroidSound.ogg'))
                    self._escudos.remove(escudo)
                    self._bullets.remove(bullet)
                    destroyed = True
                    break
            if not destroyed and escudo.collides_with(self._star_ship) and self._star_ship.INMUNITY==0: #Comprueba si el jugador colisiona con los escudos, y sigue el procedimiento correspondiente
                self._star_ship.LIVES-=1
                self._star_ship.INMUNITY+=1
                if self._star_ship.LIVES==0:
                    self._star_ship.disable()
                    break
            if self._star_ship.INMUNITY>0:
                self._star_ship.INMUNITY+=1
                if self._star_ship.INMUNITY==1000:
                    self._star_ship.INMUNITY=0
        if self._boss:
            for bullet in self._bullets[:]:
                if bullet.collides_with(self._boss) and self._boss.position.y==200: #Mismo procedimiento para saber si alguna bala del jugador colisiona con el boss, 
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/AsteroidSound.ogg')) #para que este pueda ser dañado debe haber llegado a su posición.y fija, 
                    self._boss.LIVES-=1                                            #de esta manera se evita que el jugador lo peuda matar antes de que salgan sus escudos
                    self._bullets.remove(bullet)
                if self._boss.LIVES == 0: 
                    break
            self._boss.update()    
            if self._boss.position == Vector2(512,200) and len(self._escudos) == 0: #Cuando el boss llegue a su posicón y comience la batalla aparecerán los escudos
                self._escudos.extend(escudos)
                self._bossLife = BossLife(self._screen,self._boss)
             
    def mainloop(self):
        clock = pygame.time.Clock()
        while True:
            while True:
                # manage input from keyboard
                self._handle_input()
                # update
                self.phase1()
                # draw (double buffer by PyGame)
                self._draw()
                # time sync 60fps
                clock.tick(60)
                # when self._asteroids is empty, self._asteroids == False
                if self._star_ship.is_disabled() or not self._asteroids: #Se termina el nivel si el jugador a muerto o a conseguido destruir todos los asteroides
                    break
            if not self._star_ship.is_disabled(): #Solo comenzará el siguiente nivel en caso de que el nivel anterior haya terminado y el jugador siga vivo
                while True:
                    self._handle_input()
                    if not self._asteroids: #Se reponen los asteroides
                        for _ in range(5):
                            self._asteroids.append(Asteroid(self.SIZE, self._star_ship, category = 1))
                    self.phase2()
                    self._draw()
                    # time sync 60fps
                    clock.tick(60)
                    if self._star_ship.is_disabled() or not self._asteroids: #Se termina el nivel si el jugador a muerto o a conseguido destruir todos los asteroides
                        break
                if not self._star_ship.is_disabled(): #Solo comenzará el siguiente nivel en caso de que el nivel anterior haya terminado y el jugador siga vivo
                    self.MUSIC = 'music/bossmusic.ogg' #Se sustituye la musica de fondo por la música de jefe final
                    pygame.mixer.init()
                    pygame.mixer.music.load(self.MUSIC)
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound(self.MUSIC),-1)
                    while True:
                        self._handle_input()
                        if self._boss is None:
                            self._boss = Boss(self.SIZE, position=Vector2(512,-80), velocity=None)
                        self.boss_phase()
                        self._draw()
                        # time sync 60fps
                        clock.tick(60)
                        if self._star_ship.is_disabled() or self._boss.LIVES==0:
                            break
            # process endgame or restart
            message = self.GAME_OVER_TEXT if self._star_ship.is_disabled() else self.VICTORY_TEXT
            print_text(self._screen, message, self._font) #Mensaje de game over
            while True:
                pygame.display.flip()
                clock.tick(60)
                restart = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): #Si se pulsa la tecla ESC se sale del juego
                        quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #Si se pulsa la tecla SPACE se comienza una nueva partida
                        self._init_objects()
                        restart = True
                        self.MUSIC = 'music/tota_pop.ogg' #La musica de fondo vuelve a ser la normal
                        pygame.mixer.init()
                        pygame.mixer.music.load(self.MUSIC)
                        # loops=-1 for infinite playing
                        pygame.mixer.Channel(1).play(pygame.mixer.Sound(self.MUSIC),-1)
                if restart:
                    break


if __name__ == '__main__':
    myAsteroids = Asteroids()  # new Asteroids() en java
    myAsteroids.mainloop()
