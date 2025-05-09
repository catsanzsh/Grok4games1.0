import pygame

# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Land - No PNG")

# Colors
BLUE = (0, 0, 255)    # Sky
GREEN = (0, 255, 0)   # Ground
RED = (255, 0, 0)     # Mario
BROWN = (139, 69, 19) # Platforms, Enemies
YELLOW = (255, 255, 0)# Coins, Goal

# Mario properties
mario_x, mario_y = 100, HEIGHT - 50
mario_width, mario_height = 20, 30
mario_vel_x, mario_vel_y = 0, 0
is_jumping = False

# Game objects
platforms = [
    {"x": 0, "y": HEIGHT - 20, "width": WIDTH, "height": 20},  # Ground
    {"x": 200, "y": 400, "width": 100, "height": 20},
    {"x": 400, "y": 300, "width": 100, "height": 20}
]
enemies = [{"x": 300, "y": HEIGHT - 40, "width": 20, "height": 20, "vel": 2}]
coins = [{"x": 250, "y": 350, "radius": 10}, {"x": 450, "y": 250, "radius": 10}]
goal = {"x": 700, "y": HEIGHT - 50, "width": 20, "height": 50}
score = 0

# Font for score
font = pygame.font.Font(None, 36)

# Clock for 60 FPS
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                mario_vel_x = -5
            elif event.key == pygame.K_RIGHT:
                mario_vel_x = 5
            elif event.key == pygame.K_SPACE and not is_jumping:
                mario_vel_y = -10
                is_jumping = True
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                mario_vel_x = 0

    # Update Mario
    mario_x += mario_vel_x
    mario_y += mario_vel_y
    if is_jumping:
        mario_vel_y += 0.3  # Gravity
    if mario_x < 0:
        mario_x = 0
    elif mario_x > WIDTH - mario_width:
        mario_x = WIDTH - mario_width

    # Platform collisions
    for p in platforms:
        if (mario_x + mario_width > p["x"] and mario_x < p["x"] + p["width"] and
            mario_y + mario_height > p["y"] and mario_y < p["y"] + p["height"]):
            if mario_vel_y > 0:
                mario_y = p["y"] - mario_height
                mario_vel_y = 0
                is_jumping = False

    # Enemy movement and collisions
    for e in enemies[:]:
        e["x"] += e["vel"]
        if e["x"] <= 0 or e["x"] >= WIDTH - e["width"]:
            e["vel"] *= -1
        if (mario_x + mario_width > e["x"] and mario_x < e["x"] + e["width"] and
            mario_y + mario_height > e["y"] and mario_y < e["y"] + e["height"]):
            if mario_vel_y > 0 and mario_y + mario_height - e["y"] < 10:
                enemies.remove(e)  # Defeat enemy
                mario_vel_y = -5   # Bounce
            else:
                running = False    # Game over

    # Coin collection
    for c in coins[:]:
        if (mario_x + mario_width > c["x"] - c["radius"] and mario_x < c["x"] + c["radius"] and
            mario_y + mario_height > c["y"] - c["radius"] and mario_y < c["y"] + c["radius"]):
            coins.remove(c)
            score += 1

    # Goal check
    if (mario_x + mario_width > goal["x"] and mario_x < goal["x"] + goal["width"] and
        mario_y + mario_height > goal["y"] and mario_y < goal["y"] + goal["height"]):
        print("Level Complete!")
        running = False

    # Drawing
    screen.fill(BLUE)  # Sky
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 20, WIDTH, 20))  # Ground
    for p in platforms:
        pygame.draw.rect(screen, BROWN, (p["x"], p["y"], p["width"], p["height"]))
    for e in enemies:
        pygame.draw.rect(screen, BROWN, (e["x"], e["y"], e["width"], e["height"]))
    for c in coins:
        pygame.draw.circle(screen, YELLOW, (int(c["x"]), int(c["y"])), c["radius"])
    pygame.draw.rect(screen, YELLOW, (goal["x"], goal["y"], goal["width"], goal["height"]))
    pygame.draw.rect(screen, RED, (mario_x, mario_y, mario_width, mario_height))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Update display and maintain 60 FPS
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
