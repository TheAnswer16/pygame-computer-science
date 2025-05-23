import pygame
import random
import sys

# Inicialização
pygame.init()
WIDTH, HEIGHT = 800, 300
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skater Run")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_Y = HEIGHT - 40

# Skater
skater_width, skater_height = 40, 40
skater_x = 50
skater_y = GROUND_Y - skater_height
skater_velocity = 0
gravity = 0.6
jump_strength = -20
is_jumping = False

# Obstáculos
obstacle_width = 40
obstacle_height = 30
obstacle_speed = 6
obstacles = []

# Plataformas
platforms = [pygame.Rect(0, GROUND_Y, WIDTH, 40)]

# Score
score = 0
high_score = 0

# Criar obstáculos
def create_obstacle():
    tipo = random.choice(["banco", "vala"])
    x = WIDTH
    if tipo == "banco":
        rect = pygame.Rect(x, GROUND_Y - obstacle_height, obstacle_width, obstacle_height)
        return {"type": "banco", "rect": rect}
    elif tipo == "vala":
        largura_vala = random.randint(60, 120)
        return {"type": "vala", "x": x, "width": largura_vala}

# Resetar
def reset_game():
    global skater_y, skater_velocity, is_jumping, obstacles, platforms, score
    skater_y = GROUND_Y - skater_height
    skater_velocity = 0
    is_jumping = False
    obstacles.clear()
    platforms = [pygame.Rect(0, GROUND_Y, WIDTH, 40)]
    score = 0

# Loop principal
def game_loop():
    global skater_y, skater_velocity, is_jumping, score, high_score, obstacle_speed

    running = True
    while running:
        clock.tick(60)
        SCREEN.fill(WHITE)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not is_jumping:
            skater_velocity = jump_strength
            is_jumping = True

        # Pulo
        skater_velocity += gravity
        skater_y += skater_velocity

        if skater_y >= GROUND_Y - skater_height:
            skater_y = GROUND_Y - skater_height
            skater_velocity = 0
            is_jumping = False

        # Criar obstáculos
        if len(obstacles) == 0 or (obstacles[-1]["type"] == "banco" and obstacles[-1]["rect"].x < WIDTH - random.randint(200, 400)) or (obstacles[-1]["type"] == "vala" and obstacles[-1]["x"] < WIDTH - random.randint(200, 400)):
            obstacles.append(create_obstacle())

        skater_rect = pygame.Rect(skater_x, skater_y, skater_width, skater_height)

        # Atualizar plataformas
        platforms.clear()
        last_x = 0
        for obs in obstacles:
            if obs["type"] == "vala":
                platforms.append(pygame.Rect(last_x, GROUND_Y, obs["x"] - last_x, 40))
                last_x = obs["x"] + obs["width"]
        platforms.append(pygame.Rect(last_x, GROUND_Y, WIDTH - last_x, 40))

        # Verificar chão
        on_platform = False
        for plat in platforms:
            if plat.colliderect(skater_rect.move(0, 1)):
                on_platform = True
                break
        if not on_platform:
            skater_velocity += gravity

        # Desenhar obstáculos
        for obs in list(obstacles):
            if obs["type"] == "banco":
                obs["rect"].x -= obstacle_speed
                pygame.draw.rect(SCREEN, BLACK, obs["rect"])
                if skater_rect.colliderect(obs["rect"]):
                    high_score = max(score, high_score)
                    reset_game()
                    obstacle_speed = 6
                    break
                if obs["rect"].right < 0:
                    obstacles.remove(obs)
                    score += 1
            elif obs["type"] == "vala":
                obs["x"] -= obstacle_speed
                pygame.draw.line(SCREEN, BLACK, (obs["x"], GROUND_Y), (obs["x"] + obs["width"], GROUND_Y), 4)
                if skater_rect.x + skater_width > obs["x"] and skater_rect.x < obs["x"] + obs["width"]:
                    if skater_y + skater_height >= GROUND_Y:
                        high_score = max(score, high_score)
                        reset_game()
                        obstacle_speed = 6
                        break
                if obs["x"] + obs["width"] < 0:
                    obstacles.remove(obs)
                    score += 1

        # Aumentar dificuldade
        if score and score % 10 == 0:
            obstacle_speed = 6 + score // 10

        # Desenhar chão
        for plat in platforms:
            pygame.draw.rect(SCREEN, BLACK, plat)

        # Desenhar skatista
        pygame.draw.rect(SCREEN, BLACK, skater_rect)

        # Pontuação
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        high_score_text = FONT.render(f"High Score: {high_score}", True, BLACK)
        SCREEN.blit(score_text, (10, 10))
        SCREEN.blit(high_score_text, (10, 40))

        pygame.display.update()

# Início
game_loop()
