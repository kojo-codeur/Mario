import pygame
import sys
import random
import math

# Initialisation de Pygame et du module de son (mixer)
pygame.init()
try:
    # Tentative d'initialisation du mixer avec des paramètres spécifiques
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    print("Pygame mixer initialized successfully")
except pygame.error as e:
    # En cas d'échec, désactiver la musique
    print(f"Mixer initialization failed: {e}")
    music_enabled = False  # Désactive la musique si le mixer échoue

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600  # Dimensions de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de la fenêtre
pygame.display.set_caption("Super Mario en Action")  # Titre de la fenêtre

# Chargement des polices de caractères
try:
    # Tentative de chargement des polices personnalisées
    title_font = pygame.font.Font("freesansbold.ttf", 64)
    subtitle_font = pygame.font.Font("freesansbold.ttf", 32)
    menu_font = pygame.font.Font("freesansbold.ttf", 40)
    hud_font = pygame.font.Font("freesansbold.ttf", 28)
    small_font = pygame.font.Font("freesansbold.ttf", 20)
except:
    # En cas d'échec, utilisation de polices système par défaut
    print("Failed to load custom fonts, using fallback")
    title_font = pygame.font.SysFont("Arial", 64, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 32, bold=True)
    menu_font = pygame.font.SysFont("Arial", 40, bold=True)
    hud_font = pygame.font.SysFont("Arial", 28)
    small_font = pygame.font.SysFont("Arial", 20)

# Définition des couleurs utilisées dans le jeu
SKY_BLUE = (135, 206, 250)  # Bleu ciel pour le fond
WHITE = (255, 255, 255)     # Blanc
BLACK = (0, 0, 0)           # Noir
RED = (220, 0, 0)           # Rouge (pour Mario)
DARK_RED = (180, 0, 0)      # Rouge foncé (ombres de Mario)
YELLOW = (255, 215, 0)      # Jaune (pour les pièces)
GOLD = (255, 165, 0)        # Or (pour les pièces)
GREEN = (76, 175, 80)       # Vert (pour les plateformes)
DARK_GREEN = (0, 100, 0)    # Vert foncé (ombres des plateformes)
BROWN = (139, 69, 19)       # Marron (pour les portes)
DARK_BROWN = (100, 50, 0)   # Marron foncé (ombres des portes)
MARIO_BLUE = (30, 144, 255) # Bleu (pour les vêtements de Mario)
DARK_BLUE = (20, 100, 200)  # Bleu foncé
ORANGE = (255, 140, 0)      # Orange (pour les ennemis)
GRAY = (128, 128, 128, 150) # Gris semi-transparent

# États des options sonores
music_enabled = True  # La musique est activée par défaut
sound_enabled = True  # Les sons sont activés par défaut

