import pygame
import os
import random
from SpriteHeroi import Aventureiro

class Cachorro(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.SPRITE_SCALE = 2.5
        self.TILE_SIZE = getattr(self.game, 'TILE_SIZE', 32)
        self.death_animation_duration = 3000
        self.death_start_time = 0
        self.alpha = 255
        self.collision_map = []

        self.sounds = {
            'ataque': pygame.mixer.Sound(os.path.join("Sons", "cachorro", "atacando.wav")),
            'dano': pygame.mixer.Sound(os.path.join("Sons", "cachorro", "parado.wav")),
            'morte': pygame.mixer.Sound(os.path.join("Sons", "cachorro", "morrendo.wav")),
        }
        for sound in self.sounds.values():
            sound.set_volume(0.05)

        self.states = {
            'parado': [], 'andando_direita': [], 'andando_esquerda': [],
            'atacando_direita': [], 'atacando_esquerda': [],
            'levando_dano_direita': [], 'levando_dano_esquerda': [],
            'morrendo_direita': [], 'morrendo_esquerda': []
        }
        self.load_animations()

        self.image = self.states['parado'][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.health = 80
        self.max_health = 80
        self.damage = 10
        self.speed = 2.0
        self.attack_cooldown = 800
        self.last_attack = 0

        self.current_state = 'parado'
        self.current_frame = 0
        self.animation_speed = 0.15
        self.facing_right = True

        self.detection_radius = 300
        self.attack_range = 40
        self.is_attacking = False
        self.is_taking_damage = False
        self.is_dead = False

        self.idle_time = 0
        self.idle_cooldown = random.randint(1000, 3000)
        self.last_idle_change = pygame.time.get_ticks()

        self.collision_rect = pygame.Rect(0, 0, 140, 60)
        self.collision_rect.center = self.rect.center

    def load_animations(self):
        animation_frames = {
            'parado': 6, 'andando_esquerda': 5,
            'atacando_esquerda': 3, 'levando_dano_esquerda': 4,
            'morrendo_esquerda': 7
        }

        for state, frame_count in animation_frames.items():
            print(f'Carregando animação: {state} com {frame_count} frames.')
            for i in range(frame_count):
                img_path = os.path.join("Inimigos", "cachorro", f"{state}_{i}.png")
                if not os.path.exists(img_path):
                    print(f'Imagem não encontrada: {img_path}')
                try:
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(
                        img,
                        (int(img.get_width() * self.SPRITE_SCALE), int(img.get_height() * self.SPRITE_SCALE))
                    )
                    self.states[state].append(img)

                    if '_esquerda' in state:
                        flipped_state = state.replace('_esquerda', '_direita')
                        flipped_img = pygame.transform.flip(img, True, False)
                        self.states[flipped_state].append(flipped_img)
                except:
                    surf = pygame.Surface((32, 32))
                    surf.fill((200, 100, 0) if 'morrendo' not in state else (150, 50, 0))
                    self.states[state].append(surf)
                    if '_esquerda' in state:
                        flipped_state = state.replace('_esquerda', '_direita')
                        self.states[flipped_state].append(pygame.transform.flip(surf, True, False))

    def update(self, player_rect):
        current_time = pygame.time.get_ticks()

        if self.is_dead:
            # Animação de fade-out ao morrer
            progress = min(1.0, (current_time - self.death_start_time) / self.death_animation_duration)
            self.alpha = int(255 * (1 - progress))
            self.image.set_alpha(self.alpha)
            if progress >= 1.0:
                self.kill()
            return

        self.current_frame += self.animation_speed
        if int(self.current_frame) >= len(self.states[self.current_state]):
            self.current_frame = 0
            if 'atacando' in self.current_state:
                self.is_attacking = False
                self.current_state = 'parado'
            elif 'levando_dano' in self.current_state:
                self.is_taking_damage = False
                self.current_state = 'parado'

        self.image = self.states[self.current_state][int(self.current_frame)]

        if not self.is_attacking and not self.is_taking_damage:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            distance = (dx**2 + dy**2)**0.5

            if distance < self.detection_radius:
                self.facing_right = dx > 0
                if distance < self.attack_range:
                    self.attack()
                else:
                    new_x = self.rect.x + (1 if dx > 0 else -1) * self.speed if abs(dx) > 5 else self.rect.x
                    new_y = self.rect.y + (1 if dy > 0 else -1) * self.speed if abs(dy) > 5 else self.rect.y

                    if not self.check_collision(new_x, self.rect.y):
                        self.rect.x = new_x
                    if not self.check_collision(self.rect.x, new_y):
                        self.rect.y = new_y

                    self.current_state = 'andando_direita' if self.facing_right else 'andando_esquerda'
                    self.idle_time = 0
            else:
                if current_time - self.last_idle_change > self.idle_cooldown:
                    self.facing_right = random.choice([True, False])
                    self.last_idle_change = current_time
                    self.idle_cooldown = random.randint(1000, 3000)

        self.collision_rect.center = self.rect.center

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack > self.attack_cooldown:
            self.is_attacking = True
            self.current_state = 'atacando_direita' if self.facing_right else 'atacando_esquerda'
            self.current_frame = 0
            self.last_attack = current_time
            self.sounds['ataque'].play()
            return True
        return False

    def take_damage(self, amount):
        if self.is_dead:
            return False

        self.health -= amount

        if self.health <= 0:
            self.die()
            return True

        self.is_taking_damage = True
        self.current_state = 'levando_dano_direita' if self.facing_right else 'levando_dano_esquerda'
        self.current_frame = 0
        self.sounds['dano'].play()
        return True

    def die(self):
        self.is_dead = True
        self.current_state = 'morrendo_direita' if self.facing_right else 'morrendo_esquerda'
        self.current_frame = 0
        self.death_start_time = pygame.time.get_ticks()
        self.sounds['morte'].play()
        self.collision_rect = pygame.Rect(0, 0, 0, 0)  # Desativa colisão

        if hasattr(self.game, 'aventureiro'):
            self.game.aventureiro.restore_health(100)

    def check_collision(self, new_x, new_y):
        if not self.collision_map:
            return False

        tile_size = self.TILE_SIZE
        collision_rect = self.collision_rect.copy()
        collision_rect.x = new_x + (self.rect.width - collision_rect.width) // 2
        collision_rect.y = new_y + (self.rect.height - collision_rect.height) // 2

        corners = [
            (collision_rect.left, collision_rect.top),
            (collision_rect.right, collision_rect.top),
            (collision_rect.left, collision_rect.bottom),
            (collision_rect.right, collision_rect.bottom)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x // tile_size)
            tile_y = int(corner_y // tile_size)

            if 0 <= tile_y < len(self.collision_map) and 0 <= tile_x < len(self.collision_map[0]):
                if self.collision_map[tile_y][tile_x] == 1:
                    return True

        return False

    def draw_health_bar(self, surface, camera_x, camera_y):
        if self.is_dead or self.alpha < 50:
            return

        bar_width = 40
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width

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
