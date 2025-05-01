import pygame
import sys
import platform
import asyncio
from pygame.math import Vector2

# Constants
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240
LEVEL_WIDTH = 1024
FPS = 60
GRAVITY = 0.4
JUMP_FORCE = -10
MAX_SPEED = 6
PLAYER_ACCEL = 0.5
FRICTION = 0.85

# NES Color Palette
COLORS = {
    "sky": (107, 140, 255),
    "ground": (94, 54, 21),
    "mario_red": (214, 40, 40),
    "mario_skin": (255, 206, 158),
    "pipe_green": (0, 168, 0),
    "flag_red": (193, 47, 43),
    "text_white": (255, 255, 255)
}

class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((16, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(32, 224))
        self.vel = Vector2(0, 0)
        self.state = "small"
        self.facing_right = True
        self.jump_timer = 0
        self.update_sprite()
    
    def update_sprite(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, COLORS["mario_red"], (4, 4, 8, 16))
        pygame.draw.circle(self.image, COLORS["mario_skin"], (8, 6), 4)
        leg_pos = 20 if pygame.time.get_ticks() % 300 < 150 else 22
        pygame.draw.rect(self.image, COLORS["mario_red"], (4, leg_pos, 4, 8))
        pygame.draw.rect(self.image, COLORS["mario_red"], (8, 20 if leg_pos == 22 else 22, 4, 8))
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def move(self, dt):
        keys = pygame.key.get_pressed()
        accel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_ACCEL * dt * 60
        self.vel.x += accel_x
        self.vel.x *= FRICTION
        self.facing_right = self.vel.x > 0 if abs(self.vel.x) > 0.1 else self.facing_right
        
        if keys[pygame.K_SPACE] and self.jump_timer == 0 and self.rect.bottom >= 224:
            self.vel.y = JUMP_FORCE
            self.jump_timer = 1
        elif self.jump_timer > 0 and self.jump_timer < 10 and keys[pygame.K_SPACE]:
            self.vel.y = JUMP_FORCE * (1 - self.jump_timer / 25)
            self.jump_timer += 1
        else:
            self.jump_timer = 0 if self.rect.bottom >= 224 else self.jump_timer
        
        self.vel.y += GRAVITY * dt * 60
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.rect.x = max(0, min(self.rect.x, LEVEL_WIDTH - 16))

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type="ground"):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        color = COLORS["ground"] if type == "ground" else COLORS["pipe_green"] if type == "pipe" else (150, 75, 0)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Flagpole:
    def __init__(self, x):
        self.image = pygame.Surface((16, 64))
        self.image.fill(COLORS["flag_red"])
        self.rect = self.image.get_rect(topleft=(x, 224 - 64))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario - 8 Worlds")
        self.clock = pygame.time.Clock()
        self.world = 1
        self.sublevel = 1
        self.score = 0
        self.coins = 0
        self.time = 400
        self.lives = 3
        self.camera_x = 0
        self.load_level()
        self.mario = Mario()

    def load_level(self):
        self.blocks = pygame.sprite.Group()
        # Ground
        for x in range(0, LEVEL_WIDTH, 16):
            self.blocks.add(Block(x, 224, "ground"))
        # Pipes
        for i in range(self.sublevel):
            pipe_x = 100 + i * 200
            pipe_height = 2 + i
            for y in range(224 - pipe_height * 16, 224, 16):
                self.blocks.add(Block(pipe_x, y, "pipe"))
        # Platforms
        platform_y = max(96, 160 - 16 * (self.world - 1))
        for i in range(self.world):
            platform_x_start = 200 + i * 300
            for x in range(platform_x_start, min(platform_x_start + 64, LEVEL_WIDTH - 16), 16):
                self.blocks.add(Block(x, platform_y, "brick"))
        # Flagpole
        self.flagpole = Flagpole(LEVEL_WIDTH - 32)

    def next_level(self):
        self.sublevel += 1
        if self.sublevel > 4:
            self.sublevel = 1
            self.world += 1
            if self.world > 8:
                print("Game Completed!")
                pygame.quit()
                sys.exit()
        self.load_level()
        self.mario.rect.midbottom = (32, 224)
        self.camera_x = 0

    def update_camera(self):
        if self.mario.rect.x - self.camera_x > SCREEN_WIDTH * 0.75:
            self.camera_x = self.mario.rect.x - SCREEN_WIDTH * 0.75
        self.camera_x = max(0, min(self.camera_x, LEVEL_WIDTH - SCREEN_WIDTH))

    def draw_blocks(self):
        for block in self.blocks:
            x_pos = block.rect.x - self.camera_x
            if x_pos > -16 and x_pos < SCREEN_WIDTH:
                self.screen.blit(block.image, (x_pos, block.rect.y))

    def draw_hud(self):
        font = pygame.font.Font(None, 16)
        texts = [
            f"MARIO {self.score:06d}",
            f"COINS x{self.coins:02d}",
            f"WORLD {self.world}-{self.sublevel}",
            f"TIME {int(self.time):03d}"
        ]
        for i, text in enumerate(texts):
            surf = font.render(text, True, COLORS["text_white"])
            self.screen.blit(surf, (8 + 80 * (i // 2), 8 + 12 * (i % 2)))

    def check_collisions(self):
        hits = pygame.sprite.spritecollide(self.mario, self.blocks, False)
        for block in hits:
            if self.mario.vel.y > 0:
                self.mario.rect.bottom = block.rect.top
                self.mario.vel.y = 0
                self.mario.jump_timer = 0
            elif self.mario.vel.y < 0:
                self.mario.rect.top = block.rect.bottom
                self.mario.vel.y = 0

    def update_loop(self):
        dt = 1.0 / FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        self.mario.move(dt)
        self.time -= dt
        self.update_camera()
        self.check_collisions()
        
        if self.mario.rect.right >= self.flagpole.rect.x:
            self.next_level()
        
        self.screen.fill(COLORS["sky"])
        self.draw_blocks()
        if self.flagpole.rect.x - self.camera_x > -16 and self.flagpole.rect.x - self.camera_x < SCREEN_WIDTH:
            self.screen.blit(self.flagpole.image, (self.flagpole.rect.x - self.camera_x, self.flagpole.rect.y))
        self.screen.blit(self.mario.image, (self.mario.rect.x - self.camera_x, self.mario.rect.y))
        self.draw_hud()
        pygame.display.update()

    def setup(self):
        self.load_level()
        self.mario = Mario()

async def main():
    game = Game()
    game.setup()
    while True:
        game.update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
