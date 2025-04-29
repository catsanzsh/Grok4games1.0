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

# Define map (0 = walkable, 1 = blocked)
map_data = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
for i in range(5, 10):
    map_data[5][i] = 1  # Horizontal wall

# Player data: {id: [x, y, color]}
players = {
    0: [100, 100, (255, 0, 0)],   # Player 0: Red
    1: [200, 100, (0, 0, 255)],   # Player 1: Blue
    2: [300, 100, (0, 255, 0)]    # Player 2: Green
}
player_speed = 5
player_size = 20

# Simulate peer inputs (for demo, controlled by different keys)
controls = {
    0: [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d],  # Player 0: WASD
    1: [pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l],  # Player 1: IJKL
    2: [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]  # Player 2: Arrows
}

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
    
    # Update X movement
    new_x = x + dx
    if is_walkable(new_x, y):
        x = new_x
    
    # Update Y movement
    new_y = y + dy
    if is_walkable(x, new_y):
        y = new_y
    
    players[player_id][0] = x
    players[player_id][1] = y

def render():
    screen.fill((0, 0, 0))  # Black background
    
    # Draw map
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            color = (0, 255, 0) if map_data[y][x] == 0 else (139, 69, 19)  # Green or Brown
            pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # Draw players
    for pid, (x, y, color) in players.items():
        pygame.draw.rect(screen, color, (x, y, player_size, player_size))
    
    pygame.display.flip()

def setup():
    pygame.display.set_caption("P2P RPG Game")

async def main():
    setup()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        
        # Update all players (simulating P2P updates)
        for pid in players:
            update_player(pid, keys)
        
        # Render the game state
        render()
        
        await asyncio.sleep(1.0 / FPS)  # Control frame rate

# Pyodide compatibility
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
