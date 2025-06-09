import pygame
import os
from ffpyplayer.player import MediaPlayer
import time
import numpy as np
from menu import *
from SpriteHeroi import Aventureiro
from mapa import load_map
from NPC import NPC
from Zumbi import Zumbi
from Cachorro import Cachorro
from Boss import Boss
from enemy_manager import get_enemy_config


class StartGame(Menu):
    def __init__(self, game, display, display_w, display_h):
        super().__init__(game)
        self.game = game
        self.display = display
        self.DISPLAY_W = display_w
        self.DISPLAY_H = display_h
        self.tela = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.relogio = pygame.time.Clock()
        self.todas_as_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.aventureiro = Aventureiro(self.game)
        self.game.aventureiro = self.aventureiro
        self.aventureiro.rect.center = (self.DISPLAY_W // 2, self.DISPLAY_H // 2)
        self.som_atacando = pygame.mixer.Sound(os.path.join("Sons", "SomAtacando.wav"))
        self.som_andando = pygame.mixer.Sound(os.path.join("Sons", "SomAndando.wav"))
        self.boss_music = pygame.mixer.Sound(os.path.join("Sons", "MusicaBoss.wav"))
        self.som_atacando.set_volume(0.1)
        self.som_andando.set_volume(0.1)
        self.boss_music.set_volume(0.1)
        self.boss = None
        self.current_map = 1
        self.collision_map, self.mapa_image = load_map(self.current_map)
        self.camera_x, self.camera_y = 0, 0
        self.TILE_SIZE = self.game.TILE_SIZE
        self.npc = None
        self.create_npc_for_map()
        self.create_enemies()
        self.game_over = False
        self.game_over_image = pygame.image.load(os.path.join("WinGameOver", "GAME OVER.png")).convert_alpha()
        self.game_over_image = pygame.transform.scale(self.game_over_image, (self.DISPLAY_W, self.DISPLAY_H))
        self.death_time = 0
        self.death_cooldown = 3000  # 3 segundos antes de mostrar game over

    def play_intro_sequence(self):
        self.display.fill((0, 0, 0))
        pygame.display.flip()

        audio_path = os.path.join("Sons", "SomIntro.mp3")
        if not os.path.exists(audio_path):
            print(f"Erro: Arquivo de áudio não encontrado em {audio_path}")
            return False

        # Carrega e toca a música
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        total_images = 533
        frame_duration = 70  # ms por imagem
        clock = pygame.time.Clock()

        for i in range(1, total_images + 1):
            img_filename = f"intro ({i}).jpg"
            img_path = os.path.join("Intro", img_filename)

            if not os.path.exists(img_path):
                print(f"Imagem não encontrada: {img_path}")
                # Opcional: criar uma imagem de fallback
                img = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
                img.fill((0, 0, 0))  # preto ou uma cor chamativa
            else:
                img = pygame.image.load(img_path).convert()
                img = pygame.transform.scale(img, (self.DISPLAY_W, self.DISPLAY_H))

            start_time = pygame.time.get_ticks()

            displaying = True
            while displaying:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game.playing = False
                        return False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        pygame.mixer.music.stop()
                        self.play_game_music()
                        return True

                self.display.blit(img, (0, 0))
                self.tela.blit(self.display, (0, 0))
                pygame.display.update()

                # Verifica se o tempo da imagem acabou
                if pygame.time.get_ticks() - start_time >= frame_duration:
                    displaying = False

                clock.tick(60)  # Limita a 60 FPS

        # Aguarda o final da música, se ainda estiver tocando
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

        pygame.mixer.music.stop()
        self.play_game_music()
        return True



    def play_game_music(self):
        try:
            pygame.mixer.music.load(os.path.join("Sons", "MusicaJogo.wav"))
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            print("Música do jogo iniciada.")
        except Exception as e:
            print(f"Erro ao carregar música do jogo: {e}")

    def handle_player_death(self):
        if not self.aventureiro.state.startswith('morrendo'):
            # Para TODOS os sons (incluindo inimigos, passos, ataques, etc.)
            pygame.mixer.stop()  # Isso para todos os canais de áudio
            pygame.mixer.music.stop()  # Para a música de fundo
            
            # Toca o som de morte (opcional)
            death_sound = pygame.mixer.Sound(os.path.join("Sons", "SomApanhando.wav"))
            death_sound.play()
            
            # Inicia a animação de morte
            self.aventureiro.die()
            self.death_time = pygame.time.get_ticks()
            
            # Toca a música de derrota (sem loop, ou em loop dependendo do arquivo)
            defeat_music_path = os.path.join("Sons", "SomLose.mp3")
            if os.path.exists(defeat_music_path):
                pygame.mixer.music.load(defeat_music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()  # Se quiser loop, use play(-1)
            
            # Inicia a cutscene de derrota
            self.play_defeat_cutscene()
            
    def render(self):
        self.display.fill(self.game.BLACK)
        
        if not self.game_over:
            self.display.blit(self.mapa_image, (-self.camera_x, -self.camera_y))
            
            for sprite in self.todas_as_sprites:
                self.display.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))
                if isinstance(sprite, (Zumbi, Cachorro, Boss)):
                    sprite.draw_health_bar(self.display, self.camera_x, self.camera_y)

            if self.current_map == 3 and self.boss and not self.boss.is_dead:
                self.draw_boss_health_bar()

            if self.npc is not None and self.npc.dialog_active:
                self.npc.draw_dialog(self.display)
            elif self.npc is not None and self.npc.show_confirmation:
                self.npc.draw_dialog(self.display)
            
            self.aventureiro.draw_health_bar(self.display, self.camera_x, self.camera_y)
        else:
            self.display.blit(self.game_over_image, (0, 0))
            self.game.draw_text("APERTE ENTER PARA RECOMEÇAR", 20, 
                               self.DISPLAY_W // 2, self.DISPLAY_H - 50)

        self.tela.blit(self.display, (0, 0))
        pygame.display.flip()

    def create_npc_for_map(self):
        if self.npc:
            self.todas_as_sprites.remove(self.npc)
        
        if self.current_map == 1:
            dialog_data = [
                {
                    'speaker': 'Cavaleiro',
                    'text':  "...Você... sobreviveu? Então... ainda há uma chance...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text':   "Que chance? O que aconteceu aqui?",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':  "Eles... tomaram tudo... luz, terra, sangue... não confie em ninguém...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text': "Mas quem fez isso? Ainda tem alguém vivo?",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':  "...Ela ainda respirava... mesmo com a carne dela se abrindo... eu... eu não consegui salva-la...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text': "Você foi atacado... isso foi obra de um deles?",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':   "...Esse maldito vírus... tá devorando ela por dentro... esse antídoto... ",
                    'text': "é tudo que resta. Leve pra ela. Antes que ela vire uma daquelas coisas.",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text': "Ela não vai morrer como um monstro. Eu juro.",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':    "...Ela... minha filha... foi mordida... por aquela coisa...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text':   "Você tá ferido... o que aconteceu? Quem era ela?",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':     "...Tem pouco tempo... esse antídoto... leve até ela... Salve-a, por favor...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text':   "Eu prometo. Ela vai sobreviver. Nem que eu tenha que atravessar o inferno.",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':      "...Eu devia ter acabado com o sofrimento dela... mas eu... eu não tive coragem. ",
                    'text': "Ela ainda me olhava como se fosse minha garotinha...",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text':    "Você tentou protegê-la... o que aconteceu com vocês?",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
                {
                    'speaker': 'Cavaleiro',
                    'text':       "...Ela foi mordida. Eu fugi. Como um covarde. Esse antídoto...",
                    'text': "é tudo que consegui antes de... de ser atacado. Por favor... salve ela. Faça o que eu não consegui.",
                    'image': os.path.join("NPC", "NPC_portrait.png")
                },
                {
                    'speaker': 'Heroi',
                    'text':    "Você não vai morrer em vão. Vou tirá-la dessa... nem que eu precise matar cada maldito infectado",
                    'image': os.path.join("SprintHeroi", "heroi.png")
                },
            ]
                
            npc_x = 20.5 * self.TILE_SIZE
            npc_y = 18 * self.TILE_SIZE
            self.npc = NPC(self.game, npc_x, npc_y, dialog_data)
            self.todas_as_sprites.add(self.npc, self.aventureiro)
        else:
            self.npc = None
            if self.aventureiro not in self.todas_as_sprites:
                self.todas_as_sprites.add(self.aventureiro)

    def create_enemies(self):
        self.todas_as_sprites.remove(self.enemies)
        self.enemies.empty()

        enemy_config = get_enemy_config(self.TILE_SIZE).get(self.current_map)

        if enemy_config:
            enemy_class = enemy_config['class']
            for x, y in enemy_config['positions']:
                enemy = enemy_class(self.game, x, y)
                enemy.collision_map = self.collision_map 
                self.enemies.add(enemy)

        self.todas_as_sprites.add(self.enemies)

    def update_camera(self):
        self.camera_x = self.aventureiro.rect.centerx - self.DISPLAY_W // 2
        self.camera_y = self.aventureiro.rect.centery - self.DISPLAY_H // 2
        self.camera_x = max(0, min(self.camera_x, self.mapa_image.get_width() - self.DISPLAY_W))
        self.camera_y = max(0, min(self.camera_y, self.mapa_image.get_height() - self.DISPLAY_H))

    def run(self):
        self.game.playing = True
        
        while self.game.playing:
            self.game.check_events()
            self.handle_input()
            self.update()
            self.render()
            pygame.display.flip()
            self.relogio.tick(60)

    def update(self):
        self.update_camera()
        self.check_enemy_collisions()

        if self.aventureiro.state.startswith('morrendo'):
            self.aventureiro.update()
            if self.aventureiro.is_dead:
                self.play_defeat_cutscene()
                self.reset_game()  # reinicia após cutscene
            return
        
        if self.boss and self.boss.is_dead and not self.boss.already_dead:
            if self.boss.alpha <= 0:
                self.boss.already_dead = True
                self.play_boss_cutscene()
                self.game.playing = False

        if self.aventureiro.rect.right >= self.mapa_image.get_width():
            if self.current_map == 1:
                self.change_map(2)
                self.aventureiro.rect.left = 0
            elif self.current_map == 2:
                self.change_map(3)
                self.aventureiro.rect.left = 0
        elif self.aventureiro.rect.left <= 0:
            if self.current_map == 3:
                self.change_map(2)
                self.aventureiro.rect.right = self.mapa_image.get_width()
            elif self.current_map == 2:
                self.change_map(1)
                self.aventureiro.rect.right = self.mapa_image.get_width()
        
        for sprite in self.todas_as_sprites:
            if isinstance(sprite, (Zumbi, Cachorro, Boss)):
                sprite.update(self.aventureiro.rect)
            elif isinstance(sprite, NPC):
                sprite.update(self.aventureiro.rect)
            else:
                sprite.update()

    def handle_input(self):
        if self.game_over:
            if self.game.START_KEY:
                self.reset_game()
                self.game.START_KEY = False
            return

        if self.npc is not None and self.npc.dialog_active:
            self.som_andando.stop()
            self.aventureiro.stop_walking()
            self.aventureiro.state = 'respirando_direita'
            self.aventureiro.current_frame = 0
            
            if self.game.START_KEY:
                self.npc.update(self.aventureiro.rect)
            return
        
        if self.aventureiro.state.startswith('morrendo'):
            return
        
        keys = pygame.key.get_pressed()
        moving = False
        
        if keys[pygame.K_a]:
            new_x = self.aventureiro.rect.x - self.aventureiro.speed
            if not self.check_collision(new_x, self.aventureiro.rect.y):
                self.aventureiro.walk_left()
                self.aventureiro.rect.x = new_x
                moving = True
        
        elif keys[pygame.K_d]:
            new_x = self.aventureiro.rect.x + self.aventureiro.speed
            if not self.check_collision(new_x, self.aventureiro.rect.y):
                self.aventureiro.walk_right()
                self.aventureiro.rect.x = new_x
                moving = True
        
        elif keys[pygame.K_w]:
            new_y = self.aventureiro.rect.y - self.aventureiro.speed
            if not self.check_collision(self.aventureiro.rect.x, new_y):
                self.aventureiro.walk_up()
                self.aventureiro.rect.y = new_y
                moving = True
        
        elif keys[pygame.K_s]:
            new_y = self.aventureiro.rect.y + self.aventureiro.speed
            if not self.check_collision(self.aventureiro.rect.x, new_y):
                self.aventureiro.walk_down()
                self.aventureiro.rect.y = new_y
                moving = True
        
        if moving:
            if not self.som_andando.get_num_channels() > 0:
                self.som_andando.play(-1)
        else:
            self.som_andando.stop()
            self.aventureiro.stop_walking()
        
        if keys[pygame.K_SPACE]:
            self.aventureiro.attack()
            if not self.som_atacando.get_num_channels() > 0:
                self.som_atacando.play()

    def change_map(self, new_map):
        self.current_map = new_map
        self.collision_map, self.mapa_image = load_map(self.current_map)
        self.create_npc_for_map()
        self.create_enemies()
        
        pygame.mixer.music.stop()
        if self.current_map == 3:
            self.boss_music.play(-1)
            for enemy in self.enemies:
                if isinstance(enemy, Boss):
                    self.boss = enemy
                    break
        else:
            pygame.mixer.music.load(os.path.join("Sons", "MusicaJogo.wav"))
            pygame.mixer.music.play(-1)
            self.boss = None

    def check_collision(self, new_x, new_y):
        collision_rect = self.aventureiro.collision_rect.copy()
        collision_rect.x = new_x + (self.aventureiro.rect.width - collision_rect.width) // 2
        collision_rect.y = new_y + (self.aventureiro.rect.height - collision_rect.height) // 2
        
        corners = [
            (collision_rect.left, collision_rect.top),
            (collision_rect.right, collision_rect.top),
            (collision_rect.left, collision_rect.bottom),
            (collision_rect.right, collision_rect.bottom)
        ]
        
        colliding = False
        
        for corner_x, corner_y in corners:
            tile_x = int(corner_x // self.TILE_SIZE)
            tile_y = int(corner_y // self.TILE_SIZE)
            
            if 0 <= tile_y < len(self.collision_map) and 0 <= tile_x < len(self.collision_map[0]):
                if self.collision_map[tile_y][tile_x] == 1:
                    colliding = True
                    break
        
        if not colliding and self.npc is not None:
            colliding = collision_rect.colliderect(self.npc.collision_rect)
            if colliding:
                self.som_andando.stop()
                
        return colliding

    def check_enemy_collisions(self):
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies:
            if not enemy.is_dead:
                if self.aventureiro.collision_rect.colliderect(enemy.collision_rect):
                    if enemy.attack() and self.aventureiro.take_damage(enemy.damage):
                        print(f"Dano recebido: {enemy.damage}")
                        if self.aventureiro.current_health <= 0:
                            self.handle_player_death()
                
                if (self.aventureiro.state.startswith('atacando') and 
                    int(self.aventureiro.current_frame) == 3 and
                    self.aventureiro.collision_rect.colliderect(enemy.collision_rect) and
                    not enemy.is_taking_damage and
                    current_time - self.aventureiro.last_attack > 500):
                    
                    if enemy.take_damage(self.aventureiro.damage):
                        print(f"Dano causado: {self.aventureiro.damage}")
                        self.aventureiro.last_attack = current_time

    def draw_boss_health_bar(self):
        if not self.boss or self.boss.is_dead:
            return

        bar_width = self.DISPLAY_W - 40
        bar_height = 25
        bar_x = 20
        bar_y = 40

        text_y = 15
        text_x = self.DISPLAY_W // 2

        fill_width = int((self.boss.health / self.boss.max_health) * bar_width)

        self.game.draw_text("BOSS", 22, text_x, text_y)

        pygame.draw.rect(self.display, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.display, (200, 0, 0), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.display, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3)

    def reset_game(self):
        self.game_over = False
        self.current_map = 1
        self.collision_map, self.mapa_image = load_map(self.current_map)
        self.camera_x, self.camera_y = 0, 0
        
        self.aventureiro.current_health = self.aventureiro.max_health
        self.aventureiro.state = 'respirando_direita'
        self.aventureiro.current_frame = 0
        self.aventureiro.rect.center = (self.DISPLAY_W // 2, self.DISPLAY_H // 2)
        
        self.create_npc_for_map()
        self.create_enemies()
        self.play_game_music()

        
    def play_boss_cutscene(self):
        self.display.fill((0, 0, 0))
        pygame.display.flip()

        # Carrega e toca o som da cutscene de vitória
        audio_path = os.path.join("Sons", "SomVitoria.mp3")
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play()
        else:
            print(f"Erro: Arquivo de áudio não encontrado em {audio_path}")

        # Carrega as imagens da cutscene de vitória
        cutscene_folder = os.path.join("Cutscene", "Vitoria")
        if os.path.exists(cutscene_folder):
            images = []
            for img_name in sorted(os.listdir(cutscene_folder)):
                if img_name.endswith((".png", ".jpg")):
                    img_path = os.path.join(cutscene_folder, img_name)
                    try:
                        img = pygame.image.load(img_path).convert()
                        img = pygame.transform.scale(img, (self.DISPLAY_W, self.DISPLAY_H))
                        images.append(img)
                    except:
                        print(f"Erro ao carregar imagem: {img_path}")
                        # Imagem de fallback
                        img = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
                        img.fill((0, 50, 0))  # Verde escuro
                        images.append(img)
            
            # Mostra as imagens em sequência com transições suaves
            frame_duration = 3000  # 3 segundos por imagem
            fade_duration = 500   # 0.5 segundos de fade
            
            for i, img in enumerate(images):
                start_time = pygame.time.get_ticks()
                displaying = True
                
                # Fade in para a primeira imagem
                if i == 0:
                    for alpha in range(0, 255, 5):
                        img.set_alpha(alpha)
                        self.display.blit(img, (0, 0))
                        self.tela.blit(self.display, (0, 0))
                        pygame.display.flip()
                        pygame.time.delay(20)
                
                while displaying:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.game.playing = False
                            return
                        elif event.type == pygame.KEYDOWN:
                            # Permite pular a cutscene
                            displaying = False
                            break
                    
                    self.display.blit(img, (0, 0))
                    self.tela.blit(self.display, (0, 0))
                    pygame.display.flip()
                    
                    current_time = pygame.time.get_ticks()
                    elapsed = current_time - start_time
                    
                    # Fade out no final da imagem (exceto a última)
                    if i < len(images) - 1 and elapsed > frame_duration - fade_duration:
                        alpha = 255 * (1 - (elapsed - (frame_duration - fade_duration)) / fade_duration)
                        img.set_alpha(max(0, int(alpha)))
                    
                    if elapsed >= frame_duration:
                        displaying = False
                    
                    pygame.time.delay(30)
                
                # Fade in para a próxima imagem
                if i < len(images) - 1:
                    next_img = images[i+1]
                    next_img.set_alpha(0)
                    for alpha in range(0, 255, 5):
                        self.display.blit(img, (0, 0))
                        next_img.set_alpha(alpha)
                        self.display.blit(next_img, (0, 0))
                        self.tela.blit(self.display, (0, 0))
                        pygame.display.flip()
                        pygame.time.delay(20)
        else:
            print(f"Pasta da cutscene não encontrada: {cutscene_folder}")
            # Fallback simples
            self.game.draw_text("VITÓRIA", 50, self.DISPLAY_W//2, self.DISPLAY_H//2)
            pygame.display.flip()
            pygame.time.delay(3000)

        # Após a cutscene, mostra a tela de créditos/final
        self.game.draw_text("FIM DE JOGO", 40, self.DISPLAY_W // 2, self.DISPLAY_H - 60)
        pygame.display.update()
        pygame.time.delay(4000)
        self.game.playing = False
        
    def play_defeat_cutscene(self):
        self.display.fill((0, 0, 0))
        pygame.display.flip()
        
        audio_path = os.path.join("Sons", "SomLose.mp3")
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play()
        else:
            print(f"Erro: Arquivo de áudio não encontrado em {audio_path}")

        cutscene_folder = os.path.join("Lose", "lose")
        if os.path.exists(cutscene_folder):
            images = []
            for img_name in sorted(os.listdir(cutscene_folder)):
                if img_name.endswith((".jpg")):
                    img_path = os.path.join(cutscene_folder, img_name)
                    try:
                        img = pygame.image.load(img_path).convert()
                        img = pygame.transform.scale(img, (self.DISPLAY_W, self.DISPLAY_H))
                        images.append(img)
                    except:
                        print(f"Erro ao carregar imagem: {img_path}")

            frame_duration = 3000

            for img in images:
                start_time = pygame.time.get_ticks()
                displaying = True

                while displaying:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.game.playing = False
                            return
                        elif event.type == pygame.KEYDOWN:
                            displaying = False
                            break

                    self.display.blit(img, (0, 0))
                    self.tela.blit(self.display, (0, 0))
                    pygame.display.flip()

                    if pygame.time.get_ticks() - start_time >= frame_duration:
                        displaying = False

                    pygame.time.delay(30)
        else:
            self.game.draw_text("VOCÊ MORREU", 50, self.DISPLAY_W // 2, self.DISPLAY_H // 2)
            pygame.display.flip()
            pygame.time.delay(3000)

        self.game_over = True