import pygame
import random
import sys
import configparser

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

# Imagens
BACKGROUND_IMG = pygame.image.load("assets/sky.png").convert()
MENU_BACKGROUND = pygame.image.load("assets/menu_background.png").convert()
SKATER_IMG = pygame.image.load("assets/skater_running.png").convert_alpha()
BENCH_IMG = pygame.image.load("assets/bench.png").convert_alpha()
# Use sua imagem para a caixa empilhada e o pombo
CAIXA_IMG = pygame.image.load("assets/caixa_empilhada.png").convert_alpha()
POMBO_IMG = pygame.image.load("assets/pombo.png").convert_alpha()

def show_menu():
    menu_items = ["Iniciar Jogo", "Ver High Score", "Sair"]
    buttons = []
    button_width, button_height = 250, 50
    spacing = 20
    start_y = HEIGHT // 2 - (button_height + spacing) * len(menu_items) // 2

    for i, text in enumerate(menu_items):
        x = WIDTH // 2 - button_width // 2
        y = start_y + i * (button_height + spacing)
        rect = pygame.Rect(x, y, button_width, button_height)
        buttons.append((rect, text))

    while True:
        SCREEN.blit(MENU_BACKGROUND, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, text in buttons:
                    if rect.collidepoint(mouse_pos):
                        return text.lower()

        for rect, text in buttons:
            color = (180, 180, 180) if rect.collidepoint(mouse_pos) else (220, 220, 220)
            pygame.draw.rect(SCREEN, color, rect, border_radius=10)
            pygame.draw.rect(SCREEN, BLACK, rect, 2, border_radius=10)
            label = FONT.render(text, True, BLACK)
            label_rect = label.get_rect(center=rect.center)
            SCREEN.blit(label, label_rect)

        pygame.display.update()
        clock.tick(60)

def show_high_score():
    high = HighScoreManager.get_high_score()
    back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 40)

    while True:
        SCREEN.fill(WHITE)
        label = FONT.render(f"High Score: {high}", True, BLACK)
        label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        SCREEN.blit(label, label_rect)

        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(SCREEN, (200, 200, 200), back_rect, border_radius=10)
        pygame.draw.rect(SCREEN, BLACK, back_rect, 2, border_radius=10)
        back_label = FONT.render("Voltar", True, BLACK)
        back_label_rect = back_label.get_rect(center=back_rect.center)
        SCREEN.blit(back_label, back_label_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse_pos):
                    return

        pygame.display.update()
        clock.tick(60)

# === CLASSES DO JOGO ===

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
        self.jump_buffer = 0
        self.jump_buffer_time = 5
        self.terminal_velocity = 20
        self.is_jumping = False
        self.is_sliding = False
        self.slide_time = 0
        self.max_slide_time = 20

    def update(self):
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        self.velocity += self.gravity
        if self.velocity > self.terminal_velocity:
            self.velocity = self.terminal_velocity

        self.y += self.velocity
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.velocity = 0
            self.is_jumping = False
            self.jump_buffer = 0

        if self.is_sliding:
            self.slide_time -= 1
            if self.slide_time <= 0:
                self.is_sliding = False

    def jump(self):
        if not self.is_jumping:
            self.velocity = self.jump_strength
            self.is_jumping = True
        else:
            self.jump_buffer = self.jump_buffer_time

    def slide(self):
        if not self.is_sliding and not self.is_jumping:
            self.is_sliding = True
            self.slide_time = self.max_slide_time

    def get_rect(self):
        margin = 10
        if self.is_sliding:
            return pygame.Rect(self.x + margin, self.y + 30, self.width - 2 * margin, self.height - 40)
        return pygame.Rect(self.x + margin, self.y + margin, self.width - 2 * margin, self.height - margin)

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
        self.rect = pygame.Rect(WIDTH, GROUND_Y - self.height + 18, self.width, self.height)

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

class CaixaEmpilhada(Obstacle):
    def __init__(self):
        self.image = pygame.transform.scale(CAIXA_IMG, (80, 105))  # maior que banco
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # Posicionado no chão
        self.rect = pygame.Rect(WIDTH, GROUND_Y - self.height, self.width, self.height)

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collides_with(self, skater_rect):
        return self.rect.colliderect(skater_rect)

    def is_off_screen(self):
        return self.rect.right < 0

class Pombo(Obstacle):
    def __init__(self):
        self.image = pygame.transform.scale(POMBO_IMG, (50, 40))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = WIDTH
        self.y = GROUND_Y - 80  # altura fixa, perto do topo do skatista
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 7  # velocidade constante para a esquerda

    def update(self, speed):
        self.x -= self.speed  # velocidade fixa, independente da velocidade do jogo para variar
        self.rect.x = int(self.x)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collides_with(self, skater_rect):
        return self.rect.colliderect(skater_rect)

    def is_off_screen(self):
        return self.rect.right < 0

