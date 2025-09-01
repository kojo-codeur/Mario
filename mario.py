import pygame
import sys
import random
import math

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()  # Initialisation du module audio

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario en action")

big_font = pygame.font.SysFont(None, 72)

# Chargement des polices personnalisées
try:
    title_font = pygame.font.Font("freesansbold.ttf", 60)
    subtitle_font = pygame.font.Font("freesansbold.ttf", 30)
    menu_font = pygame.font.Font("freesansbold.ttf", 36)
    game_font = pygame.font.Font("freesansbold.ttf", 24)
    small_font = pygame.font.Font("freesansbold.ttf", 18)
except:
    # Fallback aux polices système si les polices personnalisées ne sont pas disponibles
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 30, bold=True)
    menu_font = pygame.font.SysFont("Arial", 36, bold=True)
    game_font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

# Couleurs
SKY_BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
GREEN = (76, 175, 80)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 120, 255)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (135, 206, 250)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
MARIO_RED = (220, 0, 0)
MARIO_BLUE = (30, 144, 255)

# Effets sonores (placeholders - vous pouvez ajouter vos propres fichiers sonores)
try:
    jump_sound = pygame.mixer.Sound("jump.wav")
    coin_sound = pygame.mixer.Sound("coin.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    victory_sound = pygame.mixer.Sound("victory.wav")
except:
    # Création de sons de secours si les fichiers ne sont pas disponibles
    jump_sound = pygame.mixer.Sound(buffer=bytearray([0]*44))
    coin_sound = pygame.mixer.Sound(buffer=bytearray([0]*44))
    game_over_sound = pygame.mixer.Sound(buffer=bytearray([0]*44))
    victory_sound = pygame.mixer.Sound(buffer=bytearray([0]*44))

# Joueur avec effet 3D
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.depth = 20
        self.x = 100
        self.y = HEIGHT - 150
        self.z = 0
        self.vel_y = 0
        self.vel_z = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.speed = 5
        self.facing_right = True
        self.score = 0
        self.coins_collected = 0
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.has_hat = True

    def draw(self):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
        
        # Dessiner l'ombre en 3D
        shadow_points = [
            (self.x + self.depth/2, self.y + self.height),
            (self.x + self.width - self.depth/2, self.y + self.height),
            (self.x + self.width + self.depth/2, self.y + self.height - self.depth),
            (self.x + self.depth/2, self.y + self.height - self.depth)
        ]
        pygame.draw.polygon(screen, (0, 0, 0, 128), shadow_points)
        
        # Corps principal avec effet 3D
        pygame.draw.rect(screen, MARIO_RED, (self.x, self.y, self.width, self.height))
        
        # Côté droit pour l'effet 3D
        right_side = [
            (self.x + self.width, self.y),
            (self.x + self.width + self.depth/2, self.y - self.depth/2),
            (self.x + self.width + self.depth/2, self.y + self.height - self.depth/2),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, (180, 0, 0), right_side)
        
        # Dessiner la casquette si le joueur en a une
        if self.has_hat:
            pygame.draw.rect(screen, MARIO_RED, (self.x - 5, self.y, self.width + 10, 15))
            cap_side = [
                (self.x + self.width + 5, self.y),
                (self.x + self.width + self.depth/2 + 5, self.y - self.depth/2),
                (self.x + self.width + self.depth/2 + 5, self.y + 15 - self.depth/2),
                (self.x + self.width + 5, self.y + 15)
            ]
            pygame.draw.polygon(screen, (180, 0, 0), cap_side)
        
        # Animation des jambes
        leg_offset = math.sin(self.animation_frame) * 5 if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT] else 0
        
        # Dessiner les jambes
        pygame.draw.rect(screen, MARIO_BLUE, (self.x + 5, self.y + 40, 10, 20 + leg_offset))
        pygame.draw.rect(screen, MARIO_BLUE, (self.x + 25, self.y + 40, 10, 20 - leg_offset))
        
        # Dessiner les yeux
        eye_x = self.x + 25 if self.facing_right else self.x + 5
        pygame.draw.circle(screen, WHITE, (eye_x, self.y + 20), 5)
        pygame.draw.circle(screen, BLACK, (eye_x, self.y + 20), 2)

    def update(self, platforms, coins, doors, enemies, current_level):
        # Mettre à jour l'animation
        if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.animation_frame += self.animation_speed
        
        # Appliquer la gravité
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Gérer l'invincibilité temporaire
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Collision avec le sol
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
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.is_jumping = False

        # Collecter les pièces
        for coin in coins[:]:
            if (self.x + self.width > coin.x and
                self.x < coin.x + coin.size and
                self.y + self.height > coin.y and
                self.y < coin.y + coin.size):
                coins.remove(coin)
                self.score += 100
                self.coins_collected += 1
                try:
                    coin_sound.play()
                except:
                    pass

        # Collision avec les ennemis
        for enemy in enemies[:]:
            if (self.x + self.width > enemy.x and
                self.x < enemy.x + enemy.width and
                self.y + self.height > enemy.y and
                self.y < enemy.y + enemy.height):
                if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height/2:
                    enemies.remove(enemy)
                    self.vel_y = self.jump_power/2
                    self.score += 200
                elif not self.invincible:
                    self.lives -= 1
                    self.invincible = True
                    self.invincible_timer = 60
                    if self.lives <= 0:
                        try:
                            game_over_sound.play()
                        except:
                            pass
                        return "game_over"
        
        # Vérifier si le joueur tombe hors de l'écran
        if self.y > HEIGHT:
            self.lives -= 1
            self.x = 100
            self.y = HEIGHT - 150
            self.vel_y = 0
            if self.lives <= 0:
                try:
                    game_over_sound.play()
                except:
                    pass
                return "game_over"
            self.invincible = True
            self.invincible_timer = 120

        # Vérifier si le joueur atteint la porte pour changer de niveau
        for door in doors:
            if (self.x + self.width > door.x and
                self.x < door.x + door.width and
                self.y + self.height > door.y and
                self.y < door.y + door.height):
                if self.coins_collected >= door.coins_required:
                    try:
                        victory_sound.play()
                    except:
                        pass
                    return door.next_level
        
        return current_level

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True
            try:
                jump_sound.play()
            except:
                pass

