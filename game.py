import pygame
import random
import sys

# Inicialização
pygame.init()

# Tamanho da tela
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Cores
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

# Fonte
FONT = pygame.font.SysFont("Arial", 32)

# Relógio
clock = pygame.time.Clock()
FPS = 60

# Variáveis do jogo
gravity = 0.5
jump_strength = -10
pipe_gap = 150
pipe_width = 70
pipe_speed = 3

# Classe do Pássaro
class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 20

    def update(self):
        self.velocity += gravity
        self.y += self.velocity

    def jump(self):
        self.velocity = jump_strength

    def draw(self):
        pygame.draw.circle(SCREEN, RED, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

# Função para criar canos
def create_pipe():
    top_height = random.randint(50, HEIGHT - pipe_gap - 100)
    bottom_height = HEIGHT - top_height - pipe_gap
    return {'x': WIDTH, 'top': top_height, 'bottom': bottom_height}

# Loop principal do jogo
def game_loop():
    bird = Bird()
    pipes = [create_pipe()]
    score = 0
    game_over = False

    while True:
        clock.tick(FPS)
        SCREEN.fill(BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    return game_loop()

        if not game_over:
            bird.update()

            # Atualizar canos
            for pipe in pipes:
                pipe['x'] -= pipe_speed

            # Remover e adicionar canos
            if pipes[-1]['x'] < WIDTH - 200:
                pipes.append(create_pipe())

            if pipes[0]['x'] < -pipe_width:
                pipes.pop(0)
                score += 1

            # Verificar colisões
            bird_rect = bird.get_rect()
            for pipe in pipes:
                top_rect = pygame.Rect(pipe['x'], 0, pipe_width, pipe['top'])
                bottom_rect = pygame.Rect(pipe['x'], HEIGHT - pipe['bottom'],
                                          pipe_width, pipe['bottom'])
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    game_over = True

            # Verificar chão e teto
            if bird.y > HEIGHT or bird.y < 0:
                game_over = True

        # Desenhar canos
        for pipe in pipes:
            pygame.draw.rect(SCREEN, GREEN, (pipe['x'], 0, pipe_width, pipe['top']))
            pygame.draw.rect(SCREEN, GREEN, (pipe['x'], HEIGHT - pipe['bottom'],
                                             pipe_width, pipe['bottom']))

        # Desenhar pássaro
        bird.draw()

        # Mostrar pontuação
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        # Fim de jogo
        if game_over:
            over_text = FONT.render("Game Over! Press R to restart", True, WHITE)
            SCREEN.blit(over_text, (20, HEIGHT // 2 - 20))

        pygame.display.flip()

# Início
game_loop()