# Chargement des fichiers son avec gestion d'erreurs
try:
    # Tentative de chargement des sons
    jump_sound = pygame.mixer.Sound("jump.wav")
    coin_sound = pygame.mixer.Sound("coin.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    victory_sound = pygame.mixer.Sound("victory.wav")
    fireball_sound = pygame.mixer.Sound("fireball.wav")
    # Réglage du volume au maximum
    jump_sound.set_volume(1.0)
    coin_sound.set_volume(1.0)
    game_over_sound.set_volume(1.0)
    victory_sound.set_volume(1.0)
    fireball_sound.set_volume(1.0)
    print("Sound files loaded successfully")
except Exception as e:
    # En cas d'échec, création de sons silencieux
    print(f"Failed to load sound files: {e}")
    jump_sound = pygame.mixer.Sound(buffer=bytearray(44))
    coin_sound = pygame.mixer.Sound(buffer=bytearray(44))
    game_over_sound = pygame.mixer.Sound(buffer=bytearray(44))
    victory_sound = pygame.mixer.Sound(buffer=bytearray(44))
    fireball_sound = pygame.mixer.Sound(buffer=bytearray(44))

# Chargement de la musique de fond
if music_enabled:
    try:
        pygame.mixer.music.load("menu_music.wav")
        pygame.mixer.music.set_volume(0.5)  # Volume à 50%
        print("Background music loaded successfully")
    except Exception as e:
        print(f"Failed to load background music: {e}")
        music_enabled = False

# Chargement de l'image de fond du menu
try:
    menu_background = pygame.image.load("menu_background.png").convert_alpha()
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
    print("Menu background image loaded successfully")
except Exception as e:
    print(f"Failed to load menu background image: {e}")
    menu_background = None

# Classe du joueur (Mario)
class Player:
    def __init__(self):  # Correction : _init_ → __init__
        # Propriétés physiques du joueur
        self.width = 40      # Largeur
        self.height = 60     # Hauteur
        self.depth = 15      # Profondeur (pour l'effet 3D)
        self.x = 100         # Position horizontale initiale
        self.y = HEIGHT - 150 # Position verticale initiale
        self.vel_y = 0       # Vitesse verticale
        self.jump_power = -15 # Puissance du saut (négatif car vers le haut)
        self.gravity = 0.8   # Force de gravité
        self.is_jumping = False # État de saut
        self.speed = 5       # Vitesse de déplacement horizontal
        self.facing_right = True # Direction du regard
        self.score = 0       # Score du joueur
        self.coins_collected = 0 # Nombre de pièces collectées
        self.lives = 3       # Nombre de vies
        self.animation_frame = 0 # Frame d'animation courante
        self.animation_speed = 0.3 # Vitesse d'animation
        self.fireballs = []  # Liste des boules de feu lancées
        self.can_throw = True # Possibilité de lancer une boule de feu
        self.throw_cooldown = 20 # Délai entre les lancés

    def draw(self):
        # Dessin de l'ombre du joueur
        shadow = [(self.x + self.depth/2, self.y + self.height),
                  (self.x + self.width - self.depth/2, self.y + self.height),
                  (self.x + self.width + self.depth/2, self.y + self.height - self.depth),
                  (self.x + self.depth/2, self.y + self.height - self.depth)]
        pygame.draw.polygon(screen, (0, 0, 0, 100), shadow)

        # Calcul des décalages d'animation pour les jambes et les bras
        leg_offset = math.sin(self.animation_frame) * 8 if (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]) else 0
        arm_offset = math.cos(self.animation_frame) * 8

        # Corps du joueur
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height), border_radius=5)
        # Côté du corps pour l'effet 3D
        side = [(self.x + self.width, self.y),
                (self.x + self.width + self.depth, self.y - self.depth/2),
                (self.x + self.width + self.depth, self.y + self.height - self.depth/2),
                (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, DARK_RED, side)

        # Chapeau de Mario
        pygame.draw.rect(screen, RED, (self.x - 5, self.y - 5, self.width + 10, 15), border_radius=3)
        hat_side = [(self.x + self.width + 5, self.y - 5),
                    (self.x + self.width + self.depth + 5, self.y - self.depth/2 - 5),
                    (self.x + self.width + self.depth + 5, self.y + 10 - self.depth/2),
                    (self.x + self.width + 5, self.y + 10)]
        pygame.draw.polygon(screen, DARK_RED, hat_side)
        pygame.draw.circle(screen, WHITE, (self.x + (15 if self.facing_right else 25), self.y + 5), 4)

        # Jambes de Mario
        leg1_y = self.y + 40 + (4 if leg_offset > 0 else 0)
        leg2_y = self.y + 40 - (4 if leg_offset < 0 else 0)
        pygame.draw.rect(screen, MARIO_BLUE, (self.x + 5, leg1_y, 12, 20 + abs(leg_offset)), border_radius=3)
        pygame.draw.rect(screen, MARIO_BLUE, (self.x + 23, leg2_y, 12, 20 - abs(leg_offset)), border_radius=3)

        # Bras de Mario
        arm_y = self.y + 20 + (4 if arm_offset > 0 else 0)
        arm_x = self.x - 5 if self.facing_right else self.x + 40
        pygame.draw.rect(screen, RED, (arm_x, arm_y, 10, 20 + abs(arm_offset)), border_radius=3)
        pygame.draw.rect(screen, WHITE, (arm_x + (2 if self.facing_right else 0), arm_y + 15, 6, 6), border_radius=3)

        # Visage de Mario
        eye_x = self.x + (25 if self.facing_right else 15)
        pygame.draw.circle(screen, WHITE, (eye_x, self.y + 15), 6)
        pygame.draw.circle(screen, BLACK, (eye_x, self.y + 15), 3)

    def update(self, platforms, coins, doors, enemies, current_level):
        # Mise à jour de la position et de l'état du joueur
        keys = pygame.key.get_pressed()
        # Animation lors du déplacement
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.animation_frame += self.animation_speed

        # Application de la gravité
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Gestion du sol
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.is_jumping = False

        # Collision avec les plateformes
        for platform in platforms:
            if (self.y + self.height >= platform.y and
                self.y + self.height <= platform.y + 20 and
                self.x + self.width > platform.x and
                self.x < platform.x + platform.width and
                self.vel_y >= 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.is_jumping = False

        # Collecte des pièces
        for coin in coins[:]:
            if (self.x + self.width > coin.x and
                self.x < coin.x + coin.size and
                self.y + self.height > coin.y and
                self.y < coin.y + coin.size):
                coins.remove(coin)
                self.score += 100
                self.coins_collected += 1
                if sound_enabled:
                    print("Playing coin sound")  # Debug
                    coin_sound.play()

        # Collision avec les ennemis
        for enemy in enemies[:]:
            if (self.x + self.width > enemy.x and
                self.x < enemy.x + enemy.width and
                self.y + self.height > enemy.y and
                self.y < enemy.y + enemy.height):
                # Si Mario saute sur un ennemi
                if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height/2:
                    enemies.remove(enemy)
                    self.vel_y = self.jump_power/2
                    self.score += 200
                else:
                    # Si Mario est touché par un ennemi
                    self.lives -= 1
                    self.x = 100
                    self.y = HEIGHT - 150
                    self.vel_y = 0
                    if self.lives <= 0:
                        if sound_enabled:
                            print("Playing game over sound")  # Debug
                            game_over_sound.play()
                        return "game_over"

        # Chute hors de l'écran
        if self.y > HEIGHT:
            self.lives -= 1
            self.x = 100
            self.y = HEIGHT - 150
            self.vel_y = 0
            if self.lives <= 0:
                if sound_enabled:
                    print("Playing game over sound")  # Debug
                    game_over_sound.play()
                return "game_over"

        # Interaction avec les portes
        for door in doors:
            if (self.x + self.width > door.x and
                self.x < door.x + door.width and
                self.y + self.height > door.y and
                self.y < door.y + door.height and
                self.coins_collected >= door.coins_required):
                if sound_enabled:
                    print("Playing victory sound")  # Debug
                    victory_sound.play()
                return door.next_level

        # Mise à jour des boules de feu
        for fireball in self.fireballs[:]:
            fireball['x'] += fireball['speed']
            # Suppression des boules de feu sorties de l'écran
            if fireball['x'] > WIDTH or fireball['x'] < 0:
                self.fireballs.remove(fireball)
            # Collision des boules de feu avec les ennemis
            for enemy in enemies[:]:
                if (fireball['x'] + 10 > enemy.x and
                    fireball['x'] < enemy.x + enemy.width and
                    fireball['y'] + 10 > enemy.y and
                    fireball['y'] < enemy.y + enemy.height):
                    enemies.remove(enemy)
                    self.fireballs.remove(fireball)
                    self.score += 300
                    break

        # Gestion du délai entre les lancés de boules de feu
        if not self.can_throw:
            self.throw_cooldown -= 1
            if self.throw_cooldown <= 0:
                self.can_throw = True
                self.throw_cooldown = 20

        return current_level

    def jump(self):
        # Gestion du saut
        if not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True
            if sound_enabled:
                print("Playing jump sound")  # Debug
                jump_sound.play()

    def throw_fireball(self):
        # Lancement d'une boule de feu
        if self.can_throw:
            self.fireballs.append({
                'x': self.x + self.width if self.facing_right else self.x - 10,
                'y': self.y + self.height//2 - 5,
                'speed': 10 if self.facing_right else -10
            })
            self.can_throw = False
            if sound_enabled:
                print("Playing fireball sound")  # Debug
                fireball_sound.play()

# Classe des plateformes
class Platform:
    def __init__(self, x, y, width, is_breakable=False):  # Correction : _init_ → __init__
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.depth = 15
        self.is_breakable = is_breakable
        self.color = GREEN if not is_breakable else BROWN
        self.dark_color = DARK_GREEN if not is_breakable else DARK_BROWN

    def draw(self):
        # Dessin de la plateforme avec effet 3D
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=5)
        front = [(self.x, self.y + self.height),
                 (self.x + self.depth, self.y + self.height - self.depth),
                 (self.x + self.width + self.depth, self.y + self.height - self.depth),
                 (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, self.dark_color, front)
        side = [(self.x + self.width, self.y),
                (self.x + self.width + self.depth, self.y - self.depth),
                (self.x + self.width + self.depth, self.y + self.height - self.depth),
                (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, self.dark_color, side)
        # Détails sur la plateforme
        for i in range(0, self.width, 10):
            pygame.draw.line(screen, self.dark_color, (self.x + i, self.y), (self.x + i, self.y + self.height), 2)
        for i in range(0, self.height, 10):
            pygame.draw.line(screen, self.dark_color, (self.x, self.y + i), (self.x + self.width, self.y + i), 2)

# Classe des pièces
class Coin:
    def __init__(self, x, y):  # Correction : _init_ → __init__
        self.x = x
        self.y = y
        self.size = 20
        self.animation_frame = 0
        self.animation_speed = 0.15

    def draw(self):
        # Animation de la pièce (effet de brillance)
        self.animation_frame += self.animation_speed
        scale = 0.8 + 0.2 * math.sin(self.animation_frame)
        radius = int(self.size * scale / 2)
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size/2), int(self.y + self.size/2)), radius)
        pygame.draw.circle(screen, GOLD, (int(self.x + self.size/2 + 2), int(self.y + self.size/2 - 2)), radius - 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size/2), int(self.y + self.size/2)), radius, 1)
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size/2 + 3), int(self.y + self.size/2 - 3)), 4)

