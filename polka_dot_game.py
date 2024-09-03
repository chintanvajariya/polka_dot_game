# power ups
# score ✓
# start screen
# game over screen ✓
# high score ✓
# sound effects
# background music
# pause screen
# help screen
# difficulty system

import pygame
import random
import math
import os

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Polka Dot Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

player_size = 10
player_x = screen_width // 2
player_y = screen_height // 2
player_active = False

# minimum of 10 dots on the screen at all times
MIN_DOTS = 12

ADD_DOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_DOT_EVENT, random.randint(400, 2000))

# create a dot (either randomly or pointed at the player)
def create_dot(player_x, player_y, target_player=True):
    size = random.randint(5, 70)
    speed = random.uniform(1, 5.5)

    # randomly start on one of the screen edges
    start_edge = random.choice(['top', 'bottom', 'left', 'right'])
    if start_edge == 'top':
        start_x = random.randint(0, screen_width)
        start_y = -size 
    elif start_edge == 'bottom':
        start_x = random.randint(0, screen_width)
        start_y = screen_height + size 
    elif start_edge == 'left':
        start_x = -size 
        start_y = random.randint(0, screen_height)
    else:  # right
        start_x = screen_width + size
        start_y = random.randint(0, screen_height)

    if target_player:
        direction_x = player_x - start_x
        direction_y = player_y - start_y
    else:
        direction_x = random.uniform(-1, 1)
        direction_y = random.uniform(-1, 1)

    magnitude = math.sqrt(direction_x**2 + direction_y**2)
    direction = (direction_x / magnitude, direction_y / magnitude)

    color = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 128)
    
    return [start_x, start_y, size, speed, direction, color]

def draw_player(x, y, size):
    pygame.draw.circle(screen, WHITE, (x, y), size)

# make dots appear
def draw_dots(dots):
    for dot in dots:
        s = pygame.Surface((dot[2]*2, dot[2]*2), pygame.SRCALPHA)
        pygame.draw.circle(s, dot[5], (dot[2], dot[2]), dot[2])
        screen.blit(s, (dot[0]-dot[2], dot[1]-dot[2]))

def move_dots(dots):
    for dot in dots:
        dot[0] += dot[3] * dot[4][0]
        dot[1] += dot[3] * dot[4][1]

        if (dot[0] < -dot[2] or dot[0] > screen_width + dot[2] or
                dot[1] < -dot[2] or dot[1] > screen_height + dot[2]):
            dots.remove(dot)

def check_collision(dot1, dot2):
    distance = math.sqrt((dot1[0] - dot2[0])**2 + (dot1[1] - dot2[1])**2)
    return distance < (dot1[2] + dot2[2])

# display the score
def display_score(score, high_score):
    text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(text, (10, 10))
    screen.blit(high_score_text, (10, 50))

# load high score from file
def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            return int(file.read())
    return 0

# save high score to file
def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

# post-death screen
def game_over_overlay(score):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    game_over_text = game_over_font.render("Game Over", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2 - 100))
    screen.blit(score_text, (screen_width // 2 - 100, screen_height // 2))

    replay_text = font.render("Replay?", True, WHITE)
    replay_button = pygame.Rect(screen_width // 2 - 60, screen_height // 2 + 70, 120, 50)
    pygame.draw.rect(screen, GRAY, replay_button)
    screen.blit(replay_text, (screen_width // 2 - 45, screen_height // 2 + 80))

    pygame.display.flip()
    return replay_button

# load the current high score
high_score = load_high_score()

dots = [create_dot(player_x, player_y, target_player=False) for _ in range(15)]

# game loop
running = True
score = 0 
game_over = False
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == ADD_DOT_EVENT:
            dots.append(create_dot(player_x, player_y))
            pygame.time.set_timer(ADD_DOT_EVENT, random.randint(400, 2000))
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if replay_button.collidepoint(mouse_pos):
                # restart
                player_size = 10
                player_x = screen_width // 2
                player_y = screen_height // 2
                player_active = False
                score = 0
                game_over = False
                dots = [create_dot(player_x, player_y, target_player=False) for _ in range(15)]
    
    if not game_over:
        while len(dots) < MIN_DOTS:
            dots.append(create_dot(player_x, player_y, target_player=True))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if not player_active:
            if math.sqrt((player_x - mouse_x) ** 2 + (player_y - mouse_y) ** 2) < player_size:
                player_active = True

        if player_active:
            player_x, player_y = mouse_x, mouse_y

        move_dots(dots)
        draw_dots(dots)
        
        for dot in dots[:]:
            if check_collision([player_x, player_y, player_size], dot):
                if dot[2] < player_size:
                    player_size += 1

                    score += 1
                    dots.remove(dot)
                else:
                    game_over = True

        if score > high_score:
            high_score = score

        draw_player(player_x, player_y, player_size)
        
        display_score(score, high_score)
    
    else:
        replay_button = game_over_overlay(score)
    
    pygame.display.flip()
    clock.tick(30)

save_high_score(high_score)

pygame.quit()