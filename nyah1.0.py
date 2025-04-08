import pygame
import sys
import math
import random

# === CONFIG ===
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240  # PS1-style low res
FPS = 30  # Retro framerate
TILE_SIZE = 16  # Chunky tiles

# === INIT ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()
pygame.display.set_caption("Ratchet & Clank: It's About Nyah - Konami 2.5D Engine")

# === COLORS ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)  # Ratchet color
NEON = (128, 0, 255)   # Outline pop
GRAY = (60, 60, 60)    # Foreground tiles
DARK_GRAY = (40, 40, 40)  # Midground tiles
YELLOW = (255, 255, 0) # Projectiles
RED = (255, 60, 60)    # Accents
BG_COLOR = (20, 20, 50)  # Dark blue backdrop

# === FONT ===
font = pygame.font.Font(None, 24)  # Simple PS1-style font

# === LEVEL DATA ===
FOREGROUND_MAP = [
    "                            ",
    "                            ",
    "                            ",
    "         ===               ",
    "       =======             ",
    "     ============          ",
    "   =================       ",
    "==========================="
]

MIDGROUND_MAP = [
    "                            ",
    "                            ",
    "       ----                ",
    "     --------              ",
    "   ------------            ",
    "                            ",
    "                            ",
    "                            "
]

# === CLASSES ===
class Tile:
    def __init__(self, x, y, layer="foreground"):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.layer = layer

    def draw(self, offset_x, parallax_factor=1.0):
        color = GRAY if self.layer == "foreground" else DARK_GRAY
        adjusted_x = self.rect.x - (offset_x * parallax_factor)
        pygame.draw.rect(screen, color, (adjusted_x, self.rect.y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, BLACK, (adjusted_x, self.rect.y, TILE_SIZE, TILE_SIZE), 1)

class Ratchet:
    def __init__(self):
        self.x = 50
        self.y = 0  # Start at the top
        self.vx = 1.5
        self.w = 12
        self.h = 16
        self.facing = 1
        self.depth = 0
        self.projectiles = []
        self.cooldown = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, tiles):
        self.x += self.vx
        self.collide(self.vx, 0, tiles)
        if self.x < 0 or self.x > SCREEN_WIDTH * 2:
            self.vx = -self.vx
            self.facing = -self.facing

        if self.cooldown == 0:
            self.projectiles.append(Projectile(self.x + self.w * self.facing, self.y + self.h // 2, self.facing, self.depth))
            self.cooldown = 30

        if self.cooldown > 0:
            self.cooldown -= 1

        for proj in self.projectiles[:]:
            proj.update()
            if proj.dead:
                self.projectiles.remove(proj)

    def collide(self, vx, vy, tiles):
        rect = self.rect()
        relevant_tiles = [t for t in tiles if t.layer == "foreground"]
        for tile in relevant_tiles:
            if rect.colliderect(tile.rect):
                if vy > 0:
                    self.y = tile.rect.top - self.h
                if vx > 0:
                    self.x = tile.rect.left - self.w
                    self.vx = -self.vx
                    self.facing = -self.facing
                elif vx < 0:
                    self.x = tile.rect.right
                    self.vx = -self.vx
                    self.facing = -self.facing
        highest_tile_y = min([t.rect.top for t in relevant_tiles] + [SCREEN_HEIGHT])
        if self.y + self.h > highest_tile_y:
            self.y = highest_tile_y - self.h

    def draw(self, offset_x):
        jitter_x = random.randint(-1, 1)
        jitter_y = random.randint(-1, 1)
        x = self.x - offset_x
        pygame.draw.rect(screen, BLUE, (x + jitter_x, self.y + jitter_y, self.w, self.h))
        pygame.draw.rect(screen, NEON, (x + jitter_x, self.y + jitter_y, self.w, self.h), 1)
        for proj in self.projectiles:
            proj.draw(offset_x)

class Projectile:
    def __init__(self, x, y, direction, depth):
        self.x = x
        self.y = y
        self.vx = 4 * direction
        self.depth = depth
        self.dead = False

    def update(self):
        self.x += self.vx
        if self.x > SCREEN_WIDTH * 2 or self.x < -SCREEN_WIDTH:
            self.dead = True

    def draw(self, offset_x):
        scale = 1.0 if self.depth == 0 else 0.8
        x = self.x - offset_x if self.depth == 0 else self.x - (offset_x * 0.5)
        pygame.draw.rect(screen, YELLOW, (x, self.y, int(4 * scale), int(2 * scale)))
        pygame.draw.rect(screen, RED, (x, self.y, int(4 * scale), int(2 * scale)), 1)

# === GAME FUNCTIONS ===
def build_level():
    tiles = []
    for row_idx, row in enumerate(FOREGROUND_MAP):
        for col_idx, char in enumerate(row):
            if char == "=":
                tiles.append(Tile(col_idx * TILE_SIZE, row_idx * TILE_SIZE, "foreground"))
    for row_idx, row in enumerate(MIDGROUND_MAP):
        for col_idx, char in enumerate(row):
            if char == "-":
                tiles.append(Tile(col_idx * TILE_SIZE, row_idx * TILE_SIZE, "midground"))
    return tiles

def main_menu():
    selected = 0  # 0 = Start, 1 = Exit
    options = ["Start Game", "Exit"]
    while True:
        screen.fill(BLACK)
        logo_text = font.render("Flames Team Presents", True, WHITE)
        screen.blit(logo_text, (SCREEN_WIDTH // 2 - logo_text.get_width() // 2, 50))
        title_text = font.render("Ratchet & Clank: Nyah", True, NEON)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 150 + i * 30))

        for _ in range(50):
            x, y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
            pygame.draw.rect(screen, (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)), (x, y, 1, 1))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
                    selected = min(1, selected + 1)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        return True  # Start game
                    else:
                        return False  # Exit

def loading_screen():
    frames = 0
    while frames < 60:  # ~2 seconds at 30 FPS
        screen.fill(BLACK)
        loading_text = font.render("Loading...", True, WHITE)
        screen.blit(loading_text, (SCREEN_WIDTH // 2 - loading_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        angle = frames * 6
        x = SCREEN_WIDTH // 2 + math.cos(math.radians(angle)) * 20
        y = SCREEN_HEIGHT // 2 + math.sin(math.radians(angle)) * 20
        pygame.draw.circle(screen, NEON, (int(x), int(y)), 5)

        for _ in range(30):
            x, y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
            pygame.draw.rect(screen, (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)), (x, y, 1, 1))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():  # Handle events during loading
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        frames += 1

def game_loop(tiles, ratchet):
    camera_x = 0
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ratchet.update(tiles)
        camera_x = max(0, ratchet.x - SCREEN_WIDTH // 2)

        for tile in tiles:
            parallax = 1.0 if tile.layer == "foreground" else 0.5
            tile.draw(camera_x, parallax)
        ratchet.draw(camera_x)

        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(screen, (10, 10, 20), (0, y), (SCREEN_WIDTH, y), 1)

        pygame.display.flip()
    return False

# === MAIN PROGRAM ===
running = True
while running:
    if main_menu():
        loading_screen()
        tiles = build_level()
        ratchet = Ratchet()
        running = game_loop(tiles, ratchet)
    else:
        running = False

pygame.quit()
sys.exit()