# Classe des portes
class Door:
    def __init__(self, x, y, next_level, coins_required):  # Correction : _init_ → __init__
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.depth = 15
        self.next_level = next_level
        self.coins_required = coins_required
        self.animation_frame = 0

    def draw(self):
        # Animation de la porte (effet de brillance)
        self.animation_frame += 0.05
        glow = math.sin(self.animation_frame) * 10
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height), border_radius=5)
        side = [(self.x + self.width, self.y),
                (self.x + self.width + self.depth, self.y - self.depth),
                (self.x + self.width + self.depth, self.y + self.height - self.depth),
                (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, DARK_BROWN, side)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, border_radius=5)
        pygame.draw.circle(screen, YELLOW, (self.x + 30, self.y + self.height//2), 6)
        text_color = WHITE if glow < 0 else (min(255, 255 + glow), min(255, 215 + glow), 0)
        text = hud_font.render(str(self.coins_required), True, text_color)
        screen.blit(text, (self.x + self.width//2 - text.get_width()//2, self.y + self.height//2 - text.get_height()//2))

# Classe des ennemis
class Enemy:
    def __init__(self, x, y, min_x, max_x, level):  # Correction : _init_ → __init__
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.depth = 10
        self.speed = 1 + level * 0.5  # La vitesse augmente avec le niveau
        self.min_x = min_x
        self.max_x = max_x
        self.direction = 1
        self.animation_frame = 0
        self.type = random.choice(["goomba", "koopa"])  # Type d'ennemi aléatoire

    def draw(self):
        # Dessin de l'ennemi avec animation
        color = ORANGE if self.type == "goomba" else GREEN
        dark_color = (200, 100, 0) if self.type == "goomba" else DARK_GREEN
        self.animation_frame += 0.1
        wobble = math.sin(self.animation_frame) * 2
        pygame.draw.rect(screen, color, (self.x, self.y + wobble, self.width, self.height - wobble), border_radius=5)
        side = [(self.x + self.width, self.y + wobble),
                (self.x + self.width + self.depth, self.y + wobble - self.depth),
                (self.x + self.width + self.depth, self.y + self.height - wobble - self.depth),
                (self.x + self.width, self.y + self.height - wobble)]
        pygame.draw.polygon(screen, dark_color, side)
        eye_offset = math.cos(self.animation_frame) * 2
        eye_x1 = self.x + 8
        eye_x2 = self.x + 22
        pygame.draw.circle(screen, WHITE, (eye_x1, self.y + 10 + wobble + eye_offset), 4)
        pygame.draw.circle(screen, WHITE, (eye_x2, self.y + 10 + wobble - eye_offset), 4)
        pygame.draw.circle(screen, BLACK, (eye_x1, self.y + 10 + wobble + eye_offset), 2)
        pygame.draw.circle(screen, BLACK, (eye_x2, self.y + 10 + wobble - eye_offset), 2)

    def update(self):
        # Déplacement de l'ennemi (va-et-vient)
        self.x += self.speed * self.direction
        if self.x <= self.min_x:
            self.direction = 1
        elif self.x + self.width >= self.max_x:
            self.direction = -1

# Chargement des niveaux
def load_level(level_num):
    platforms = []  # Liste des plateformes
    coins = []      # Liste des pièces
    doors = []      # Liste des portes
    enemies = []    # Liste des ennemis

    # Configuration du niveau 1
    if level_num == 1:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),  # Sol principal
            Platform(200, 450, 200),          # Plateforme
            Platform(500, 350, 150),          # Plateforme
            Platform(300, 250, 100),          # Plateforme
            Platform(600, 200, 200),          # Plateforme
            Platform(100, 350, 80, True)      # Plateforme cassable
        ]
        coins = [
            Coin(250, 410),  # Pièce
            Coin(550, 310),  # Pièce
            Coin(330, 210),  # Pièce
            Coin(650, 160),  # Pièce
            Coin(130, 310)   # Pièce
        ]
        doors = [Door(700, 140, 2, 3)]  # Porte vers le niveau 2, nécessite 3 pièces
        enemies = [
            Enemy(400, 430, 200, 400, level_num),  # Ennemi
            Enemy(650, 330, 500, 650, level_num)   # Ennemi
        ]
    # Configuration du niveau 2
    elif level_num == 2:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),
            Platform(100, 450, 100),
            Platform(300, 400, 100),
            Platform(500, 350, 100),
            Platform(200, 300, 100),
            Platform(400, 250, 100),
            Platform(600, 200, 100),
            Platform(300, 150, 100),
            Platform(500, 100, 80, True)
        ]
        coins = [
            Coin(130, 410),
            Coin(330, 360),
            Coin(530, 310),
            Coin(230, 260),
            Coin(430, 210),
            Coin(630, 160),
            Coin(330, 110),
            Coin(530, 60)
        ]
        doors = [Door(700, 90, 3, 5)]  # Porte vers le niveau 3, nécessite 5 pièces
        enemies = [
            Enemy(150, 430, 100, 200, level_num),
            Enemy(350, 380, 300, 400, level_num),
            Enemy(550, 330, 500, 600, level_num),
            Enemy(250, 280, 200, 300, level_num),
            Enemy(650, 180, 600, 700, level_num)
        ]
    # Configuration du niveau 3
    elif level_num == 3:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),
            Platform(100, 450, 80),
            Platform(250, 400, 80),
            Platform(400, 350, 80),
            Platform(550, 300, 80),
            Platform(700, 250, 80),
            Platform(550, 200, 80),
            Platform(400, 150, 80),
            Platform(250, 100, 80),
            Platform(100, 50, 80),
            Platform(400, 400, 80, True),
            Platform(550, 250, 80, True)
        ]
        coins = [
            Coin(130, 410),
            Coin(280, 360),
            Coin(430, 310),
            Coin(580, 260),
            Coin(730, 210),
            Coin(580, 160),
            Coin(430, 110),
            Coin(280, 60),
            Coin(130, 10),
            Coin(430, 360),
            Coin(580, 210)
        ]
        doors = [Door(700, 10, 4, 7)]  # Porte vers le niveau 4, nécessite 7 pièces
        enemies = [
            Enemy(150, 430, 100, 180, level_num),
            Enemy(300, 380, 250, 330, level_num),
            Enemy(450, 330, 400, 480, level_num),
            Enemy(600, 280, 550, 630, level_num),
            Enemy(600, 180, 550, 630, level_num),
            Enemy(450, 130, 400, 480, level_num),
            Enemy(300, 80, 250, 330, level_num)
        ]
    # Configuration du niveau 4 (niveau final)
    elif level_num == 4:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),
            Platform(300, 400, 200),
            Platform(350, 300, 100),
            Platform(400, 200, 200)
        ]
        coins = []  # Pas de pièces dans le niveau final
        doors = [Door(450, 140, 1, 0)]  # Porte de retour au niveau 1 (victoire)
        enemies = []  # Pas d'ennemis dans le niveau final

    return platforms, coins, doors, enemies

