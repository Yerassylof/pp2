import pygame, random, sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game Extended")

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

import os
# Change working directory to the script's location so assets load correctly
os.chdir(os.path.dirname(__file__))

# Load image assets
road   = pygame.image.load("png/background.png")
car    = pygame.image.load("png/player.png")
enemy  = pygame.image.load("png/enemy.png")
coin   = pygame.image.load("png/coin.png")

# Scale images to desired sizes
road  = pygame.transform.scale(road,  (WIDTH, HEIGHT))
car   = pygame.transform.scale(car,   (50, 100))
enemy = pygame.transform.scale(enemy, (50, 100))
coin  = pygame.transform.scale(coin,  (30, 30))

# Place player car near the bottom-center of the screen
player_rect = car.get_rect(center=(WIDTH // 2, HEIGHT - 100))

# Place enemy car above the top edge (off-screen) at a random x position
enemy_rect  = enemy.get_rect(center=(random.randint(50, WIDTH - 50), -100))
enemy_speed = 5  # Initial downward speed of the enemy

# --- Coin helper ---
def random_coin():
    """Spawn a coin at a random x position above the screen.
    Returns its rect and a randomly chosen point value (weight)."""
    rect   = coin.get_rect(center=(random.randint(50, WIDTH - 50), -50))
    weight = random.choice([1, 2, 5])  # 1 = common, 2 = uncommon, 5 = rare
    return rect, weight

# Spawn the first coin
coin_rect, coin_weight = random_coin()

# Score counter and font for HUD
score = 0
font  = pygame.font.SysFont("Arial", 24)

# ──────────────── Main game loop ────────────────
running = True
while running:

    # Draw the scrolling road background
    screen.blit(road, (0, 0))

    # Handle window-close event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Player input: move left / right, clamped to screen edges ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  and player_rect.left  > 0:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += 5

    # --- Enemy movement: scroll down, respawn at top when off-screen ---
    enemy_rect.y += enemy_speed
    if enemy_rect.top > HEIGHT:
        enemy_rect.center = (random.randint(50, WIDTH - 50), -100)

    # --- Coin movement: scroll down at fixed speed, respawn when off-screen ---
    coin_rect.y += 5
    if coin_rect.top > HEIGHT:
        coin_rect, coin_weight = random_coin()

    # --- Collision: player hits enemy → Game Over ---
    if player_rect.colliderect(enemy_rect):
        print("Game Over!")
        pygame.quit()
        sys.exit()

    # --- Collision: player collects coin ---
    if player_rect.colliderect(coin_rect):
        score += coin_weight          # Add the coin's point value to score
        coin_rect, coin_weight = random_coin()  # Spawn a new coin

        # Every 10 points, increase enemy speed by 1 (difficulty ramp)
        if score % 10 == 0:
            enemy_speed += 1

    # --- Draw sprites ---
    screen.blit(car,   player_rect)
    screen.blit(enemy, enemy_rect)
    screen.blit(coin,  coin_rect)

    # --- HUD: display current score in top-left corner ---
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(50)  # Cap at 50 FPS