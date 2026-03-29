import pygame
import sys
import os
import random

# --- НАСТРОЙКИ ---
WIDTH, HEIGHT = 900, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PINGPONG")
clock = pygame.time.Clock()

# --- ЦВЕТА ---
WHITE = (240, 240, 240)
YELLOW = (255, 220, 0)
BG = (20, 20, 30)
ACCENT = (0, 200, 255)
FLASH = (100, 255, 100)
DARK = (10, 10, 15)

# --- ШРИФТЫ ---
font = pygame.font.SysFont('Arial', 28)
big_font = pygame.font.SysFont('Arial', 70)

# --- ОБЪЕКТЫ ---
def reset_game():
    global paddle1, paddle2, ball, ball_dx, ball_dy, p1_score, p2_score
    paddle1 = pygame.Rect(40, HEIGHT//2 - 60, 20, 120)
    paddle2 = pygame.Rect(WIDTH - 60, HEIGHT//2 - 60, 20, 120)
    ball = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
    ball_dx = random.choice([-5, 5])
    ball_dy = random.choice([-3, 3])
    p1_score = 0
    p2_score = 0

reset_game()

# --- АНИМАЦИИ ---
flash1 = 0
flash2 = 0
particles = []

# --- РЕКОРДЫ ---
record_file = "pong_record.txt"
if os.path.exists(record_file):
    with open(record_file, "r") as f:
        data = f.read().split()
        if len(data) == 2:
            p1_record, p2_record = map(int, data)
        else:
            p1_record = 0
            p2_record = 0
else:
    p1_record = 0
    p2_record = 0

# --- СОСТОЯНИЯ ---
menu = True
paused = False
mode = None

# --- КНОПКИ ---
btn_ai = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
btn_pvp = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60)

btn_resume = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 60)
btn_restart = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 40, 300, 60)
btn_menu = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 60)

# --- ЧАСТИЦЫ ---
def spawn_particles(x, y):
    for _ in range(10):
        particles.append([[x, y], [random.uniform(-3, 3), random.uniform(-3, 3)], random.randint(4, 7)])

# --- ГЛАВНЫЙ ЦИКЛ ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open(record_file, "w") as f:
                f.write(f"{p1_record} {p2_record}")
            pygame.quit()
            sys.exit()

        if menu and event.type == pygame.MOUSEBUTTONDOWN:
            if btn_ai.collidepoint(event.pos):
                mode = "ai"
                reset_game()
                menu = False
            if btn_pvp.collidepoint(event.pos):
                mode = "pvp"
                reset_game()
                menu = False

        if not menu and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused

        if paused and event.type == pygame.MOUSEBUTTONDOWN:
            if btn_resume.collidepoint(event.pos):
                paused = False
            if btn_restart.collidepoint(event.pos):
                reset_game()
                paused = False
            if btn_menu.collidepoint(event.pos):
                menu = True
                paused = False

    screen.fill(BG)

    if menu:
        title = big_font.render("PINGPONG", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        pygame.draw.rect(screen, ACCENT, btn_ai, border_radius=10)
        pygame.draw.rect(screen, ACCENT, btn_pvp, border_radius=10)

        screen.blit(font.render("Play vs AI", True, BG), (btn_ai.centerx - 80, btn_ai.centery - 15))
        screen.blit(font.render("Player vs Player", True, BG), (btn_pvp.centerx - 110, btn_pvp.centery - 15))

    else:
        if not paused:
            # --- ДВИЖЕНИЕ ---
            ball.x += ball_dx
            ball.y += ball_dy

            keys = pygame.key.get_pressed()

            # ЛЕВЫЙ
            if keys[pygame.K_w] and paddle1.top > 0:
                paddle1.y -= 7
            if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
                paddle1.y += 7

            # ПРАВЫЙ
            if mode == "pvp":
                if keys[pygame.K_UP] and paddle2.top > 0:
                    paddle2.y -= 7
                if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
                    paddle2.y += 7
            else:
                if paddle2.centery < ball.centery:
                    paddle2.y += 5
                elif paddle2.centery > ball.centery:
                    paddle2.y -= 5

            # СТОЛКНОВЕНИЯ
            if ball.colliderect(paddle1):
                ball_dx *= -1
                ball.left = paddle1.right
                flash1 = 8
                spawn_particles(ball.centerx, ball.centery)
                p1_score += 1
                if p1_score > p1_record:
                    p1_record = p1_score

            if ball.colliderect(paddle2):
                ball_dx *= -1
                ball.right = paddle2.left
                flash2 = 8
                spawn_particles(ball.centerx, ball.centery)
                p2_score += 1
                if p2_score > p2_record:
                    p2_record = p2_score

            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_dy *= -1

            if ball.left <= 0 or ball.right >= WIDTH:
                ball_dx *= -1

        # --- АНИМАЦИИ ---
        color1 = FLASH if flash1 > 0 else WHITE
        color2 = FLASH if flash2 > 0 else WHITE
        flash1 = max(0, flash1 - 1)
        flash2 = max(0, flash2 - 1)

        for p in particles[:]:
            p[0][0] += p[1][0]
            p[0][1] += p[1][1]
            p[2] -= 0.2
            pygame.draw.circle(screen, YELLOW, (int(p[0][0]), int(p[0][1])), int(p[2]))
            if p[2] <= 0:
                particles.remove(p)

        # --- ОТРИСОВКА ---
        pygame.draw.rect(screen, color1, paddle1, border_radius=6)
        pygame.draw.rect(screen, color2, paddle2, border_radius=6)
        pygame.draw.ellipse(screen, WHITE, ball)

        for y in range(0, HEIGHT, 30):
            pygame.draw.rect(screen, (80, 80, 80), (WIDTH//2 - 2, y, 4, 15))

        score = font.render(f"{p1_score} : {p2_score}", True, WHITE)
        screen.blit(score, (WIDTH//2 - score.get_width()//2, 20))

        # --- ПАУЗА ---
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(DARK)
            screen.blit(overlay, (0, 0))

            title = big_font.render("PAUSE", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

            pygame.draw.rect(screen, ACCENT, btn_resume, border_radius=10)
            pygame.draw.rect(screen, ACCENT, btn_restart, border_radius=10)
            pygame.draw.rect(screen, ACCENT, btn_menu, border_radius=10)

            screen.blit(font.render("Resume", True, BG), (btn_resume.centerx - 50, btn_resume.centery - 15))
            screen.blit(font.render("Restart", True, BG), (btn_restart.centerx - 50, btn_restart.centery - 15))
            screen.blit(font.render("Menu", True, BG), (btn_menu.centerx - 40, btn_menu.centery - 15))

    pygame.display.flip()
    clock.tick(60)