# Plateforme avec effet 3D
class Platform:
    def __init__(self, x, y, width, is_breakable=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.depth = 10
        self.is_breakable = is_breakable
        self.color = GREEN if not is_breakable else BROWN

    def draw(self):
        # Dessiner le dessus de la plateforme
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Dessiner l'avant de la plateforme (effet 3D)
        front_face = [
            (self.x, self.y + self.height),
            (self.x + self.depth, self.y + self.height - self.depth/2),
            (self.x + self.width + self.depth, self.y + self.height - self.depth/2),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, DARK_GREEN if not self.is_breakable else (100, 50, 0), front_face)
        
        # Dessiner le côté droit (effet 3D)
        right_side = [
            (self.x + self.width, self.y),
            (self.x + self.width + self.depth, self.y - self.depth/2),
            (self.x + self.width + self.depth, self.y + self.height - self.depth/2),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, DARK_GREEN if not self.is_breakable else (100, 50, 0), right_side)
        
        # Ajouter des détails aux briques
        if not self.is_breakable:
            for i in range(0, self.width, 15):
                pygame.draw.line(screen, BROWN, (self.x + i, self.y), (self.x + i, self.y + self.height), 1)
            for i in range(0, self.height, 15):
                pygame.draw.line(screen, BROWN, (self.x, self.y + i), (self.x + self.width, self.y + i), 1)
        else:
            # Détails pour les briques cassables
            for i in range(0, self.width, 10):
                pygame.draw.line(screen, (100, 50, 0), (self.x + i, self.y), (self.x + i, self.y + self.height), 1)
            for i in range(0, self.height, 10):
                pygame.draw.line(screen, (100, 50, 0), (self.x, self.y + i), (self.x + self.width, self.y + i), 1)

# Pièce avec effet 3D et animation
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 15
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.collected = False

    def draw(self):
        if self.collected:
            return
            
        self.animation_frame += self.animation_speed
        bounce = math.sin(self.animation_frame) * 5
        
        # Dessiner l'effet 3D de la pièce
        pygame.draw.circle(screen, YELLOW, (self.x + self.size//2, self.y + self.size//2 - bounce), self.size//2)
        pygame.draw.circle(screen, GOLD, (self.x + self.size//2 + 2, self.y + self.size//2 - bounce - 2), self.size//2 - 2)
        pygame.draw.circle(screen, BLACK, (self.x + self.size//2, self.y + self.size//2 - bounce), self.size//2, 1)
        
        # Dessiner le reflet
        pygame.draw.circle(screen, (255, 255, 200), (self.x + self.size//2 + 3, self.y + self.size//2 - bounce - 3), 3)

# Porte avec effet 3D
class Door:
    def __init__(self, x, y, next_level, coins_required):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.depth = 10
        self.next_level = next_level
        self.coins_required = coins_required
        self.animation_frame = 0

    def draw(self):
        self.animation_frame += 0.05
        glow = math.sin(self.animation_frame) * 5
        
        # Dessiner la face avant
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (50, 25, 0), (self.x, self.y, self.width, self.height), 2)
        
        # Dessiner le côté (effet 3D)
        side_points = [
            (self.x + self.width, self.y),
            (self.x + self.width + self.depth, self.y - self.depth/2),
            (self.x + self.width + self.depth, self.y + self.height - self.depth/2),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, (100, 50, 0), side_points)
        
        # Poignée de porte
        pygame.draw.circle(screen, YELLOW, (self.x + 30, self.y + self.height//2), 5)
        
        # Afficher le nombre de pièces requises avec effet de lueur
        text_color = (255, 255, 255) if glow < 0 else (255, 255, 0)
        text = game_font.render(str(self.coins_required), True, text_color)
        screen.blit(text, (self.x + self.width//2 - text.get_width()//2, self.y + self.height//2 - text.get_height()//2))

# Ennemi avec effet 3D
class Enemy:
    def __init__(self, x, y, min_x, max_x, level):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.depth = 10
        self.speed = 0 + (level * 0.5)
        self.min_x = min_x
        self.max_x = max_x
        self.direction = 1
        self.animation_frame = 0
        self.type = random.choice(["goomba", "koopa"])

    def draw(self):
        # Dessiner le corps principal
        color = ORANGE if self.type == "goomba" else (0, 150, 0)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Dessiner le côté (effet 3D)
        side_points = [
            (self.x + self.width, self.y),
            (self.x + self.width + self.depth, self.y - self.depth/2),
            (self.x + self.width + self.depth, self.y + self.height - self.depth/2),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, (200, 100, 0) if self.type == "goomba" else (0, 100, 0), side_points)
        
        # Dessiner les yeux avec animation
        self.animation_frame += 0.05
        eye_offset = math.sin(self.animation_frame) * 2
        
        if self.type == "goomba":
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 10 + eye_offset), 5)
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 10 - eye_offset), 5)
            pygame.draw.circle(screen, BLACK, (self.x + 8, self.y + 10 + eye_offset), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 22, self.y + 10 - eye_offset), 2)
        else:
            # Koopa Troopa avec carapace
            pygame.draw.ellipse(screen, (0, 100, 0), (self.x + 5, self.y + 5, 20, 20))
            pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 12 + eye_offset), 3)
            pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 12 - eye_offset), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 12 + eye_offset), 1)
            pygame.draw.circle(screen, BLACK, (self.x + 20, self.y + 12 - eye_offset), 1)

    def update(self):
        self.x += self.speed * self.direction
        
        if self.x <= self.min_x:
            self.direction = 1
        elif self.x + self.width >= self.max_x:
            self.direction = -1

# Définition des niveaux
def load_level(level_num):
    platforms = []
    coins = []
    doors = []
    enemies = []
    
    if level_num == 1:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),
            Platform(200, 450, 200),
            Platform(500, 350, 150),
            Platform(300, 250, 100),
            Platform(600, 200, 200),
            Platform(100, 350, 80, True)  # Plateforme cassable
        ]
        coins = [
            Coin(250, 410),
            Coin(550, 310),
            Coin(330, 210),
            Coin(650, 160),
            Coin(130, 310)
        ]
        doors = [
            Door(700, 140, 2, 3)
        ]
        enemies = [
            Enemy(400, 430, 200, 400, level_num),
            Enemy(650, 330, 500, 650, level_num)
        ]
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
        doors = [
            Door(700, 90, 3, 5)
        ]
        enemies = [
            Enemy(150, 430, 100, 200, level_num),
            Enemy(350, 380, 300, 400, level_num),
            Enemy(550, 330, 500, 600, level_num),
            Enemy(250, 280, 200, 300, level_num),
            Enemy(650, 180, 600, 700, level_num)
        ]
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
        doors = [
            Door(700, 10, 4, 7)
        ]
        enemies = [
            Enemy(150, 430, 100, 180, level_num),
            Enemy(300, 380, 250, 330, level_num),
            Enemy(450, 330, 400, 480, level_num),
            Enemy(600, 280, 550, 630, level_num),
            Enemy(600, 180, 550, 630, level_num),
            Enemy(450, 130, 400, 480, level_num),
            Enemy(300, 80, 250, 330, level_num)
        ]
    elif level_num == 4:
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),
            Platform(300, 400, 200),
            Platform(350, 300, 100),
            Platform(400, 200, 200)
        ]
        coins = []
        doors = [
            Door(450, 140, 1, 0)
        ]
        enemies = []
    
    return platforms, coins, doors, enemies

