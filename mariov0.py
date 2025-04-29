import pygame
import asyncio
import platform

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 25, 18
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define isometric map (0 = walkable, 1 = blocked)
map_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

# Player data: {id: [x, y, color]}
players = {
    0: [100, 100, (255, 0, 0)],  # Player 0: Red
}
player_speed = 5
player_size = 20

# Enemy for combat demo
enemies = {
    0: [300, 200, (255, 255, 0)]  # Enemy 0: Yellow
}

# Controls for Player 0
controls = {
    0: [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]  # WASD
}

# Game state
game_state = "explore"  # "explore" or "combat"

def is_walkable(x, y, width=player_size, height=player_size):
    left_tile = x // TILE_SIZE
    right_tile = (x + width - 1) // TILE_SIZE
    top_tile = y // TILE_SIZE
    bottom_tile = (y + height - 1) // TILE_SIZE
    for ty in range(top_tile, bottom_tile + 1):
        for tx in range(left_tile, right_tile + 1):
            if (tx < 0 or tx >= MAP_WIDTH or ty < 0 or ty >= MAP_HEIGHT or 
                map_data[ty][tx] == 1):
                return False
    return True

def update_player(player_id, keys):
    global game_state
    x, y, _ = players[player_id]
    dx, dy = 0, 0
    up, down, left, right = controls[player_id]
    
    if keys[up]:
        dy -= player_speed
    if keys[down]:
        dy += player_speed
    if keys[left]:
        dx -= player_speed
    if keys[right]:
        dx += player_speed
    
    new_x = x + dx
    new_y = y + dy
    if is_walkable(new_x, new_y):
        x = new_x
        y = new_y
    
    players[player_id][0] = x
    players[player_id][1] = y
    
    # Check for combat trigger
    for eid, (ex, ey, _) in enemies.items():
        if abs(x - ex) < 50 and abs(y - ey) < 50:
            game_state = "combat"

def render_isometric_map():
    screen.fill((0, 0, 0))  # Black background
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            iso_x = (x - y) * (TILE_SIZE // 2) + WIDTH // 2
            iso_y = (x + y) * (TILE_SIZE // 4)
            color = (0, 255, 0) if map_data[y][x] == 0 else (139, 69, 19)
            pygame.draw.rect(screen, color, (iso_x, iso_y, TILE_SIZE, TILE_SIZE))

def render_combat():
    screen.fill((50, 50, 50))  # Gray background
    font = pygame.font.Font(None, 36)
    text = font.render("Combat Mode - Press SPACE to Exit", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

def render():
    if game_state == "explore":
        render_isometric_map()
        for pid, (x, y, color) in players.items():
            iso_x = (x // TILE_SIZE - y // TILE_SIZE) * (TILE_SIZE // 2) + WIDTH // 2
            iso_y = (x // TILE_SIZE + y // TILE_SIZE) * (TILE_SIZE // 4)
            pygame.draw.rect(screen, color, (iso_x, iso_y, player_size, player_size))
        for eid, (x, y, color) in enemies.items():
            iso_x = (x // TILE_SIZE - y // TILE_SIZE) * (TILE_SIZE // 2) + WIDTH // 2
            iso_y = (x // TILE_SIZE + y // TILE_SIZE) * (TILE_SIZE // 4)
            pygame.draw.rect(screen, color, (iso_x, iso_y, player_size, player_size))
    elif game_state == "combat":
        render_combat()
    pygame.display.flip()

def setup():
    pygame.display.set_caption("SMRPG-Inspired Pygame Game")

async def main():
    global game_state
    setup()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_state == "combat" and event.key == pygame.K_SPACE:
                game_state = "explore"
        
        keys = pygame.key.get_pressed()
        
        if game_state == "explore":
            for pid in players:
                update_player(pid, keys)
        
        render()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
