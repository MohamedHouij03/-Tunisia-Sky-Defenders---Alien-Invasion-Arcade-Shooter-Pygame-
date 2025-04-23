import pygame
import random
import sys
from pygame import mixer


# Initialize pygame
pygame.init()
mixer.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tunisian Sky Defenders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TUNISIA_RED = (200, 16, 46)

# Fonts
title_font = pygame.font.SysFont('space nova', 48, bold=True)
menu_font = pygame.font.SysFont('space nova', 36)
hud_font = pygame.font.SysFont('space nova', 24)

# Game states
MENU = 0
WEAPON_SELECT = 1
GAME = 2
GAME_OVER = 3
game_state = MENU

# Weapon types
WEAPONS = {
    "Standard": {"color": YELLOW, "speed": 10, "damage": 1, "rate": 250},
    "Rapid Fire": {"color": GREEN, "speed": 12, "damage": 1, "rate": 100},
    "Heavy Cannon": {"color": RED, "speed": 8, "damage": 3, "rate": 400}
}
selected_weapon = "Standard"

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = menu_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Create buttons
start_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Continue", TUNISIA_RED, (150, 0, 0))
weapon_buttons = [
    Button(WIDTH//2 - 300, HEIGHT//2, 200, 50, "Standard", BLUE, (0, 0, 150)),
    Button(WIDTH//2 - 50, HEIGHT//2, 200, 50, "Rapid Fire", GREEN, (0, 100, 0)),
    Button(WIDTH//2 + 200, HEIGHT//2, 200, 50, "Heavy Cannon", RED, (100, 0, 0))
]
play_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50, "Start Mission", GREEN, (0, 150, 0))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Load player image
        try:
            self.original_image = pygame.image.load('tunisian-air-force-tunisian-armed-forces-tunisian-independence-png-favpng-hYKPBC2WjULC4hcQMG8CnwpRx.jpg').convert_alpha()
            # Resize if needed (adjust 50, 40 to your desired dimensions)
            self.image = pygame.transform.scale(self.original_image, (50, 40))
        except:
            # Fallback if image fails to load
            print("Could not load player_jet.png - using placeholder")
            self.image = pygame.Surface((50, 40))
            self.image.fill(GREEN)  # Green placeholder
            # Draw a simple triangle for the jet
            pygame.draw.polygon(self.image, WHITE, [(25, 0), (0, 40), (50, 40)])
            # Add Tunisian flag colors
            pygame.draw.rect(self.image, TUNISIA_RED, (10, 15, 30, 10))
            pygame.draw.circle(self.image, WHITE, (25, 20), 5)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.health = 3
        self.weapon = WEAPONS["Standard"]
        self.last_shot = 0
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.weapon["rate"]:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, self.weapon)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(weapon["color"])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -weapon["speed"]
        self.damage = weapon["damage"]
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)
        self.health = 2
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

# Game variables
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
score = 0

# Create initial enemies
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if game_state == MENU:
            start_button.check_hover(mouse_pos)
            if start_button.is_clicked(mouse_pos, event):
                game_state = WEAPON_SELECT
                
        elif game_state == WEAPON_SELECT:
            for btn in weapon_buttons:
                btn.check_hover(mouse_pos)
                if btn.is_clicked(mouse_pos, event):
                    selected_weapon = btn.text
            play_button.check_hover(mouse_pos)
            if play_button.is_clicked(mouse_pos, event):
                player.weapon = WEAPONS[selected_weapon]
                game_state = GAME
                
        elif game_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                    
        elif game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game and return to weapon selection
                    game_state = WEAPON_SELECT
                    all_sprites = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    player = Player()
                    all_sprites.add(player)
                    score = 0
                    for i in range(8):
                        enemy = Enemy()
                        all_sprites.add(enemy)
                        enemies.add(enemy)
    
    # Update
    if game_state == GAME:
        all_sprites.update()
        
        # Check bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            for bullet in bullet_list:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemy.kill()
                    score += 10
                    # Respawn new enemy
                    new_enemy = Enemy()
                    all_sprites.add(new_enemy)
                    enemies.add(new_enemy)
        
        # Check enemy-player collisions
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            player.health -= 1
            new_enemy = Enemy()
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)
            if player.health <= 0:
                game_state = GAME_OVER
    
    # Drawing
    screen.fill(BLACK)
    
    if game_state == MENU:
        # Draw stars background
        for i in range(100):
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Title
        title1 = title_font.render("TUNISIAN SKY DEFENDERS", True, TUNISIA_RED)
        title2 = menu_font.render("Aliens are attacking Tunisia!", True, WHITE)
        title3 = menu_font.render("We must defend our territories!", True, WHITE)
        
        screen.blit(title1, (WIDTH//2 - title1.get_width()//2, HEIGHT//4))
        screen.blit(title2, (WIDTH//2 - title2.get_width()//2, HEIGHT//3))
        screen.blit(title3, (WIDTH//2 - title3.get_width()//2, HEIGHT//3 + 40))
        
        start_button.draw(screen)
        
    elif game_state == WEAPON_SELECT:
        # Draw weapon selection screen
        title = title_font.render("SELECT YOUR WEAPON", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        for btn in weapon_buttons:
            btn.draw(screen)
            
        selected_text = menu_font.render(f"Selected: {selected_weapon}", True, WHITE)
        screen.blit(selected_text, (WIDTH//2 - selected_text.get_width()//2, HEIGHT//2 + 70))
        
        play_button.draw(screen)
        
    elif game_state == GAME:
        # Draw game screen
        for i in range(50):  # Fewer stars during gameplay
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        all_sprites.draw(screen)
        
        # Draw HUD
        score_text = hud_font.render(f"Score: {score}", True, WHITE)
        health_text = hud_font.render(f"Health: {player.health}", True, WHITE)
        weapon_text = hud_font.render(f"Weapon: {selected_weapon}", True, player.weapon["color"])
        
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(weapon_text, (10, 70))
        
    elif game_state == GAME_OVER:
        # Draw game over screen
        game_over_text = title_font.render("GAME OVER", True, RED)
        score_text = title_font.render(f"Final Score: {score}", True, WHITE)
        restart_text = menu_font.render("Press R to Choose New Weapon", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()