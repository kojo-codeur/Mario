import pygame  # Importation de la bibliothèque Pygame pour créer le jeu
import sys     # Importation du module sys pour gérer la fermeture du programme
import random  # Importation du module random pour générer des éléments aléatoires

# Initialisation de Pygame
pygame.init()  # Initialise tous les modules Pygame nécessaires

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600  # Définition de la largeur et hauteur de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de la fenêtre de jeu
pygame.display.set_caption("Mario-like Platformer")  # Définition du titre de la fenêtre

# Couleurs - Définition des couleurs utilisées dans le jeu en format RGB
SKY_BLUE = (107, 140, 255)  # Bleu ciel pour l'arrière-plan
BROWN = (139, 69, 19)       # Marron pour les détails des plateformes
GREEN = (76, 175, 80)       # Vert pour les plateformes
RED = (255, 0, 0)           # Rouge pour le joueur
YELLOW = (255, 255, 0)      # Jaune pour les pièces
WHITE = (255, 255, 255)     # Blanc pour le texte et les yeux
BLACK = (0, 0, 0)           # Noir pour les contours
ORANGE = (255, 165, 0)      # Orange pour les ennemis

# Joueur - Définition de la classe représentant le personnage principal
class Player:
    def __init__(self):  # Constructeur de la classe Player
        self.width = 40          # Largeur du joueur
        self.height = 60         # Hauteur du joueur
        self.x = 100             # Position horizontale initiale
        self.y = HEIGHT - 150    # Position verticale initiale
        self.vel_y = 0           # Vitesse verticale (pour le saut et la chute)
        self.jump_power = -15    # Puissance du saut (négatif car vers le haut)
        self.gravity = 0.8       # Force de gravité appliquée au joueur
        self.is_jumping = False  # État indiquant si le joueur saute
        self.speed = 5           # Vitesse de déplacement horizontal
        self.facing_right = True # Direction vers laquelle le joueur regarde
        self.score = 0           # Score actuel du joueur
        self.coins_collected = 0 # Nombre de pièces collectées
        self.lives = 3           # Nombre de vies restantes
        self.invincible = False  # État d'invincibilité temporaire
        self.invincible_timer = 0 # Compteur pour l'invincibilité

    def draw(self):  # Méthode pour dessiner le joueur à l'écran
        # Dessiner le corps de Mario
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            # Clignotement pendant l'invincibilité (tous les 200ms)
            return  # Ne pas dessiner pendant les phases de clignotement
        
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))  # Corps principal
        
        # Dessiner la casquette
        pygame.draw.rect(screen, RED, (self.x - 5, self.y, self.width + 10, 15))  # Casquette de Mario
        
        # Dessiner les yeux (simplifiés)
        eye_x = self.x + 25 if self.facing_right else self.x + 5  # Position de l'oeil selon la direction
        pygame.draw.circle(screen, WHITE, (eye_x, self.y + 20), 5)  # Oeil du personnage

    def update(self, platforms, coins, doors, enemies, current_level):  # Mise à jour de l'état du joueur
        # Appliquer la gravité
        self.vel_y += self.gravity  # Augmente la vitesse verticale avec la gravité
        self.y += self.vel_y       # Met à jour la position verticale

        # Gérer l'invincibilité temporaire
        if self.invincible:        # Si le joueur est invincible
            self.invincible_timer -= 1  # Décrémente le compteur
            if self.invincible_timer <= 0:  # Si le compteur arrive à zéro
                self.invincible = False    # Fin de l'invincibilité

        # Collision avec le sol
        if self.y > HEIGHT - self.height:  # Si le joueur touche le bas de l'écran
            self.y = HEIGHT - self.height  # Replace le joueur sur le sol
            self.vel_y = 0                 # Annule la vitesse verticale
            self.is_jumping = False        # Le joueur n'est plus en train de sauter

        # Collision avec les plateformes
        for platform in platforms:  # Pour chaque plateforme
            if (self.y + self.height >= platform.y and  # Si le bas du joueur est au niveau du haut de la plateforme
                self.y + self.height <= platform.y + 20 and  # Et dans la marge de collision
                self.x + self.width > platform.x and  # Et que le joueur chevauche horizontalement
                self.x < platform.x + platform.width and  # La plateforme
                self.vel_y > 0):  # Et que le joueur descend
                self.y = platform.y - self.height  # Place le joueur sur la plateforme
                self.vel_y = 0                    # Annule la vitesse verticale
                self.is_jumping = False           # Le joueur n'est plus en train de sauter

        # Collecter les pièces
        for coin in coins[:]:  # Pour chaque pièce (copie de la liste pour modification)
            if (self.x + self.width > coin.x and  # Si le joueur chevauche horizontalement
                self.x < coin.x + coin.size and   # La pièce
                self.y + self.height > coin.y and # Et verticalement
                self.y < coin.y + coin.size):     # La pièce
                coins.remove(coin)               # Supprime la pièce de la liste
                self.score += 100                # Ajoute 100 points au score
                self.coins_collected += 1        # Incrémente le compteur de pièces

        # Collision avec les ennemis
        for enemy in enemies[:]:  # Pour chaque ennemi (copie de la liste pour modification)
            if (self.x + self.width > enemy.x and  # Si le joueur chevauche horizontalement
                self.x < enemy.x + enemy.width and # L'ennemi
                self.y + self.height > enemy.y and # Et verticalement
                self.y < enemy.y + enemy.height):  # L'ennemi
                if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height/2:  # Si le joueur tombe sur l'ennemi
                    # Écraser l'ennemi
                    enemies.remove(enemy)          # Supprime l'ennemi
                    self.vel_y = self.jump_power/2 # Donne un petit rebond au joueur
                    self.score += 200              # Ajoute 200 points au score
                elif not self.invincible:          # Si le joueur n'est pas invincible
                    # Perdre une vie
                    self.lives -= 1                # Enlève une vie
                    self.invincible = True         # Active l'invincibilité temporaire
                    self.invincible_timer = 60     # 1 seconde d'invincibilité à 60 FPS
                    if self.lives <= 0:            # Si plus de vies
                        return "game_over"         # Retourne l'état "game over"
        
        # Vérifier si le joueur tombe hors de l'écran
        if self.y > HEIGHT:        # Si le joueur est tombé complètement hors de l'écran
            self.lives -= 1        # Enlève une vie
            self.x = 100           # Réinitialise la position horizontale
            self.y = HEIGHT - 150  # Réinitialise la position verticale
            self.vel_y = 0         # Réinitialise la vitesse verticale
            if self.lives <= 0:    # Si plus de vies
                return "game_over" # Retourne l'état "game over"
            self.invincible = True         # Active l'invincibilité temporaire
            self.invincible_timer = 120    # 2 secondes d'invincibilité à 60 FPS

        # Vérifier si le joueur atteint la porte pour changer de niveau
        for door in doors:  # Pour chaque porte
            if (self.x + self.width > door.x and  # Si le joueur chevauche horizontalement
                self.x < door.x + door.width and  # La porte
                self.y + self.height > door.y and # Et verticalement
                self.y < door.y + door.height):   # La porte
                if self.coins_collected >= door.coins_required:  # Si assez de pièces collectées
                    return door.next_level  # Retourne le prochain niveau
        
        return current_level  # Retourne le niveau actuel si aucun changement

    def jump(self):  # Méthode pour faire sauter le joueur
        if not self.is_jumping:  # Si le joueur n'est pas déjà en train de sauter
            self.vel_y = self.jump_power  # Applique la force de saut
            self.is_jumping = True        # Met à jour l'état de saut

