import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simple Fighting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Fonts
title_font = pygame.font.Font(None, 128)
menu_font = pygame.font.Font(None, 64)
font = pygame.font.Font(None, 48)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((100, 200))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 100
        self.speed = 8
        self.attack_cooldown = 0
        self.max_cooldown = 30  # 0.5 seconds at 60 FPS
        self.special_cooldown = 0
        self.max_special_cooldown = 180  # 3 seconds at 60 FPS
        self.jump_power = 20
        self.y_velocity = 0
        self.is_jumping = False
        self.facing_right = True if x < WIDTH // 2 else False

    def move(self, dx):
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

    def jump(self):
        if not self.is_jumping:
            self.y_velocity = -self.jump_power
            self.is_jumping = True

    def apply_gravity(self, platforms):
        self.y_velocity += 1  # Gravity
        self.rect.y += self.y_velocity

        # Check for collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_velocity > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.is_jumping = False
                    self.y_velocity = 0
                elif self.y_velocity < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.y_velocity = 0

        # Check for collision with ground
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False
            self.y_velocity = 0

    def attack(self, other):
        if self.attack_cooldown == 0 and abs(self.rect.x - other.rect.x) < 120:
            damage = random.randint(5, 15)
            other.health -= damage
            other.health = max(0, other.health)
            self.attack_cooldown = self.max_cooldown
            return damage
        return 0

    def special_attack(self):
        if self.special_cooldown == 0:
            self.special_cooldown = self.max_special_cooldown
            return Projectile(self.rect.centerx, self.rect.centery, self.facing_right)
        return None

    def update(self, platforms):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        self.apply_gravity(platforms)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right):
        super().__init__()
        self.image = pygame.Surface((40, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 15 if facing_right else -15

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def title_screen():
    while True:
        screen.fill(BLACK)
        draw_text('Simple Fighting Game', title_font, WHITE, screen, WIDTH // 2 - 400, HEIGHT // 4)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 75)
        button_2 = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 150, 300, 75)
        
        pygame.draw.rect(screen, WHITE, button_1)
        pygame.draw.rect(screen, WHITE, button_2)

        draw_text('Play', menu_font, BLACK, screen, WIDTH // 2 - 40, HEIGHT // 2 + 15)
        draw_text('Quit', menu_font, BLACK, screen, WIDTH // 2 - 40, HEIGHT // 2 + 165)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        if button_1.collidepoint((mx, my)):
            if click:
                return
        if button_2.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        pygame.time.Clock().tick(60)

def game():
    # Create players
    player1 = Player(WIDTH // 4, HEIGHT - 200, RED)
    player2 = Player(3 * WIDTH // 4, HEIGHT - 200, BLUE)

    # Create platforms
    platforms = [
        Platform(WIDTH // 4 - 150, HEIGHT * 2 // 3, 300, 30),
        Platform(WIDTH // 2 - 150, HEIGHT // 2, 300, 30),
        Platform(3 * WIDTH // 4 - 150, HEIGHT * 2 // 3, 300, 30)
    ]

    # Create sprite groups
    all_sprites = pygame.sprite.Group(player1, player2, *platforms)
    projectiles = pygame.sprite.Group()

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # Player controls
        keys = pygame.key.get_pressed()
        
        # Player 1 controls
        if keys[pygame.K_a]:
            player1.move(-player1.speed)
        if keys[pygame.K_d]:
            player1.move(player1.speed)
        if keys[pygame.K_w]:
            player1.jump()
        if keys[pygame.K_s]:
            player1.attack(player2)
        if keys[pygame.K_e]:
            projectile = player1.special_attack()
            if projectile:
                projectiles.add(projectile)
                all_sprites.add(projectile)

        # Player 2 controls
        if keys[pygame.K_LEFT]:
            player2.move(-player2.speed)
        if keys[pygame.K_RIGHT]:
            player2.move(player2.speed)
        if keys[pygame.K_UP]:
            player2.jump()
        if keys[pygame.K_DOWN]:
            player2.attack(player1)
        if keys[pygame.K_RCTRL]:
            projectile = player2.special_attack()
            if projectile:
                projectiles.add(projectile)
                all_sprites.add(projectile)

        # Update sprites
        player1.update(platforms)
        player2.update(platforms)
        projectiles.update()

        # Check for projectile hits
        for projectile in projectiles:
            if projectile.rect.colliderect(player1.rect) and projectile.speed < 0:
                player1.health -= 20
                projectile.kill()
            elif projectile.rect.colliderect(player2.rect) and projectile.speed > 0:
                player2.health -= 20
                projectile.kill()

        # Draw everything
        screen.fill(WHITE)
        all_sprites.draw(screen)

        # Draw health bars
        pygame.draw.rect(screen, RED, (20, 20, player1.health * 4, 40))
        pygame.draw.rect(screen, BLUE, (WIDTH - 420, 20, player2.health * 4, 40))

        # Draw cooldown bars
        pygame.draw.rect(screen, GRAY, (20, 80, 120, 20))
        pygame.draw.rect(screen, RED, (20, 80, 120 * (1 - player1.attack_cooldown / player1.max_cooldown), 20))
        pygame.draw.rect(screen, GRAY, (WIDTH - 140, 80, 120, 20))
        pygame.draw.rect(screen, BLUE, (WIDTH - 140, 80, 120 * (1 - player2.attack_cooldown / player2.max_cooldown), 20))

        # Draw special attack cooldown bars
        pygame.draw.rect(screen, GRAY, (20, 120, 120, 20))
        pygame.draw.rect(screen, YELLOW, (20, 120, 120 * (1 - player1.special_cooldown / player1.max_special_cooldown), 20))
        pygame.draw.rect(screen, GRAY, (WIDTH - 140, 120, 120, 20))
        pygame.draw.rect(screen, YELLOW, (WIDTH - 140, 120, 120 * (1 - player2.special_cooldown / player2.max_special_cooldown), 20))

        # Display health text
        health_text1 = font.render(f"P1: {player1.health}", True, RED)
        health_text2 = font.render(f"P2: {player2.health}", True, BLUE)
        screen.blit(health_text1, (20, 160))
        screen.blit(health_text2, (WIDTH - 200, 160))

        # Update the display
        pygame.display.flip()

        # Check for game over
        if player1.health <= 0 or player2.health <= 0:
            winner = "Player 1" if player2.health <= 0 else "Player 2"
            print(f"{winner} wins!")
            running = False

        clock.tick(60)

    # Display winner for 3 seconds
    screen.fill(WHITE)
    winner_text = title_font.render(f"{winner} wins!", True, BLACK)
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Main game flow
while True:
    title_screen()
    game()

# Quit Pygame
pygame.quit()
sys.exit()