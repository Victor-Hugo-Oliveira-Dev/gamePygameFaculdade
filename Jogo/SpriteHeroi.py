import pygame
import os

class Aventureiro(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.SPRITE_SCALE = 2.5
        self.TILE_SIZE = getattr(self.game, 'TILE_SIZE', 32)
        self.last_attack = 0  
        self.damage = 20  # Dano do jogador
        
        # Inicializa o dicionário de sprites
        self.sprites = {
            'respirando_direita': [],
            'respirando_esquerda': [],
            'andando_direita': [],
            'andando_esquerda': [],
            'andando_cima': [],
            'andando_baixo': [],
            'atacando_direita': [],
            'atacando_esquerda': [],
            'morrendo_direita': [],
            'morrendo_esquerda': []
        }

        # Velocidades de animação para cada estado
        self.animation_speeds = {
            'respirando_direita': 0.05,
            'respirando_esquerda': 0.05,
            'andando_direita': 0.05,  
            'andando_esquerda': 0.05,
            'andando_cima': 0.05,
            'andando_baixo': 0.05,
            'atacando_direita': 0.3,
            'atacando_esquerda': 0.3,
            'morrendo_direita': 0.5,
            'morrendo_esquerda': 0.5
        }

        # Carregando sprites de respiração para direita
        for i in range(3):
            caminho = os.path.join('SprintHeroi', 'HeroiRespirandoComEspada', f'adventurer-idle-{i:02d}.png')
            if os.path.exists(caminho):
                self.sprites['respirando_direita'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                # Cria uma imagem de fallback
                self.sprites['respirando_direita'].append(pygame.Surface((32, 32)))

        # Carregando sprites de respiração para esquerda
        for i in range(3):
            caminho = os.path.join('SprintHeroi', 'HeroiRespirandoComEspadaEsquerda', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['respirando_esquerda'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['respirando_esquerda'].append(pygame.Surface((32, 32)))

        # Carregando sprites de caminhada para direita
        for i in range(6):
            caminho = os.path.join('SprintHeroi', 'AndandoComEspada', f'adventurer-run-{i:02d}.png')
            if os.path.exists(caminho):
                self.sprites['andando_direita'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['andando_direita'].append(pygame.Surface((32, 32)))

        # Carregando sprites de caminhada para esquerda
        for i in range(6):
            caminho = os.path.join('SprintHeroi', 'AndandoComEspadaEsquerda', f'adventurer-run-{i:02d}.png')
            if os.path.exists(caminho):
                self.sprites['andando_esquerda'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['andando_esquerda'].append(pygame.Surface((32, 32)))

        # Carregando sprites de caminhada para cima
        for i in range(2):
            caminho = os.path.join('SprintHeroi', 'AndandoParaCima', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['andando_cima'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['andando_cima'].append(pygame.Surface((32, 32)))

        # Carregando sprites de caminhada para baixo
        for i in range(2):
            caminho = os.path.join('SprintHeroi', 'AndandoPraBaixo', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['andando_baixo'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['andando_baixo'].append(pygame.Surface((32, 32)))

        # Carregando sprites de ataque para direita
        for i in range(7):
            caminho = os.path.join('SprintHeroi', 'HeroiAtacando', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['atacando_direita'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['atacando_direita'].append(pygame.Surface((32, 32)))

        # Carregando sprites de ataque para esquerda
        for i in range(7):
            caminho = os.path.join('SprintHeroi', 'HeroiAtacandoEsquerda', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['atacando_esquerda'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['atacando_esquerda'].append(pygame.Surface((32, 32)))

        # Carregando sprites de morte para direita
        for i in range(7):
            caminho = os.path.join('SprintHeroi', 'HeroiMorrendo', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['morrendo_direita'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['morrendo_direita'].append(pygame.Surface((32, 32)))

        # Carregando sprites de morte para esquerda
        for i in range(7):
            caminho = os.path.join('SprintHeroi', 'HeroiMorrendoEsquerda', f'sprite_{i}.png')
            if os.path.exists(caminho):
                self.sprites['morrendo_esquerda'].append(pygame.image.load(caminho))
            else:
                print(f"Erro: Arquivo não encontrado - {caminho}")
                self.sprites['morrendo_esquerda'].append(pygame.Surface((32, 32)))

        # Redimensiona todos os sprites
        for state in self.sprites:
            for i in range(len(self.sprites[state])):
                original_img = self.sprites[state][i]
                scaled_width = int(original_img.get_width() * self.SPRITE_SCALE)
                scaled_height = int(original_img.get_height() * self.SPRITE_SCALE)
                self.sprites[state][i] = pygame.transform.scale(original_img, (scaled_width, scaled_height))

        self.image = self.sprites['respirando_direita'][0]
        self.rect = self.image.get_rect()
        self.collision_rect = pygame.Rect(0, 0, 2 * self.TILE_SIZE, 2 * self.TILE_SIZE)
        self.collision_rect.center = self.rect.center

        self.max_health = 100
        self.current_health = self.max_health
        self.last_damage_time = 0
        self.damage_cooldown = 500  # 1 segundo de cooldown entre danos
        self.state = 'respirando_direita'
        self.current_frame = 0
        self.speed = 2.5
        self.last_movement_key = None

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.damage_cooldown:
            self.current_health = max(0, self.current_health - amount)
            self.last_damage_time = current_time
            return True  # Dano aplicado
        return False  # Dano não aplicado (em cooldown)

    def restore_health(self, amount):
        """Restaura uma quantidade específica de vida do herói."""
        previous_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        if self.current_health > previous_health:
            # Tocar som de cura, se desejar
            pass

    def draw_health_bar(self, surface, camera_x, camera_y):
        bar_width = 40
        bar_height = 5
        fill = (self.current_health / self.max_health) * bar_width  # Já calcula proporção
        
        outline_rect = pygame.Rect(
            self.rect.x - camera_x + (self.rect.width - bar_width) // 2,
            self.rect.y - camera_y - 10,
            bar_width,
            bar_height
        )
        fill_rect = pygame.Rect(
            self.rect.x - camera_x + (self.rect.width - bar_width) // 2,
            self.rect.y - camera_y - 10,
            fill,
            bar_height
        )
        
        pygame.draw.rect(surface, (255, 0, 0), fill_rect)  # Vermelho (vida atual)
        pygame.draw.rect(surface, (255, 255, 255), outline_rect, 1)  # Borda branca

    def update(self):
        if not self.sprites[self.state]:
            print(f"Erro: Nenhum frame carregado para o estado '{self.state}'")
            return

        self.current_frame += self.animation_speeds[self.state]
        if int(self.current_frame) >= len(self.sprites[self.state]):
            self.current_frame = 0  
            if self.state.startswith('atacando') or self.state.startswith('morrendo'):
                self.state = 'respirando_direita' if self.last_movement_key == 'right' else 'respirando_esquerda'

        self.image = self.sprites[self.state][int(self.current_frame)]
        self.collision_rect.center = self.rect.center

    def attack(self):
        if self.last_movement_key == 'right':
            self.state = 'atacando_direita'
        elif self.last_movement_key == 'left':
            self.state = 'atacando_esquerda'
        self.current_frame = 0

    def walk_left(self):
        self.state = 'andando_esquerda'
        self.last_movement_key = 'left'

    def walk_right(self):
        self.state = 'andando_direita'
        self.last_movement_key = 'right'

    def walk_up(self):
        self.state = 'andando_cima'
        self.last_movement_key = 'up'

    def walk_down(self):
        self.state = 'andando_baixo'
        self.last_movement_key = 'down'

    def stop_walking(self):
        if self.state.startswith('andando'):
            self.state = 'respirando_direita' if self.last_movement_key == 'right' else 'respirando_esquerda'
            self.current_frame = 0

    def die(self):
        if not self.state.startswith('morrendo'):
            self.state = 'morrendo_direita' if self.last_movement_key == 'right' else 'morrendo_esquerda'
            self.current_frame = 0
            return True
        return False

    def is_dead(self):
        # Verifica se a animação de morte terminou
        return self.state.startswith('morrendo') and int(self.current_frame) >= len(self.sprites[self.state]) - 1
    
    def is_dead(self):
        return self.state.startswith('morrendo') and int(self.current_frame) >= len(self.sprites[self.state]) - 1