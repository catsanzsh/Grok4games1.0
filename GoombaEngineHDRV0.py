import pygame
import asyncio
import platform
import sys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
FPS = 60
clock = pygame.time.Clock()  # Added to enforce 60 fps

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRASS = (0, 255, 0)
DIRT = (139, 69, 19)
SKIN = (255, 224, 189)
YELLOW = (255, 255, 0)  # For question blocks

# Goomba variables
goomba_x = 375
goomba_y = 360
direction = 1
speed = 0.83  # Adjusted from video observation

# Player variables
player_x = 400.0
player_y = 350.0
player_vx = 0.0
player_vy = 0.0
ACCELERATION = 1.0
FRICTION = 0.5
MAX_SPEED = 1.33  # Adjusted from video observation
GRAVITY = 0.33     # Adjusted from video observation
JUMP_SPEED = 10.0
ground_y = 400

# Tile size
TILE_SIZE = 16

# Level elements (example from World 1-1 observation)
blocks = [
    {"type": "question", "x": 300, "y": 300, "width": 40, "height": 40}
]

def draw_cloud(screen, x, y):
    pygame.draw.ellipse(screen, WHITE, (x, y, 60, 40))
    pygame.draw.ellipse(screen, WHITE, (x + 20, y - 10, 50, 30))
    pygame.draw.ellipse(screen, WHITE, (x + 40, y, 60, 40))

def draw_background(screen):
    screen.fill(BLUE)
    draw_cloud(screen, 100, 50)
    draw_cloud(screen, 300, 100)
    draw_cloud(screen, 600, 70)
    pygame.draw.ellipse(screen, GREEN, (100, 350, 200, 50))
    pygame.draw.ellipse(screen, GREEN, (400, 350, 150, 40))
    for y in range(400, 600, TILE_SIZE):
        color = GRASS if y == 400 else DIRT
        for x in range(0, 800, TILE_SIZE):
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

def draw_goomba(screen, x, y):
    pygame.draw.ellipse(screen, (139, 69, 19), (x, y, 50, 40))
    pygame.draw.ellipse(screen, WHITE, (x + 10, y + 10, 10, 15))
    pygame.draw.ellipse(screen, WHITE, (x + 30, y + 10, 10, 15))
    pygame.draw.ellipse(screen, BLACK, (x + 12, y + 12, 5, 5))
    pygame.draw.ellipse(screen, BLACK, (x + 32, y + 12, 5, 5))
    pygame.draw.rect(screen, BLACK, (x + 10, y + 5, 10, 5))
    pygame.draw.rect(screen, BLACK, (x + 30, y + 5, 10, 5))
    pygame.draw.ellipse(screen, BLACK, (x + 15, y + 25, 20, 10))
    pygame.draw.rect(screen, (139, 69, 19), (x + 5, y + 35, 15, 10))
    pygame.draw.rect(screen, (139, 69, 19), (x + 30, y + 35, 15, 10))

def draw_player(screen, x, y):
    pygame.draw.rect(screen, RED, (x + 15, y, 20, 10))
    pygame.draw.rect(screen, RED, (x + 10, y + 5, 10, 5))
    pygame.draw.circle(screen, SKIN, (x + 25, y + 15), 10)
    pygame.draw.circle(screen, BLACK, (x + 20, y + 15), 2)
    pygame.draw.circle(screen, BLACK, (x + 30, y + 15), 2)
    pygame.draw.rect(screen, BLACK, (x + 20, y + 20, 10, 2))
    pygame.draw.rect(screen, BLUE, (x + 10, y + 25, 30, 25))
    pygame.draw.rect(screen, RED, (x + 15, y + 30, 20, 15))
    pygame.draw.rect(screen, BLACK, (x + 10, y + 45, 10, 5))
    pygame.draw.rect(screen, BLACK, (x + 30, y + 45, 10, 5))

def draw_block(screen, block):
    if block["type"] == "question":
        pygame.draw.rect(screen, YELLOW, (block["x"], block["y"], block["width"], block["height"]))
        pygame.draw.rect(screen, BLACK, (block["x"], block["y"], block["width"], block["height"]), 2)  # Border

def setup():
    pygame.display.set_caption("SMB3 All-Stars Replica Enhanced")

def update_loop():
    global goomba_x, direction, player_x, player_y, player_vx, player_vy

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_vx -= ACCELERATION
    if keys[pygame.K_RIGHT]:
        player_vx += ACCELERATION

    if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        if player_vx > 0:
            player_vx -= FRICTION
            if player_vx < 0:
                player_vx = 0
        elif player_vx < 0:
            player_vx += FRICTION
            if player_vx > 0:
                player_vx = 0

    player_vx = max(-MAX_SPEED, min(MAX_SPEED, player_vx))
    player_x += player_vx

    if player_x < 0:
        player_x = 0
        player_vx = 0
    elif player_x > 750:
        player_x = 750
        player_vx = 0

    player_vy += GRAVITY
    player_y += player_vy

    # Collision with ground
    if player_y + 50 > ground_y:
        player_y = ground_y - 50
        player_vy = 0
        on_ground = True
    else:
        on_ground = False

    # Collision with blocks
    player_rect = pygame.Rect(int(player_x), int(player_y), 50, 50)
    for block in blocks:
        block_rect = pygame.Rect(block["x"], block["y"], block["width"], block["height"])
        if player_rect.colliderect(block_rect):
            if player_vy > 0 and player_y + 50 > block["y"] and player_y < block["y"]:
                player_y = block["y"] - 50
                player_vy = 0
                on_ground = True
            elif player_vy < 0 and player_y < block["y"] + block["height"]:
                player_y = block["y"] + block["height"]
                player_vy = 0

    if on_ground and keys[pygame.K_SPACE]:
        player_vy = -JUMP_SPEED

    goomba_x += speed * direction
    if goomba_x > 750:
        direction = -1
    elif goomba_x < 0:
        direction = 1

    goomba_rect = pygame.Rect(int(goomba_x), int(goomba_y), 50, 40)
    if player_rect.colliderect(goomba_rect):
        if player_vy > 0 and player_y + 50 > goomba_y and player_y < goomba_y:
            direction = 0
            player_vy = -JUMP_SPEED / 2
        else:
            print("Ouch!")

    draw_background(screen)
    for block in blocks:
        draw_block(screen, block)
    draw_goomba(screen, int(goomba_x), goomba_y)
    draw_player(screen, int(player_x), int(player_y))
    pygame.display.flip()
    clock.tick(FPS)  # Enforce 60 fps

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