# Plateforme - Définition de la classe représentant les plateformes
class Platform:
    def __init__(self, x, y, width):  # Constructeur de la classe Platform
        self.x = x      # Position horizontale
        self.y = y      # Position verticale
        self.width = width  # Largeur de la plateforme
        self.height = 20    # Hauteur de la plateforme

    def draw(self):  # Méthode pour dessiner la plateforme
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))  # Rectangle vert principal
        # Ajouter des détails aux briques
        for i in range(0, self.width, 15):  # Lignes verticales tous les 15 pixels
            pygame.draw.line(screen, BROWN, (self.x + i, self.y), (self.x + i, self.y + self.height), 1)
        for i in range(0, self.height, 15):  # Lignes horizontales tous les 15 pixels
            pygame.draw.line(screen, BROWN, (self.x, self.y + i), (self.x + self.width, self.y + i), 1)

# Pièce - Définition de la classe représentant les pièces à collecter
class Coin:
    def __init__(self, x, y):  # Constructeur de la classe Coin
        self.x = x          # Position horizontale
        self.y = y          # Position verticale
        self.size = 15      # Taille de la pièce

    def draw(self):  # Méthode pour dessiner la pièce
        pygame.draw.circle(screen, YELLOW, (self.x + self.size//2, self.y + self.size//2), self.size//2)  # Cercle jaune
        pygame.draw.circle(screen, BLACK, (self.x + self.size//2, self.y + self.size//2), self.size//2, 1)  # Contour noir

# Porte pour changer de niveau - Définition de la classe représentant les portes
class Door:
    def __init__(self, x, y, next_level, coins_required):  # Constructeur de la classe Door
        self.x = x                  # Position horizontale
        self.y = y                  # Position verticale
        self.width = 40             # Largeur de la porte
        self.height = 60            # Hauteur de la porte
        self.next_level = next_level  # Niveau suivant accessible par cette porte
        self.coins_required = coins_required  # Pièces nécessaires pour utiliser la porte

    def draw(self):  # Méthode pour dessiner la porte
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))  # Rectangle marron principal
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)  # Contour noir
        
        # Afficher le nombre de pièces requises
        font = pygame.font.SysFont(None, 20)  # Police de taille 20
        text = font.render(str(self.coins_required), True, WHITE)  # Texte blanc avec le nombre de pièces
        screen.blit(text, (self.x + self.width//2 - text.get_width()//2, self.y + self.height//2 - text.get_height()//2))  # Centrer le texte

# Ennemi - Définition de la classe représentant les ennemis
class Enemy:
    def __init__(self, x, y, min_x, max_x, level):  # Constructeur de la classe Enemy
        self.x = x          # Position horizontale initiale
        self.y = y          # Position verticale
        self.width = 30     # Largeur de l'ennemi
        self.height = 30    # Hauteur de l'ennemi
        # La vitesse augmente avec le niveau
        self.speed = 0 + (level * 0.5)  # Niveau 1: 0.5, Niveau 2: 1, Niveau 3: 1.5
        self.min_x = min_x  # Limite gauche de déplacement
        self.max_x = max_x  # Limite droite de déplacement
        self.direction = 1  # 1 pour droite, -1 pour gauche

    def draw(self):  # Méthode pour dessiner l'ennemi
        pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))  # Corps orange
        # Dessiner les yeux
        pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 10), 5)  # Oeil gauche
        pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 10), 5)  # Oeil droit
        pygame.draw.circle(screen, BLACK, (self.x + 8, self.y + 10), 2)  # Pupille gauche
        pygame.draw.circle(screen, BLACK, (self.x + 22, self.y + 10), 2)  # Pupille droite

    def update(self):  # Méthode pour mettre à jour la position de l'ennemi
        self.x += self.speed * self.direction  # Déplace l'ennemi selon sa direction
        
        # Changer de direction aux limites
        if self.x <= self.min_x:              # Si l'ennemi atteint la limite gauche
            self.direction = 1                # Change de direction vers la droite
        elif self.x + self.width >= self.max_x:  # Si l'ennemi atteint la limite droite
            self.direction = -1               # Change de direction vers la gauche

