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
goomba_y = 360  # Adjusted so bottom aligns with ground at 400
direction = 1  # 1 for right, -1 for left
speed = 5

# Player variables
player_x = 400.0
player_y = 350.0
player_vx = 0.0
player_vy = 0.0
ACCELERATION = 1.0
FRICTION = 0.5
MAX_SPEED = 5.0
GRAVITY = 0.5
JUMP_SPEED = 10.0
ground_y = 400

# Tile size
TILE_SIZE = 16

def draw_cloud(screen, x, y):
    """Draw a simple cloud inspired by SMB3."""
    pygame.draw.ellipse(screen, WHITE, (x, y, 60, 40))
    pygame.draw.ellipse(screen, WHITE, (x + 20, y - 10, 50, 30))
    pygame.draw.ellipse(screen, WHITE, (x + 40, y, 60, 40))

def draw_background(screen):
    """Draw the background with sky, clouds, hills, and ground."""
    screen.fill(BLUE)  # Sky
    # Draw clouds
    draw_cloud(screen, 100, 50)
    draw_cloud(screen, 300, 100)
    draw_cloud(screen, 600, 70)
    # Draw hills
    pygame.draw.ellipse(screen, GREEN, (100, 350, 200, 50))
    pygame.draw.ellipse(screen, GREEN, (400, 350, 150, 40))
    # Draw ground tiles
    for y in range(400, 600, TILE_SIZE):
        color = GRASS if y == 400 else DIRT
        for x in range(0, 800, TILE_SIZE):
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

def draw_goomba(screen, x, y):
    """Draw a Goomba with SMB3 All-Stars style."""
    # Body (brown)
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
    # Mouth (frown-like)
    pygame.draw.ellipse(screen, BLACK, (x + 15, y + 25, 20, 10))
    # Feet
    pygame.draw.rect(screen, (139, 69, 19), (x + 5, y + 35, 15, 10))
    pygame.draw.rect(screen, (139, 69, 19), (x + 30, y + 35, 15, 10))

def draw_player(screen, x, y):
    """Draw Mario with SMB3 All-Stars style."""
    # Hat (red with brim)
    pygame.draw.rect(screen, RED, (x + 15, y, 20, 10))
    pygame.draw.rect(screen, RED, (x + 10, y + 5, 10, 5))  # Brim
    # Head
    pygame.draw.circle(screen, SKIN, (x + 25, y + 15), 10)
    # Eyes
    pygame.draw.circle(screen, BLACK, (x + 20, y + 15), 2)
    pygame.draw.circle(screen, BLACK, (x + 30, y + 15), 2)
    # Mustache
    pygame.draw.rect(screen, BLACK, (x + 20, y + 20, 10, 2))
    # Body (blue overalls)
    pygame.draw.rect(screen, BLUE, (x + 10, y + 25, 30, 25))
    # Shirt (red)
    pygame.draw.rect(screen, RED, (x + 15, y + 30, 20, 15))
    # Shoes
    pygame.draw.rect(screen, BLACK, (x + 10, y + 45, 10, 5))
    pygame.draw.rect(screen, BLACK, (x + 30, y + 45, 10, 5))

def setup():
    """Set up the game window."""
    pygame.display.set_caption("SMB3 All-Stars Replica")

def update_loop():
    """Update game state each frame."""
    global goomba_x, direction, player_x, player_y, player_vx, player_vy

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

    # Update horizontal position
    player_x += player_vx

    # Keep player within bounds
    if player_x < 0:
        player_x = 0
        player_vx = 0
    elif player_x > 750:
        player_x = 750
        player_vx = 0

    # Apply gravity
    player_vy += GRAVITY

    # Update vertical position
    player_y += player_vy

    # Check for ground collision
    if player_y + 50 > ground_y:
        player_y = ground_y - 50
        player_vy = 0
        on_ground = True
    else:
        on_ground = False

    # Handle jump
    if on_ground and keys[pygame.K_SPACE]:
        player_vy = -JUMP_SPEED

    # Update Goomba position
    goomba_x += speed * direction
    if goomba_x > 750:
        direction = -1
    elif goomba_x < 0:
        direction = 1

    # Define rects for collision
    player_rect = pygame.Rect(int(player_x), int(player_y), 50, 50)
    goomba_rect = pygame.Rect(int(goomba_x), int(goomba_y), 50, 40)

    # Collision detection
    if player_rect.colliderect(goomba_rect):
        if player_vy > 0 and player_y + 50 > goomba_y and player_y < goomba_y:
            # Player stomps Goomba
            direction = 0  # Stop Goomba
            player_vy = -JUMP_SPEED / 2  # Bounce off
        else:
            # Player gets hurt
            print("Ouch!")

    # Render
    draw_background(screen)
    draw_goomba(screen, int(goomba_x), goomba_y)
    draw_player(screen, int(player_x), int(player_y))
    pygame.display.flip()

async def main():
    """Main game loop for Pyodide compatibility."""
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
