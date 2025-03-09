import pygame
import random
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Screen settings (Nokia 3310 exact scaled dimensions)
WIDTH = 252  # 84 pixels wide x 3 scale
HEIGHT = 144  # 48 pixels tall x 3 scale
GRID_SIZE = 3  # Nokia pixels scaled up
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nokia Snake II")

# Colors (Nokia monochrome green-on-black)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)  # Nokia's greenish tint
WHITE = (255, 255, 255)  # For text

# Snake and food
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_dir = (1, 0)
food = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
score = 0

# Timing
clock = pygame.time.Clock()
SPEED = 8

# Generate raw audio data for Nokia-like beeps
SAMPLE_RATE = 22050
def generate_square_wave(frequency, duration):
    samples = int(SAMPLE_RATE * duration)
    period = int(SAMPLE_RATE / frequency)
    amplitude = 32767
    buffer = bytearray(samples * 2)
    for i in range(samples):
        value = amplitude if (i % period) < (period // 2) else -amplitude
        buffer[i*2:i*2+2] = int(value).to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer)

# Sound effects (only beeps, no music)
eat_sound = generate_square_wave(880, 0.05)  # High beep for eating
move_sound = generate_square_wave(440, 0.02)  # Quick beep for movement
death_sound = generate_square_wave(220, 0.2)  # Low beep for death

# Game states
MENU = 0
GAME = 1
CREDITS = 2
state = MENU
menu_selection = 0  # 0 = Start, 1 = Credits
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == MENU:
                if event.key == pygame.K_UP:
                    menu_selection = 0
                elif event.key == pygame.K_DOWN:
                    menu_selection = 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if menu_selection == 0:
                        state = GAME
                        snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                        snake_dir = (1, 0)
                        food = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                        score = 0
                        game_over = False
                    else:
                        state = CREDITS
            elif state == GAME and not game_over:
                if event.key == pygame.K_UP and snake_dir != (0, 1):
                    snake_dir = (0, -1)
                elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                    snake_dir = (0, 1)
                elif event.key == pygame.K_LEFT and snake_dir != (1, 0):
                    snake_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                    snake_dir = (1, 0)
            elif state == GAME and game_over and event.key == pygame.K_SPACE:
                state = MENU
            elif state == CREDITS and event.key == pygame.K_SPACE:
                state = MENU

    if state == MENU:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 24)
        title = font.render("Snake II", True, GREEN)
        start = font.render("> Start Game" if menu_selection == 0 else "  Start Game", True, GREEN)
        credits = font.render("> Credits" if menu_selection == 1 else "  Credits", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2))
        screen.blit(credits, (WIDTH//2 - credits.get_width()//2, HEIGHT//2 + 30))

    elif state == GAME:
        if not game_over:
            head_x, head_y = snake[0]
            new_head = (head_x + snake_dir[0], head_y + snake_dir[1])
            
            # Wall collision (Nokia borders)
            if (new_head[0] <= 0 or new_head[0] >= GRID_WIDTH-1 or 
                new_head[1] <= 0 or new_head[1] >= GRID_HEIGHT-1):
                game_over = True
                death_sound.play()
            elif new_head in snake:
                game_over = True
                death_sound.play()
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    eat_sound.play()
                    food = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                else:
                    snake.pop()
                    move_sound.play()

        # Draw game
        screen.fill(BLACK)
        # Draw border
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT), GRID_SIZE)
        # Draw snake and food with full grid cells for original look
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, GREEN, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Score
        font = pygame.font.Font(None, 18)
        score_text = font.render(f"{score}", True, GREEN)
        screen.blit(score_text, (GRID_SIZE + 5, GRID_SIZE + 5))

        if game_over:
            font = pygame.font.Font(None, 24)
            text = font.render("Game Over", True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2 - 10))
            text = font.render(f"Score: {score}", True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 10))
            text = font.render("SPACE to Menu", True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 30))

    elif state == CREDITS:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 18)
        lines = [
            "THANKS NOKIA",
            "(C) Team Flames",
            "(C) 2025",
            "Powered by Grok",
            "2025 (C) xAI",
            "",
            "SPACE to Menu"
        ]
        for i, line in enumerate(lines):
            text = font.render(line, True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//4 + i * 20))

    pygame.display.flip()
    clock.tick(SPEED)

pygame.quit()