class HighScoreManager:
    @staticmethod
    def get_high_score():
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")
        return cfg.getint("screen", "high_score", fallback=0)

    @staticmethod
    def set_high_score(score):
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
        self.max_speed = 10  # Limite máximo de velocidade

    def reset(self):
        self.__init__()

    def generate_obstacle(self):
        if self.score < 10:
            return random.choice([Banco(), Vala()])
        else:
            choice = random.choice(['banco', 'vala', 'caixa', 'pombo'])
            if choice == 'banco':
                return Banco()
            elif choice == 'vala':
                return Vala()
            elif choice == 'caixa':
                return CaixaEmpilhada()
            else:
                return Pombo()

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
        paused = False
        pause_menu_rect = pygame.Rect(WIDTH - 110, 10, 100, 40)
        button_continue_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 60, 150, 50)
        button_exit_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50)

        while running:
            clock.tick(60)
            SCREEN.blit(BACKGROUND_IMG, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = not paused
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if paused:
                        if button_continue_rect.collidepoint(mouse_pos):
                            paused = False
                        elif button_exit_rect.collidepoint(mouse_pos):
                            return
                    elif pause_menu_rect.collidepoint(mouse_pos):
                        paused = True

            if not paused:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                    self.skater.jump()
                if keys[pygame.K_DOWN]:
                    self.skater.slide()

                self.skater.update()
                skater_rect = self.skater.get_rect()

                self.update_platforms()
                on_platform = any(plat.colliderect(skater_rect.move(0, 1)) for plat in self.platforms)
                if not on_platform:
                    self.skater.velocity += self.skater.gravity

                if not self.obstacles or (
                    isinstance(self.obstacles[-1], Banco) and self.obstacles[-1].rect.x < WIDTH - random.randint(300, 500)
                ) or (
                    isinstance(self.obstacles[-1], Vala) and self.obstacles[-1].x < WIDTH - random.randint(200, 400)
                ) or (
                    isinstance(self.obstacles[-1], CaixaEmpilhada) and self.obstacles[-1].rect.x < WIDTH - random.randint(300, 600)
                ) or (
                    isinstance(self.obstacles[-1], Pombo) and self.obstacles[-1].rect.x < WIDTH - random.randint(300, 600)
                ):
                    self.obstacles.append(self.generate_obstacle())

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

                # Limite máximo de velocidade para evitar jogo muito rápido
                if self.score and self.speed < self.max_speed:
                    self.speed = 6 + self.score // 15

            # Desenha plataformas e skater mesmo quando pausado
            for plat in self.platforms:
                pygame.draw.rect(SCREEN, BLACK, plat)

            self.skater.draw(SCREEN)

            score_text = FONT.render(f"Score: {self.score}", True, BLACK)
            high_score_text = FONT.render(f"High Score: {self.high_score}", True, BLACK)
            SCREEN.blit(score_text, (10, 10))
            SCREEN.blit(high_score_text, (10, 40))

            # Botão de pause no canto superior direito
            pygame.draw.rect(SCREEN, (150, 150, 150), pause_menu_rect, border_radius=8)
            pause_label = FONT.render("Pausar", True, BLACK)
            pause_label_rect = pause_label.get_rect(center=pause_menu_rect.center)
            SCREEN.blit(pause_label, pause_label_rect)

            # Se pausado, desenha o menu flutuante
            if paused:
                # Fundo semitransparente
                s = pygame.Surface((WIDTH, HEIGHT))
                s.set_alpha(180)
                s.fill((50, 50, 50))
                SCREEN.blit(s, (0, 0))

                # Botões do menu
                for rect, text in [(button_continue_rect, "Continuar"), (button_exit_rect, "Sair")]:
                    color = (180, 180, 180)
                    pygame.draw.rect(SCREEN, color, rect, border_radius=10)
                    pygame.draw.rect(SCREEN, BLACK, rect, 2, border_radius=10)
                    label = FONT.render(text, True, BLACK)
                    label_rect = label.get_rect(center=rect.center)
                    SCREEN.blit(label, label_rect)

            pygame.display.update()

# === EXECUÇÃO ===
if __name__ == "__main__":
    while True:
        action = show_menu()
        if action == "iniciar jogo":
            game = Game()
            game.run()
        elif action == "ver high score":
            show_high_score()
        elif action == "sair":
            break