# Définition des niveaux - Fonction pour charger les éléments de chaque niveau
def load_level(level_num):
    platforms = []  # Liste des plateformes du niveau
    coins = []      # Liste des pièces du niveau
    doors = []      # Liste des portes du niveau
    enemies = []    # Liste des ennemis du niveau
    
    if level_num == 1:  # Configuration du niveau 1
        # Niveau 1
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),  # Sol principal
            Platform(200, 450, 200),          # Plateforme supplémentaire
            Platform(500, 350, 150),          # Plateforme supplémentaire
            Platform(300, 250, 100),          # Plateforme supplémentaire
            Platform(600, 200, 200)           # Plateforme supplémentaire
        ]
        coins = [
            Coin(250, 410),  # Pièce sur la première plateforme
            Coin(550, 310),  # Pièce sur la deuxième plateforme
            Coin(330, 210),  # Pièce sur la troisième plateforme
            Coin(650, 160)   # Pièce sur la quatrième plateforme
        ]
        doors = [
            Door(700, 140, 2, 3)  # Porte pour niveau 2, nécessite 3 pièces
        ]
        enemies = [
            Enemy(400, 430, 200, 400, level_num),  # Ennemi sur la première plateforme
            Enemy(650, 330, 500, 650, level_num)   # Ennemi sur la deuxième plateforme
        ]
    elif level_num == 2:  # Configuration du niveau 2 (plus difficile)
        # Niveau 2 (plus difficile)
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),  # Sol principal
            Platform(100, 450, 100),          # Plateformes supplémentaires...
            Platform(300, 400, 100),
            Platform(500, 350, 100),
            Platform(200, 300, 100),
            Platform(400, 250, 100),
            Platform(600, 200, 100),
            Platform(300, 150, 100)
        ]
        coins = [
            Coin(130, 410),  # Pièces placées sur les plateformes...
            Coin(330, 360),
            Coin(530, 310),
            Coin(230, 260),
            Coin(430, 210),
            Coin(630, 160),
            Coin(330, 110)
        ]
        doors = [
            Door(700, 90, 3, 5)  # Porte pour niveau 3, nécessite 5 pièces
        ]
        enemies = [
            Enemy(150, 430, 100, 200, level_num),  # Ennemis placés sur les plateformes...
            Enemy(350, 380, 300, 400, level_num),
            Enemy(550, 330, 500, 600, level_num),
            Enemy(250, 280, 200, 300, level_num),
            Enemy(650, 180, 600, 700, level_num)
        ]
    elif level_num == 3:  # Configuration du niveau 3 (encore plus difficile)
        # Niveau 3 (encore plus difficile)
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),  # Sol principal
            Platform(100, 450, 80),           # Plateformes en escalier...
            Platform(250, 400, 80),
            Platform(400, 350, 80),
            Platform(550, 300, 80),
            Platform(700, 250, 80),
            Platform(550, 200, 80),
            Platform(400, 150, 80),
            Platform(250, 100, 80),
            Platform(100, 50, 80)
        ]
        coins = [
            Coin(130, 410),  # Pièces sur chaque plateforme...
            Coin(280, 360),
            Coin(430, 310),
            Coin(580, 260),
            Coin(730, 210),
            Coin(580, 160),
            Coin(430, 110),
            Coin(280, 60),
            Coin(130, 10)
        ]
        doors = [
            Door(700, 10, 4, 7)  # Porte pour niveau final, nécessite 7 pièces
        ]
        enemies = [
            Enemy(150, 430, 100, 180, level_num),  # Ennemis sur plusieurs plateformes...
            Enemy(300, 380, 250, 330, level_num),
            Enemy(450, 330, 400, 480, level_num),
            Enemy(600, 280, 550, 630, level_num),
            Enemy(600, 180, 550, 630, level_num),
            Enemy(450, 130, 400, 480, level_num),
            Enemy(300, 80, 250, 330, level_num)
        ]
    elif level_num == 4:  # Configuration du niveau final (écran de victoire)
        # Niveau final - victoire!
        platforms = [
            Platform(0, HEIGHT - 40, WIDTH),  # Sol principal
            Platform(300, 400, 200),          # Plateformes décoratives...
            Platform(350, 300, 100),
            Platform(400, 200, 200)
        ]
        coins = []  # Aucune pièce dans le niveau final
        doors = [
            Door(450, 140, 1, 0)  # Porte pour recommencer le jeu
        ]
        enemies = []  # Aucun ennemi dans le niveau final
    
    return platforms, coins, doors, enemies  # Retourne tous les éléments du niveau

