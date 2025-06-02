import pygame
import os

class Aventureiro(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.SPRITE_SCALE = 2.5
        self.TILE_SIZE = getattr(self.game, 'TILE_SIZE', 32)
        self.last_attack = 0
        self.damage = 20

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

        self.animation_speeds = {
            'respirando_direita': 0.05,
            'respirando_esquerda': 0.05,
            'andando_direita': 0.05,
            'andando_esquerda': 0.05,
            'andando_cima': 0.05,
            'andando_baixo': 0.05,
            'atacando_direita': 0.2,
            'atacando_esquerda': 0.2,
            'morrendo_direita': 0.3,
            'morrendo_esquerda': 0.3
        }

        self.load_sprites()

        self.image = self.sprites['respirando_direita'][0]
        self.rect = self.image.get_rect()
        self.collision_rect = pygame.Rect(0, 0, 2 * self.TILE_SIZE, 2 * self.TILE_SIZE)
        self.collision_rect.center = self.rect.center

        self.max_health = 100
        self.current_health = self.max_health
        self.last_damage_time = 0
        self.damage_cooldown = 500
        self.state = 'respirando_direita'
        self.current_frame = 0
        self.speed = 2.5
        self.last_movement_key = None

    def load_sprites(self):
        sprite_paths = {
            'respirando_direita': ('HeroiRespirandoComEspada', 'adventurer-idle-{:02d}.png', 3),
            'respirando_esquerda': ('HeroiRespirandoComEspadaEsquerda', 'sprite_{}.png', 3),
            'andando_direita': ('AndandoComEspada', 'adventurer-run-{:02d}.png', 6),
            'andando_esquerda': ('AndandoComEspadaEsquerda', 'adventurer-run-{:02d}.png', 6),
            'andando_cima': ('AndandoParaCima', 'sprite_{}.png', 2),
            'andando_baixo': ('AndandoPraBaixo', 'sprite_{}.png', 2),
            'atacando_direita': ('HeroiAtacando', 'sprite_{}.png', 7),
            'atacando_esquerda': ('HeroiAtacandoEsquerda', 'sprite_{}.png', 7),
            'morrendo_direita': ('HeroiMorrendo', 'sprite_{}.png', 7),
            'morrendo_esquerda': ('HeroiMorrendoEsquerda', 'sprite_{}.png', 7)
        }

        for state, (folder, pattern, count) in sprite_paths.items():
            for i in range(count):
                path = os.path.join('SprintHeroi', folder, pattern.format(i))
                if os.path.exists(path):
                    img = pygame.image.load(path)
                else:
                    img = pygame.Surface((32, 32))
                img = pygame.transform.scale(img, (int(img.get_width() * self.SPRITE_SCALE), int(img.get_height() * self.SPRITE_SCALE)))
                self.sprites[state].append(img)

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.damage_cooldown:
            self.current_health = max(0, self.current_health - amount)
            self.last_damage_time = current_time
            return True
        return False

    def restore_health(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def draw_health_bar(self, surface, camera_x, camera_y):
        bar_width = 40
        bar_height = 5
        fill = (self.current_health / self.max_health) * bar_width

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

        pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(surface, (255, 255, 255), outline_rect, 1)

    def update(self):
        if not self.sprites[self.state]:
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
        return self.state.startswith('morrendo') and int(self.current_frame) >= len(self.sprites[self.state]) - 1