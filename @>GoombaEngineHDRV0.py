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

# Goomba variables
goomba_x = 375
goomba_y = 350
direction = 1  # 1 for right, -1 for left
speed = 5

# Player variables
player_x = 400
player_y = 350
player_speed = 7
player_color = RED

def draw_background(screen):
    screen.fill(BLUE)  # Sky
    pygame.draw.rect(screen, GREEN, (0, 400, 800, 200))  # Ground

def draw_goomba(screen, x, y):
    # Body
    pygame.draw.ellipse(screen, (139, 69, 19), (x, y, 50, 40))  # Brown color
    # Eyes
    pygame.draw.ellipse(screen, WHITE, (x + 10, y + 10, 10, 15))
    pygame.draw.ellipse(screen, WHITE, (x + 30, y + 10, 10, 15))
    # Pupils
    pygame.draw.ellipse(screen, BLACK, (x + 12, y + 12, 5, 5))
    pygame.draw.ellipse(screen, BLACK, (x + 32, y + 12, 5, 5))
    # Feet
    pygame.draw.rect(screen, (139, 69, 19), (x + 5, y + 35, 15, 10))
    pygame.draw.rect(screen, (139, 69, 19), (x + 30, y + 35, 15, 10))

def draw_player(screen, x, y, color):
    pygame.draw.rect(screen, color, (x, y, 50, 50))

def setup():
    pygame.display.set_caption("GOOMBA ENGINE 1.0A")

def update_loop():
    global goomba_x, direction, player_x, player_color
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Keep player within bounds
    if player_x < 0:
        player_x = 0
    elif player_x > 750:
        player_x = 750

    # Update Goomba position
    goomba_x += speed * direction
    if goomba_x > 750:
        direction = -1
    elif goomba_x < 0:
        direction = 1

    # Collision detection
    player_rect = pygame.Rect(player_x, player_y, 50, 50)
    goomba_rect = pygame.Rect(goomba_x, goomba_y, 50, 40)
    if player_rect.colliderect(goomba_rect):
        player_color = WHITE
    else:
        player_color = RED

    # Render
    draw_background(screen)
    draw_goomba(screen, goomba_x, goomba_y)
    draw_player(screen, player_x, player_y, player_color)
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