# Initialisation du jeu
player = Player()  # Crée une instance du joueur
current_level = 1  # Niveau actuel (commence au niveau 1)
platforms, coins, doors, enemies = load_level(current_level)  # Charge les éléments du niveau 1
game_state = "playing"  # État initial du jeu: "playing", "game_over", "victory"

# Nuages décoratifs - Positions fixes pour les nuages en arrière-plan
clouds = [(100, 100), (400, 150), (700, 80)]

# Police pour le texte
font = pygame.font.SysFont(None, 36)      # Police de taille 36 pour le texte standard
big_font = pygame.font.SysFont(None, 72)  # Police de taille 72 pour les grands textes

# Game loop - Boucle principale du jeu
clock = pygame.time.Clock()  # Crée un objet horloge pour contrôler le framerate
running = True               # Variable pour contrôler la boucle principale

while running:  # Boucle principale du jeu
    for event in pygame.event.get():  # Traitement des événements
        if event.type == pygame.QUIT:  # Si l'utilisateur clique sur la croix de fermeture
            running = False           # Arrête la boucle principale
        if event.type == pygame.KEYDOWN:  # Si une touche est pressée
            if event.key == pygame.K_SPACE and game_state == "playing":  # Touche ESPACE pendant le jeu
                player.jump()          # Fait sauter le joueur
            if event.key == pygame.K_r:  # Touche R (reset)
                # Reset du jeu avec R
                player = Player()      # Recrée un nouveau joueur
                current_level = 1      # Remet le niveau à 1
                platforms, coins, doors, enemies = load_level(current_level)  # Recharge le niveau 1
                game_state = "playing" # Remet l'état du jeu à "playing"
            if event.key == pygame.K_RETURN and (game_state == "game_over" or game_state == "victory"):  # Touche ENTREE en fin de jeu
                # Recommencer le jeu
                player = Player()      # Recrée un nouveau joueur
                current_level = 1      # Remet le niveau à 1
                platforms, coins, doors, enemies = load_level(current_level)  # Recharge le niveau 1
                game_state = "playing" # Remet l'état du jeu à "playing"

    if game_state == "playing":  # Si le jeu est en cours
        # Mouvement du joueur
        keys = pygame.key.get_pressed()  # Récupère l'état de toutes les touches
        if keys[pygame.K_LEFT]:          # Si la flèche gauche est enfoncée
            player.x -= player.speed     # Déplace le joueur vers la gauche
            player.facing_right = False  # Met à jour la direction
        if keys[pygame.K_RIGHT]:         # Si la flèche droite est enfoncée
            player.x += player.speed     # Déplace le joueur vers la droite
            player.facing_right = True   # Met à jour la direction

        # Mise à jour des ennemis
        for enemy in enemies:  # Pour chaque ennemi
            enemy.update()     # Met à jour sa position

        # Mise à jour du joueur
        result = player.update(platforms, coins, doors, enemies, current_level)  # Met à jour l'état du joueur
        if result == "game_over":  # Si le joueur a perdu toutes ses vies
            game_state = "game_over"  # Change l'état du jeu vers "game over"
        elif result != current_level:  # Si le joueur a atteint une porte
            if result == 4 and current_level == 3:  # Si le joueur a complété le niveau 3
                # Victoire après avoir complété le niveau 3
                game_state = "victory"  # Change l'état du jeu vers "victoire"
            else:
                current_level = result  # Passe au niveau suivant
                platforms, coins, doors, enemies = load_level(current_level)  # Charge les éléments du nouveau niveau
                # Réinitialiser la position du joueur mais garder le score et les vies
                player.x = 100           # Réinitialise la position horizontale
                player.y = HEIGHT - 150  # Réinitialise la position verticale
                player.vel_y = 0         # Réinitialise la vitesse verticale
                player.is_jumping = False # Réinitialise l'état de saut

    # Dessin - Phase de rendu graphique
    screen.fill(SKY_BLUE)  # Remplit l'écran avec la couleur de fond
    
    # Dessiner les nuages
    for cloud in clouds:  # Pour chaque position de nuage
        pygame.draw.circle(screen, WHITE, (cloud[0], cloud[1]), 30)        # Partie principale du nuage
        pygame.draw.circle(screen, WHITE, (cloud[0] + 20, cloud[1] - 10), 25)  # Partie supérieure
        pygame.draw.circle(screen, WHITE, (cloud[0] + 40, cloud[1]), 30)       # Partie droite
    
    # Dessiner les plateformes, pièces et portes
    for platform in platforms:  # Pour chaque plateforme
        platform.draw()         # Dessine la plateforme
    
    for coin in coins:          # Pour chaque pièce
        coin.draw()             # Dessine la pièce
    
    for door in doors:          # Pour chaque porte
        door.draw()             # Dessine la porte
    
    # Dessiner les ennemis
    for enemy in enemies:       # Pour chaque ennemi
        enemy.draw()            # Dessine l'ennemi
    
    player.draw()               # Dessine le joueur

    # Afficher le score, le niveau et les vies
    score_text = font.render(f"Score: {player.score}", True, WHITE)  # Crée le texte du score
    level_text = font.render(f"Niveau: {current_level}", True, WHITE)  # Crée le texte du niveau
    coins_text = font.render(f"Pièces: {player.coins_collected}", True, WHITE)  # Crée le texte des pièces
    lives_text = font.render(f"Vies: {player.lives}", True, WHITE)  # Crée le texte des vies
    
    screen.blit(score_text, (10, 10))    # Affiche le score en haut à gauche
    screen.blit(level_text, (10, 50))    # Affiche le niveau en dessous
    screen.blit(coins_text, (10, 90))    # Affiche les pièces en dessous
    screen.blit(lives_text, (10, 130))   # Affiche les vies en dessous

    # Afficher les instructions
    instructions = font.render("Flèches: Bouger - Espace: Sauter - R: Reset", True, WHITE)  # Instructions
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 40))  # Centré en bas

    # Afficher l'écran de game over
    if game_state == "game_over":  # Si le jeu est en état "game over"
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Crée une surface semi-transparente
        overlay.fill((0, 0, 0, 180))  # Remplit en noir semi-transparent
        screen.blit(overlay, (0, 0))  # Affiche l'overlay sur tout l'écran
        
        game_over_text = big_font.render("GAME OVER", True, RED)  # Texte "GAME OVER" en rouge
        restart_text = font.render("Appuyez sur ENTER pour recommencer", True, WHITE)  # Instructions de redémarrage
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))  # Centré verticalement
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))  # En dessous

    # Afficher l'écran de victoire
    if game_state == "victory":  # Si le jeu est en état "victoire"
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Crée une surface semi-transparente
        overlay.fill((0, 0, 0, 180))  # Remplit en noir semi-transparent
        screen.blit(overlay, (0, 0))  # Affiche l'overlay sur tout l'écran
        
        victory_text = big_font.render("VICTOIRE!", True, YELLOW)  # Texte "VICTOIRE!" en jaune
        score_final_text = font.render(f"Score final: {player.score}", True, WHITE)  # Score final
        restart_text = font.render("Appuyez sur ENTER pour recommencer", True, WHITE)  # Instructions de redémarrage
        
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 80))  # Centré verticalement
        screen.blit(score_final_text, (WIDTH//2 - score_final_text.get_width()//2, HEIGHT//2))  # En dessous
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))  # En dessous

    pygame.display.flip()  # Met à jour l'affichage complet
    clock.tick(60)         # Limite le jeu à 60 images par seconde

pygame.quit()  # Quitte proprement Pygame
sys.exit()     # Termine le programme