import pygame
import random
import sys

# Inicialização
pygame.init()
WIDTH, HEIGHT = 900, 300
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skater Run")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_Y = HEIGHT - 40

# Carregar imagem do skatista
SKATER_IMG = pygame.image.load("assets/skater_running.png").convert_alpha()
BENCH_IMG =  pygame.image.load("assets/bench.png").convert_alpha()

class Skater:
    def __init__(self):
        self.image = pygame.transform.scale(SKATER_IMG, (70, 70))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = 50
        self.y = GROUND_Y - self.height
        self.velocity = 0
        self.gravity = 0.7
        self.jump_strength = -26
        self.is_jumping = False

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.velocity = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.velocity = self.jump_strength
            self.is_jumping = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Obstacle:
    def update(self, speed): pass
    def draw(self, surface): pass
    def collides_with(self, skater_rect): return False
    def is_off_screen(self): return False

class Banco(Obstacle):
    def __init__(self):
        self.image = pygame.transform.scale(BENCH_IMG, (90, 80))        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(WIDTH, GROUND_Y - self.height + 12, self.width, self.height)

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
       surface.blit(self.image, self.rect)

    def collides_with(self, skater_rect):
        return self.rect.colliderect(skater_rect)

    def is_off_screen(self):
        return self.rect.right < 0

class Vala(Obstacle):
    def __init__(self):
        self.width = random.randint(60, 120)
        self.x = WIDTH

    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        pygame.draw.line(surface, BLACK, (self.x, GROUND_Y + 36), (self.x + self.width, GROUND_Y + 36), 4)

    def collides_with(self, skater_rect):
        return (
            skater_rect.x + skater_rect.width > self.x and
            skater_rect.x < self.x + self.width and
            skater_rect.y + skater_rect.height >= GROUND_Y
        )

    def is_off_screen(self):
        return self.x + self.width < 0


class HighScoreManager:


    def get_high_score():

        import configparser
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")
        return cfg.getint("screen", "high_score", fallback=0)

    def set_high_score(score):
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")
        if not cfg.has_section("screen"):
            cfg.add_section("screen")
        cfg.set("screen", "high_score", str(score))
        with open("settings.ini", "w") as configfile:
            cfg.write(configfile)


class Game:

    def __init__(self):
        self.skater = Skater()
        self.obstacles = []
        self.platforms = [pygame.Rect(0, GROUND_Y, WIDTH, 40)]
        self.score = 0
        self.high_score = HighScoreManager.get_high_score()
        self.speed = 6

    def reset(self):
        self.skater = Skater()
        self.obstacles.clear()
        self.platforms = [pygame.Rect(0, GROUND_Y, WIDTH, 40)]
        self.score = 0
        self.speed = 6

    def generate_obstacle(self):
        return random.choice([Banco(), Vala()])

    def update_platforms(self):
        self.platforms.clear()
        last_x = 0
        for obs in self.obstacles:
            if isinstance(obs, Vala):
                self.platforms.append(pygame.Rect(last_x, GROUND_Y, obs.x - last_x, 40))
                last_x = obs.x + obs.width
        self.platforms.append(pygame.Rect(last_x, GROUND_Y, WIDTH - last_x, 40))

    def run(self):
        running = True
        while running:
            clock.tick(60)
            SCREEN.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                self.skater.jump()

            self.skater.update()
            skater_rect = self.skater.get_rect()

            # Verificar chão
            self.update_platforms()
            on_platform = any(plat.colliderect(skater_rect.move(0, 1)) for plat in self.platforms)
            if not on_platform:
                self.skater.velocity += self.skater.gravity

            # Gerar novo obstáculo
            if not self.obstacles or (
                isinstance(self.obstacles[-1], Banco) and self.obstacles[-1].rect.x < WIDTH - random.randint(200, 400)
            ) or (
                isinstance(self.obstacles[-1], Vala) and self.obstacles[-1].x < WIDTH - random.randint(200, 400)
            ):
                self.obstacles.append(self.generate_obstacle())

            # Atualizar e desenhar obstáculos
            for obs in list(self.obstacles):
                obs.update(self.speed)
                obs.draw(SCREEN)
                if obs.collides_with(skater_rect):
                    self.high_score = max(self.score, self.high_score)
                    HighScoreManager.set_high_score(self.high_score)
                    self.reset()
                    break
                if obs.is_off_screen():
                    self.obstacles.remove(obs)
                    self.score += 1

            # Dificuldade progressiva
            if self.score and self.score % 10 == 0:
                self.speed = 6 + self.score // 10

            # Desenhar plataformas
            for plat in self.platforms:
                pygame.draw.rect(SCREEN, BLACK, plat)

            # Desenhar skatista
            self.skater.draw(SCREEN)

            # Mostrar pontuação
            score_text = FONT.render(f"Score: {self.score}", True, BLACK)
            high_score_text = FONT.render(f"High Score: {self.high_score}", True, BLACK)
            SCREEN.blit(score_text, (10, 10))
            SCREEN.blit(high_score_text, (10, 40))

            pygame.display.update()

# Início
if __name__ == "__main__":
    game = Game()
    game.run()
