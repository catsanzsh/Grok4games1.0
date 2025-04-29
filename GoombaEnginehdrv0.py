import pygame
import asyncio
import platform
import sys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
FPS = 60

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRASS = (0, 255, 0)
DIRT = (139, 69, 19)
SKIN = (255, 224, 189)

# Goomba variables
goomba_x = 375
goomba_y = 350
direction = 1  # 1 for right, -1 for left
speed = 5

# Player variables
player_x = 400.0
player_y = 350
player_vx = 0.0
ACCELERATION = 1.0
FRICTION = 0.5
MAX_SPEED = 5.0

# Tile size
TILE_SIZE = 16

def draw_background(screen):
    screen.fill(BLUE)  # Sky
    # Draw hills (background elements inspired by SMB3)
    pygame.draw.ellipse(screen, GREEN, (100, 350, 200, 50))
    pygame.draw.ellipse(screen, GREEN, (400, 350, 150, 40))
    # Draw ground tiles
    for y in range(400, 600, TILE_SIZE):
        color = GRASS if y == 400 else DIRT
        for x in range(0, 800, TILE_SIZE):
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

def draw_goomba(screen, x, y):
    # Enhanced Goomba resembling SMB3 style
    # Body
    pygame.draw.ellipse(screen, (139, 69, 19), (x, y, 50, 40))
    # Eyes
    pygame.draw.ellipse(screen, WHITE, (x + 10, y + 10, 10, 15))
    pygame.draw.ellipse(screen, WHITE, (x + 30, y + 10, 10, 15))
    # Pupils
    pygame.draw.ellipse(screen, BLACK, (x + 12, y + 12, 5, 5))
    pygame.draw.ellipse(screen, BLACK, (x + 32, y + 12, 5, 5))
    # Eyebrows
    pygame.draw.rect(screen, BLACK, (x + 10, y + 5, 10, 5))
    pygame.draw.rect(screen, BLACK, (x + 30, y + 5, 10, 5))
    # Mouth
    pygame.draw.ellipse(screen, BLACK, (x + 15, y + 25, 20, 10))
    # Feet
    pygame.draw.rect(screen, (139, 69, 19), (x + 5, y + 35, 15, 10))
    pygame.draw.rect(screen, (139, 69, 19), (x + 30, y + 35, 15, 10))

def draw_player(screen, x, y):
    # Player designed to resemble Mario from SMB3
    # Body (blue overalls)
    pygame.draw.rect(screen, BLUE, (x + 10, y + 20, 30, 30))
    # Head
    pygame.draw.circle(screen, SKIN, (x + 25, y + 10), 10)
    # Hat
    pygame.draw.rect(screen, RED, (x + 15, y, 20, 10))
    # Eyes
    pygame.draw.circle(screen, BLACK, (x + 20, y + 10), 2)
    pygame.draw.circle(screen, BLACK, (x + 30, y + 10), 2)
    # Mustache
    pygame.draw.rect(screen, BLACK, (x + 20, y + 15, 10, 2))

def setup():
    pygame.display.set_caption("SMB3 Engine Replica")

def update_loop():
    global goomba_x, direction, player_x, player_vx
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle input with physics
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_vx -= ACCELERATION
    if keys[pygame.K_RIGHT]:
        player_vx += ACCELERATION

    # Apply friction
    if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        if player_vx > 0:
            player_vx -= FRICTION
            if player_vx < 0:
                player_vx = 0
        elif player_vx < 0:
            player_vx += FRICTION
            if player_vx > 0:
                player_vx = 0

    # Clamp velocity
    player_vx = max(-MAX_SPEED, min(MAX_SPEED, player_vx))

    # Update position
    player_x += player_vx

    # Keep player within bounds
    if player_x < 0:
        player_x = 0
        player_vx = 0
    elif player_x > 750:
        player_x = 750
        player_vx = 0

    # Update Goomba position
    goomba_x += speed * direction
    if goomba_x > 750:
        direction = -1
    elif goomba_x < 0:
        direction = 1

    # Collision detection
    player_rect = pygame.Rect(int(player_x), int(player_y), 50, 50)
    goomba_rect = pygame.Rect(int(goomba_x), int(goomba_y), 50, 40)
    # Collision effect could be added here (e.g., flashing)

    # Render
    draw_background(screen)
    draw_goomba(screen, int(goomba_x), goomba_y)
    draw_player(screen, int(player_x), player_y)
    pygame.display.flip()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
