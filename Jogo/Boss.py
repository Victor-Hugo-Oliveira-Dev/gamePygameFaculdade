import pygame
import os
import random
from SpriteHeroi import Aventureiro

class Boss(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.SPRITE_SCALE = 2.0  # Escala maior para o Boss
        self.TILE_SIZE = getattr(self.game, 'TILE_SIZE', 32)
        self.max_health = 100  # Certifique-se que está definido
        self.health = self.max_health  # Garantir que começa com vida máxima
        self.death_animation_duration = 3500  # Animação de morte mais longa
        self.death_start_time = 0
        self.alpha = 255
        self.collision_map = []
        
        # Sons
        self.sounds = {
            'ataque': pygame.mixer.Sound(os.path.join("Sons", "1 mob", "morrendo.wav")),  
            'dano': pygame.mixer.Sound(os.path.join("Sons", "1 mob", "morrendo.wav")),
            'morte': pygame.mixer.Sound(os.path.join("Sons", "1 mob", "morrendo.wav")),
        }
        for sound in self.sounds.values():
            sound.set_volume(0.4)  # Volume mais alto
        
        # Estados e animações
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
        
        # Atributos ajustáveis (Boss mais forte)
        self.health = 100  # Vida alta
        self.max_health = 100
        self.damage = 20  
        self.speed = 1.2  
        self.attack_cooldown = 4000  
        self.last_attack = 0
        
        # Controle de animação
        self.current_state = 'parado'
        self.current_frame = 0
        self.animation_speed = 0.06  # Animação mais lenta (dramática)
        self.facing_right = True
        
        # Sistema de combate
        self.detection_radius = 400  # Detecta o jogador de longe
        self.attack_range = 30  # Ataque de longo alcance
        self.is_attacking = False
        self.is_taking_damage = False
        self.is_dead = False
        
        # Comportamento de inércia
        self.idle_time = 0
        self.idle_cooldown = random.randint(1000, 3000)
        self.last_idle_change = pygame.time.get_ticks()  # Adicionando o atributo faltante
        
        # Hitbox (ajustável) - Maior para combinar com o sprite grande
        self.collision_rect = pygame.Rect(0, 0, 200, 250) 
        self.collision_rect.center = self.rect.center

    def load_animations(self):
        animation_frames = {
            'parado': 9, 'andando_esquerda': 6,
            'atacando_esquerda': 12, 'levando_dano_esquerda': 5,
            'morrendo_esquerda': 23
        }
        
        for state, frame_count in animation_frames.items():
            for i in range(frame_count):
                try:
                    img_path = os.path.join("Inimigos", "boss", f"{state}_{i}.png")
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, (int(img.get_width() * self.SPRITE_SCALE), int(img.get_height() * self.SPRITE_SCALE)))
                    self.states[state].append(img)
                    
                    if '_esquerda' in state:
                        flipped_state = state.replace('_esquerda', '_direita')
                        flipped_img = pygame.transform.flip(img, True, False)
                        self.states[flipped_state].append(flipped_img)
                except:
                    surf = pygame.Surface((48, 48))
                    surf.fill((150, 0, 150) if 'morrendo' not in state else (100, 0, 100))
                    surf = pygame.transform.scale(surf, (int(surf.get_width() * self.SPRITE_SCALE), int(surf.get_height() * self.SPRITE_SCALE)))
    
    def update(self, player_rect):
        """Atualiza o estado do zumbi com morte gradual"""
        current_time = pygame.time.get_ticks()
        
        if self.is_dead:
            # Calcula progresso da morte (0 a 1)
            progress = min(1.0, (current_time - self.death_start_time) / self.death_animation_duration)
            
            # Atualiza animação de morte
            self.current_frame += self.animation_speed
            if int(self.current_frame) >= len(self.states[self.current_state]):
                self.current_frame = 0
            
            # Aplica fade-out gradual
            self.alpha = int(255 * (1 - progress))
            self.image = self.states[self.current_state][int(self.current_frame)]
            self.image.set_alpha(self.alpha)
            
            # Remove quando a animação terminar e estiver totalmente transparente
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
        
        # Comportamento de inércia quando não está atacando ou tomando dano
        if not self.is_attacking and not self.is_taking_damage:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            distance = (dx**2 + dy**2)**0.5
            
            # Verifica se o jogador está no raio de detecção
            if distance < self.detection_radius:
                # Direção do zumbi
                self.facing_right = dx > 0
                
                # Se está no alcance de ataque
                if distance < self.attack_range:
                    self.attack()
                else:
                    # Movimenta-se em direção ao jogador
                    if abs(dx) > 5:  # Deadzone horizontal
                        direction = 1 if dx > 0 else -1
                        self.rect.x += direction * self.speed
                    
                    if abs(dy) > 5:  # Deadzone vertical
                        direction = 1 if dy > 0 else -1
                        self.rect.y += direction * self.speed
                    
                    # Atualiza animação de movimento
                    self.current_state = 'andando_direita' if self.facing_right else 'andando_esquerda'
                    self.idle_time = 0
            else:
                # Comportamento de inércia quando o jogador não está próximo
                if self.current_state != 'parado':
                    self.current_state = 'parado'
                    self.current_frame = 0
                
                # Aleatoriedade no comportamento parado
                if current_time - self.last_idle_change > self.idle_cooldown:
                    # Muda a direção que está olhando aleatoriamente
                    self.facing_right = random.choice([True, False])
                    self.last_idle_change = current_time
                    self.idle_cooldown = random.randint(1000, 3000)
                    
                    # Pequena chance de dar um passo aleatório
                    if random.random() < 0.2:  # 20% de chance
                        self.rect.x += random.choice([-1, 1]) * self.speed
                        self.rect.y += random.choice([-1, 1]) * self.speed
                        self.current_state = 'andando_direita' if self.facing_right else 'andando_esquerda'
        
        # Atualiza retângulo de colisão
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
        if not self.is_dead:
            self.health -= amount
            self.is_taking_damage = True
            self.current_state = 'levando_dano_direita' if self.facing_right else 'levando_dano_esquerda'
            self.current_frame = 0
            self.sounds['dano'].play()
            
            if self.health <= 0:
                self.die()
            return True
        return False

    def die(self):
        """Inicia o processo de morte gradual"""
        self.is_dead = True
        self.current_state = 'morrendo_direita' if self.facing_right else 'morrendo_esquerda'
        self.current_frame = 0
        self.death_start_time = pygame.time.get_ticks()
        self.sounds['morte'].play()
        self.collision_rect = pygame.Rect(0, 0, 0, 0)  # Desativa colisões

        # Regenera vida do herói quando o zumbi morre
        if hasattr(self.game, 'aventureiro'):
            self.game.aventureiro.restore_health(20)  # Restaura 20 pontos de vida

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
        pass

    def draw_debug(self, surface, camera_x, camera_y):
        """Desenha a hitbox de colisão para debug"""
        if not hasattr(self, 'collision_rect'):
            return
        
        # Cria uma cópia do retângulo de colisão ajustado para a câmera
        debug_rect = pygame.Rect(
            self.collision_rect.x - camera_x,
            self.collision_rect.y - camera_y,
            self.collision_rect.width,
            self.collision_rect.height
        )
        
        # Desenha o retângulo vermelho semi-transparente
        debug_surface = pygame.Surface((debug_rect.width, debug_rect.height), pygame.SRCALPHA)
        debug_surface.fill((255, 0, 0, 128))  # Vermelho com 50% de transparência
        surface.blit(debug_surface, (debug_rect.x, debug_rect.y))
        
        # Desenha a borda do retângulo
        pygame.draw.rect(surface, (255, 0, 0), debug_rect, 1)