# Écran d'accueil
def show_menu():
    menu_active = True
    selected_option = 0
    options = ["Jouer", "Quitter"]
    
    # Animation de l'écran titre
    title_animation = 0
    mario_x = -100
    
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
                        return  # Commencer le jeu
                    else:
                        pygame.quit()
                        sys.exit()
        
        # Mise à jour de l'animation
        title_animation += 0.05
        mario_x += 2
        if mario_x > WIDTH + 100:
            mario_x = -100
        
        # Dessin de l'écran d'accueil
        screen.fill(SKY_BLUE)
        
        # Dessiner des nuages décoratifs
        for i in range(5):
            x = (pygame.time.get_ticks() // 30 + i * 200) % (WIDTH + 200) - 100
            y = 100 + i * 40
            size = 30 + i * 5
            pygame.draw.circle(screen, WHITE, (x, y), size)
            pygame.draw.circle(screen, WHITE, (x + size//2, y - size//3), size//1.5)
            pygame.draw.circle(screen, WHITE, (x + size, y), size)
        
        # Dessiner le titre avec effet d'ombre
        title_y = 100 + math.sin(title_animation) * 10
        title_shadow = title_font.render("SUPER", True, (0, 0, 0))
        title_text = title_font.render("SUPER", True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, title_y + 3))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, title_y))
        
        title_shadow = title_font.render("MARIO", True, (0, 0, 0))
        title_text = title_font.render("MARIO", True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, title_y + 70 + 3))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, title_y + 70))
        
        subtitle_shadow = subtitle_font.render("EN ACTION", True, (0, 0, 0))
        subtitle_text = subtitle_font.render("EN ACTION", True, (255, 215, 0))
        screen.blit(subtitle_shadow, (WIDTH//2 - subtitle_shadow.get_width()//2 + 2, title_y + 140 + 2))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, title_y + 140))
        
        # Dessiner Mario qui court
        pygame.draw.rect(screen, MARIO_RED, (mario_x, HEIGHT - 200, 40, 60))
        pygame.draw.rect(screen, MARIO_BLUE, (mario_x + 5, HEIGHT - 200 + 40, 10, 20))
        pygame.draw.rect(screen, MARIO_BLUE, (mario_x + 25, HEIGHT - 200 + 40, 10, 20))
        
        # Dessiner les options du menu
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            option_shadow = menu_font.render(option, True, (0, 0, 0))
            option_text = menu_font.render(option, True, color)
            y_pos = HEIGHT - 150 + i * 60
            screen.blit(option_shadow, (WIDTH//2 - option_shadow.get_width()//2 + 2, y_pos + 2))
            screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, y_pos))
        
        # Instructions
        instructions = small_font.render("Utilisez les flèches pour naviguer et Entrée pour selectionner", True, WHITE)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)

# Initialisation du jeu
player = Player()
current_level = 1
platforms, coins, doors, enemies = load_level(current_level)
game_state = "menu"

# Arrière-plan avec effet de profondeur
background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT//2)
    size = random.randint(1, 3)
    alpha = random.randint(100, 200)
    pygame.draw.circle(background, (255, 255, 255, alpha), (x, y), size)

# Nuages avec différentes couches pour l'effet de profondeur
clouds = [
    (100, 100, 1),
    (400, 150, 2),
    (700, 80, 1),
    (200, 50, 3),
    (600, 120, 2),
    (300, 200, 1),
    (500, 80, 2)
]

# Game loop
clock = pygame.time.Clock()
running = True

# Afficher le menu au démarrage
show_menu()
game_state = "playing"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.jump()
            if event.key == pygame.K_r and game_state == "playing":
                player = Player()
                current_level = 1
                platforms, coins, doors, enemies = load_level(current_level)
            if event.key == pygame.K_RETURN and (game_state == "game_over" or game_state == "victory"):
                player = Player()
                current_level = 1
                platforms, coins, doors, enemies = load_level(current_level)
                game_state = "playing"
            if event.key == pygame.K_ESCAPE:
                game_state = "menu"
                show_menu()
                game_state = "playing"

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed
            player.facing_right = False
        if keys[pygame.K_RIGHT]:
            player.x += player.speed
            player.facing_right = True

        for enemy in enemies:
            enemy.update()

        result = player.update(platforms, coins, doors, enemies, current_level)
        if result == "game_over":
            game_state = "game_over"
        elif result != current_level:
            if result == 4 and current_level == 3:
                game_state = "victory"
            else:
                current_level = result
                platforms, coins, doors, enemies = load_level(current_level)
                player.x = 100
                player.y = HEIGHT - 150
                player.vel_y = 0
                player.is_jumping = False

    # Dessin
    screen.fill(SKY_BLUE)
    
    # Dessiner l'arrière-plan
    screen.blit(background, (0, 0))
    
    # Dessiner les nuages avec effet de parallaxe
    for cloud in clouds:
        cloud_x, cloud_y, layer = cloud
        offset = pygame.time.get_ticks() / (100 * layer) % WIDTH
        cloud_x = (cloud_x - offset) % WIDTH
        
        size = 20 + layer * 10
        pygame.draw.circle(screen, WHITE, (int(cloud_x), cloud_y), size)
        pygame.draw.circle(screen, WHITE, (int(cloud_x) + size//2, cloud_y - size//3), size//1.5)
        pygame.draw.circle(screen, WHITE, (int(cloud_x) + size, cloud_y), size)
    
    for platform in platforms:
        platform.draw()
    
    for coin in coins:
        coin.draw()
    
    for door in doors:
        door.draw()
    
    for enemy in enemies:
        enemy.draw()
    
    player.draw()

    # Afficher le HUD avec effet 3D
    pygame.draw.rect(screen, (0, 0, 0, 128), (5, 5, 200, 140), border_radius=5)
    pygame.draw.rect(screen, (50, 50, 50), (5, 5, 200, 140), 2, border_radius=5)
    
    score_text = game_font.render(f"Score: {player.score}", True, WHITE)
    level_text = game_font.render(f"Niveau: {current_level}", True, WHITE)
    coins_text = game_font.render(f"Pièces: {player.coins_collected}", True, WHITE)
    lives_text = game_font.render(f"Vies: {player.lives}", True, WHITE)
    
    screen.blit(score_text, (15, 15))
    screen.blit(level_text, (15, 55))
    screen.blit(coins_text, (15, 95))
    screen.blit(lives_text, (15, 135))

    instructions = small_font.render("Flèches: Bouger - Espace: Sauter - R: Reset - Échap: Menu", True, WHITE)
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 30))

    if game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_shadow = big_font.render("GAME OVER", True, (0, 0, 0))
        game_over_text = big_font.render("GAME OVER", True, RED)
        screen.blit(game_over_shadow, (WIDTH//2 - game_over_shadow.get_width()//2 + 3, HEIGHT//2 - 50 + 3))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        
        restart_text = game_font.render("Appuyez sur ENTER pour recommencer", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    if game_state == "victory":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        victory_shadow = big_font.render("VICTOIRE!", True, (0, 0, 0))
        victory_text = big_font.render("VICTOIRE!", True, YELLOW)
        screen.blit(victory_shadow, (WIDTH//2 - victory_shadow.get_width()//2 + 3, HEIGHT//2 - 80 + 3))
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 80))
        
        score_final_text = game_font.render(f"Score final: {player.score}", True, WHITE)
        screen.blit(score_final_text, (WIDTH//2 - score_final_text.get_width()//2, HEIGHT//2))
        
        restart_text = game_font.render("Appuyez sur ENTER pour recommencer", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
