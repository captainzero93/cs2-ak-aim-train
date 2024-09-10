import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AK-47 Spray Pattern Trainer (CS2)")

# Colors
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# Font
font = pygame.font.Font(None, 36)

# AK-47 spray pattern
spray_pattern = [
    (0, 0), (-4, 7), (4, 19), (-3, 29), (-1, 31), (13, 31),
    (8, 28), (13, 21), (-17, 12), (-42, -3), (-21, 2),
    (12, 11), (-15, 7), (-26, -8), (-3, 4), (40, 1),
    (19, 7), (14, 10), (27, 0), (33, -10), (-21, -2),
    (7, 3), (-7, 9), (-8, 4), (19, -3), (5, 6),
    (-20, -1), (-33, -4), (-45, -21), (-14, 1)
]

# Convert the relative movements to absolute positions
for i in range(1, len(spray_pattern)):
    spray_pattern[i] = (
        spray_pattern[i-1][0] + spray_pattern[i][0],
        spray_pattern[i-1][1] + spray_pattern[i][1]
    )

# Find the bounding box of the pattern
min_x = min(x for x, y in spray_pattern)
max_x = max(x for x, y in spray_pattern)
min_y = min(y for x, y in spray_pattern)
max_y = max(y for x, y in spray_pattern)

# Calculate the scale factor to fit the pattern within 80% of the screen width and height
scale_x = (WIDTH * 0.8) / (max_x - min_x)
scale_y = (HEIGHT * 0.8) / (max_y - min_y)
scale = min(scale_x, scale_y)

# Calculate the offset to center the pattern
offset_x = (WIDTH - (max_x - min_x) * scale) / 2 - min_x * scale
offset_y = (HEIGHT - (max_y - min_y) * scale) / 2 - min_y * scale

# Apply scaling and offset to the pattern
spray_pattern = [(x * scale + offset_x, y * scale + offset_y) for x, y in spray_pattern]

user_path = []
score = 0
is_tracking = False
current_bullet_index = 0
last_bullet_time = 0
current_position = spray_pattern[0]
last_score_index = -1

clock = pygame.time.Clock()

# AK-47 fire rate is about 600 RPM, or 10 rounds per second
FIRE_RATE = 99  # ms between shots (as per the AutoHotkey script I referenced for the pattern)

def lerp(a, b, t):
    return a + (b - a) * t

running = True
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_tracking = True
            user_path = []
            score = 0
            current_bullet_index = 0
            last_bullet_time = current_time
            current_position = spray_pattern[0]
            last_score_index = -1
        elif event.type == pygame.MOUSEBUTTONUP:
            is_tracking = False

    if is_tracking:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        user_path.append((mouse_x, mouse_y))
        
        if current_time - last_bullet_time > FIRE_RATE and current_bullet_index < len(spray_pattern) - 1:
            current_bullet_index += 1
            last_bullet_time = current_time

        # Smooth movement between points
        t = min(1, (current_time - last_bullet_time) / FIRE_RATE)
        current_position = (
            lerp(spray_pattern[current_bullet_index-1][0], spray_pattern[current_bullet_index][0], t),
            lerp(spray_pattern[current_bullet_index-1][1], spray_pattern[current_bullet_index][1], t)
        )

        if len(user_path) > 1 and current_bullet_index > last_score_index:
            distance = math.sqrt((mouse_x - current_position[0])**2 + 
                                 (mouse_y - current_position[1])**2)
            if distance < 25:  # Hit detection radius
                score += 1
                last_score_index = current_bullet_index

    # Drawing
    screen.fill(BLACK)
    
    # Draw spray pattern (thicker line)
    if current_bullet_index > 0:
        pygame.draw.lines(screen, WHITE, False, spray_pattern[:current_bullet_index+1], 5)

    # Draw bullets as larger circles
    for point in spray_pattern[:current_bullet_index+1]:
        pygame.draw.circle(screen, WHITE, (int(point[0]), int(point[1])), 4)

    # Draw current position (larger)
    pygame.draw.circle(screen, PINK, (int(current_position[0]), int(current_position[1])), 8)

    # Draw user path (thicker)
    if len(user_path) > 1:
        pygame.draw.lines(screen, CYAN, False, user_path, 5)

    # Draw starting point indicator (larger)
    pygame.draw.circle(screen, RED, (int(spray_pattern[0][0]), int(spray_pattern[0][1])), 12, 3)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw "AK-47" text
    ak47_text = font.render("AK-47", True, WHITE)
    screen.blit(ak47_text, (WIDTH - ak47_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