# Écran de menu
def show_menu(high_score):
    global music_enabled, sound_enabled
    menu_active = True
    selected_option = 0  # Option sélectionnée par défaut
    options = [
        "Jouer",
        f"{'Désactiver' if music_enabled else 'Activer'} Musique",
        f"{'Désactiver' if sound_enabled else 'Activer'} Son",
        "Quitter"
    ]
    title_animation = 0  # Animation du titre
    mario_x = -100       # Position horizontale de Mario dans le menu
    mario_y = HEIGHT - 200 # Position verticale de Mario dans le menu
    mario_vel_y = -5     # Vitesse verticale de Mario dans le menu
    # Génération de nuages pour le fond
    clouds = [(random.randint(0, WIDTH), random.randint(50, 150), random.randint(1, 3)) for _ in range(8)]

    # Démarrage de la musique si elle est activée
    if music_enabled and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)  # Joue en boucle

    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        pygame.mixer.music.stop()  # Arrête la musique quand le jeu commence
                        return
                    elif selected_option == 1:
                        music_enabled = not music_enabled
                        options[1] = f"{'Désactiver' if music_enabled else 'Activer'} Musique"
                        if music_enabled and not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
                        else:
                            pygame.mixer.music.stop()
                    elif selected_option == 2:
                        sound_enabled = not sound_enabled
                        options[2] = f"{'Désactiver' if sound_enabled else 'Activer'} Son"
                    elif selected_option == 3:
                        pygame.mixer.music.stop()
                        pygame.quit()
                        sys.exit()

        # Animation de Mario dans le menu
        mario_x += 3
        mario_y += mario_vel_y
        mario_vel_y += 0.2
        if mario_y > HEIGHT - 200:
            mario_y = HEIGHT - 200
            mario_vel_y = -5
        if mario_x > WIDTH + 100:
            mario_x = -100

        # Dessin du fond
        screen.fill(SKY_BLUE)
        # Collines en arrière-plan avec effet de parallaxe
        for layer in range(3):
            offset = pygame.time.get_ticks() / (300 * (layer + 1)) % WIDTH
            for i in range(3):
                x = (i * 400 - offset) % (WIDTH + 400) - 200
                y = HEIGHT - 100 + layer * 50
                size = 100 + layer * 50
                pygame.draw.ellipse(screen, (0, 150 - layer * 30, 0), (x, y, size, size // 2))

        # Dessin des nuages
        for cloud in clouds:
            x, y, layer = cloud
            offset = pygame.time.get_ticks() / (100 * layer) % (WIDTH + 200)
            cloud_x = (x - offset) % (WIDTH + 200) - 100
            size = 30 + layer * 10
            pygame.draw.circle(screen, WHITE, (cloud_x, y), size)
            pygame.draw.circle(screen, WHITE, (cloud_x + size//2, y - size//3), size//1.5)
            pygame.draw.circle(screen, WHITE, (cloud_x + size, y), size)

        # Image de fond semi-transparente
        if menu_background:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.blit(menu_background, (0, 0))
            overlay.set_alpha(128)  # 50% d'opacité
            screen.blit(overlay, (0, 0))

        # Titre avec animation
        title_y = 100 + math.sin(title_animation) * 10
        title_animation += 0.05
        title_shadow = title_font.render("SUPER MARIO", True, BLACK)
        title_text = title_font.render("SUPER MARIO", True, RED)
        subtitle_shadow = subtitle_font.render("EN ACTION", True, BLACK)
        subtitle_text = subtitle_font.render("EN ACTION", True, YELLOW)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, title_y + 3))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, title_y))
        screen.blit(subtitle_shadow, (WIDTH//2 - subtitle_shadow.get_width()//2 + 3, title_y + 80 + 3))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, title_y + 80))

        # Meilleur score
        high_score_text = hud_font.render(f"Meilleur Score: {high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, title_y + 140))

        # Dessin de Mario dans le menu
        pygame.draw.rect(screen, RED, (mario_x, mario_y, 40, 60), border_radius=5)
        pygame.draw.rect(screen, MARIO_BLUE, (mario_x + 5, mario_y + 40, 12, 20), border_radius=3)
        pygame.draw.rect(screen, MARIO_BLUE, (mario_x + 23, mario_y + 40, 12, 20), border_radius=3)
        pygame.draw.rect(screen, RED, (mario_x - 5, mario_y - 5, 50, 15), border_radius=3)

        # Options du menu
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            option_shadow = menu_font.render(option, True, BLACK)
            option_text = menu_font.render(option, True, color)
            y_pos = HEIGHT - 200 + i * 50  # Position verticale des options
            screen.blit(option_shadow, (WIDTH//2 - option_shadow.get_width()//2 + 2, y_pos + 2))
            screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, y_pos))

        # Instructions
        instructions = small_font.render("Flèches: Naviguer - Entrée: Sélectionner", True, WHITE)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

# Initialisation du jeu
player = Player()  # Création du joueur
current_level = 1  # Niveau initial
platforms, coins, doors, enemies = load_level(current_level)  # Chargement du niveau 1
game_state = "menu"  # État initial du jeu
clock = pygame.time.Clock()  # Horloge pour contrôler le FPS
high_score = 0  # Meilleur score initial

# Création des étoiles de fond
background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT//2)
    size = random.randint(2, 5)
    pygame.draw.circle(background, (255, 255, 255, 150), (x, y), size)

# Boucle principale du jeu
show_menu(high_score)  # Affichage du menu initial
game_state = "playing"  # Passage en mode jeu

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.jump()  # Sauter avec espace
            if event.key == pygame.K_f and game_state == "playing":
                player.throw_fireball()  # Lancer une boule de feu avec F
            if event.key == pygame.K_t and game_state == "playing":  # Test son avec T
                if sound_enabled:
                    print("Testing jump sound")
                    jump_sound.play()
            if event.key == pygame.K_r and game_state == "playing":
                # Réinitialisation du jeu avec R
                player = Player()
                current_level = 1
                platforms, coins, doors, enemies = load_level(current_level)
            if event.key == pygame.K_RETURN and (game_state == "game_over" or game_state == "victory"):
                # Redémarrage après game over ou victoire
                high_score = max(high_score, player.score)
                player = Player()
                current_level = 1
                platforms, coins, doors, enemies = load_level(current_level)
                game_state = "playing"
            if event.key == pygame.K_ESCAPE:
                # Retour au menu avec Échap
                game_state = "menu"
                show_menu(high_score)
                game_state = "playing"

    # Gestion de la musique en jeu
    if game_state == "playing" and music_enabled and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)  # Redémarre la musique si elle s'est arrêtée

    # Logique du jeu
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed  # Déplacement vers la gauche
            player.facing_right = False
        if keys[pygame.K_RIGHT]:
            player.x += player.speed  # Déplacement vers la droite
            player.facing_right = True

        # Mise à jour des ennemis
        for enemy in enemies:
            enemy.update()

        # Mise à jour du joueur et vérification des collisions
        result = player.update(platforms, coins, doors, enemies, current_level)
        if result == "game_over":
            game_state = "game_over"  # Passage en état game over
        elif result != current_level:
            if result == 4 and current_level == 3:
                game_state = "victory"  # Victoire après le niveau 3
            else:
                # Passage au niveau suivant
                current_level = result
                platforms, coins, doors, enemies = load_level(current_level)
                player.x = 100
                player.y = HEIGHT - 150
                player.vel_y = 0
                player.is_jumping = False

    # Dessin de l'écran
    screen.fill(SKY_BLUE)  # Fond bleu ciel
    screen.blit(background, (0, 0))  # Étoiles de fond

    # Dessin des nuages
    for cloud in [(100, 100, 1), (400, 150, 2), (700, 80, 1), (200, 50, 3), (600, 120, 2)]:
        x, y, layer = cloud
        offset = pygame.time.get_ticks() / (100 * layer) % (WIDTH + 200)
        cloud_x = (x - offset) % (WIDTH + 200) - 100
        size = 30 + layer * 10
        pygame.draw.circle(screen, WHITE, (cloud_x, y), size)
        pygame.draw.circle(screen, WHITE, (cloud_x + size//2, y - size//3), size//1.5)
        pygame.draw.circle(screen, WHITE, (cloud_x + size, y), size)

    # Dessin des éléments du jeu
    for platform in platforms:
        platform.draw()
    for coin in coins:
        coin.draw()
    for door in doors:
        door.draw()
    for enemy in enemies:
        enemy.draw()
    for fireball in player.fireballs:
        pygame.draw.circle(screen, ORANGE, (int(fireball['x']), int(fireball['y'])), 8)
        pygame.draw.circle(screen, YELLOW, (int(fireball['x'] + 2), int(fireball['y'] - 2)), 5)
    player.draw()  # Dessin du joueur

    # HUD (Head-Up Display)
    pygame.draw.rect(screen, GRAY, (10, 10, 200, 120), border_radius=10)
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 120), 2, border_radius=10)
    score_text = hud_font.render(f"Score: {player.score}", True, WHITE)
    level_text = hud_font.render(f"Niveau: {current_level}", True, WHITE)
    coins_text = hud_font.render(f"Pièces: {player.coins_collected}", True, WHITE)
    lives_text = hud_font.render(f"Vies: {player.lives}", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (20, 50))
    screen.blit(coins_text, (20, 80))
    screen.blit(lives_text, (20, 110))
    instructions = small_font.render("Flèches: Bouger - Espace: Sauter - F: Tirer - T: Tester Son - R: Réinitialiser - Échap: Menu", True, WHITE)
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 30))

    # Écran de game over
    if game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        game_over_shadow = title_font.render("GAME OVER", True, BLACK)
        game_over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over_shadow, (WIDTH//2 - game_over_shadow.get_width()//2 + 3, HEIGHT//2 - 50 + 3))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        restart_text = hud_font.render("Appuyez sur ENTRÉE pour recommencer", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    # Écran de victoire
    if game_state == "victory":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        victory_shadow = title_font.render("VICTOIRE!", True, BLACK)
        victory_text = title_font.render("VICTOIRE!", True, YELLOW)
        screen.blit(victory_shadow, (WIDTH//2 - victory_shadow.get_width()//2 + 3, HEIGHT//2 - 80 + 3))
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 80))
        score_text = hud_font.render(f"Score Final: {player.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
        restart_text = hud_font.render("Appuyez sur ENTRÉE pour recommencer", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()  # Mise à jour de l'affichage
    clock.tick(60)  # Limite à 60 FPS

pygame.quit()
sys.exit()
