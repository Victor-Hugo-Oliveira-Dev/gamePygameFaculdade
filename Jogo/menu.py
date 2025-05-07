import pygame
import os

class Menu():
    def __init__(self, game, *args):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 75, 20)
        self.offset = -100

    def draw_cursor(self):
        self.game.draw_text('*', 17, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 20
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 50
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 80
        self.quitx, self.quity = self.mid_w, self.mid_h + 110
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        pygame.mixer.music.load(os.path.join("Sons", "MusicaMenu.wav"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.bg_frames = []
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()

        for i in range(1, 15):#loping imagem menu
            caminho = os.path.join("ImagensMenu", f"frame-{i:03d}.gif")
            img = pygame.image.load(caminho)
            img = pygame.transform.scale(img, (self.game.DISPLAY_W, self.game.DISPLAY_H))
            self.bg_frames.append(img)
    
    def start_game(self):
        # Para a música do menu imediatamente
        pygame.mixer.music.stop()
        
        # Encerra a exibição do menu
        self.run_display = False
        self.game.curr_menu = None  # Remove o menu atual
        
        # Limpa a tela completamente
        self.game.display.fill((0, 0, 0))
        pygame.display.flip()
        
        print("Preparando para exibir introdução...")
        
        # Chama a introdução diretamente
        intro_completed = self.game.iniciarjogo.play_intro_sequence()
        
        if intro_completed:
            print("Introdução concluída com sucesso!")
            # Inicia o jogo principal após a introdução
            self.game.playing = True
            self.game.curr_menu = self.game.iniciarjogo
        else:
            print("Falha na introdução, iniciando jogo diretamente")
            self.game.playing = True
            self.game.curr_menu = self.game.iniciarjogo

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()

            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.bg_frames)

            self.game.display.blit(self.bg_frames[self.frame_index], (0, 0))
            self.game.draw_text('Menu Principal', 35, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 20)
            self.game.draw_text("Iniciar Jogo", 25, self.startx, self.starty)
            self.game.draw_text("Opcoes", 25, self.optionsx, self.optionsy)
            self.game.draw_text("Creditos", 25, self.creditsx, self.creditsy)
            self.game.draw_text("Sair", 25, self.quitx, self.quity)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        som_cursor = pygame.mixer.Sound(os.path.join("Sons", "MenuClick.wav"))
        if self.game.DOWN_KEY:
            som_cursor.play()
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                self.state = 'Quit'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.game.UP_KEY:
            som_cursor.play()
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                self.state = 'Quit'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'

    def check_input(self):
        som_cursor = pygame.mixer.Sound(os.path.join("Sons", "MenuEnter.wav"))
        self.move_cursor()
        if self.game.START_KEY:
            som_cursor.play()
            if self.state == 'Start':
                self.start_game()
            elif self.state == 'Quit':
                self.game.running = False
                self.run_display = False
            else:
                self.game.curr_menu = getattr(self.game, self.state.lower())
                self.run_display = False

class OptionsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h + 10
        self.controlsx, self.controlsy = self.mid_w, self.mid_h + 40
        self.sairx, self.sairy = self.mid_w, self.mid_h + 70
        self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        self.bg_frames = []
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()
        self.som_click = pygame.mixer.Sound(os.path.join("Sons", "MenuClick.wav"))
        self.som_enter = pygame.mixer.Sound(os.path.join("Sons", "MenuEnter.wav"))
    
        # Carrega os frames de fundo
        for i in range(1, 15):
            caminho = os.path.join("ImagensMenu", f"frame-{i:03d}.gif")
            try:
                img = pygame.image.load(caminho)
                img = pygame.transform.scale(img, (self.game.DISPLAY_W, self.game.DISPLAY_H))
                self.bg_frames.append(img)
            except FileNotFoundError:
                print(f"Erro: Imagem {caminho} não encontrada!")

    def display_menu(self):
        """Exibe o menu de opções e gerencia a animação de fundo."""
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            now = pygame.time.get_ticks()

            # Atualiza o frame da animação de fundo
            if now - self.last_update > self.frame_delay:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.bg_frames)

            # Desenha o frame atual e as opções do menu
            self.game.display.blit(self.bg_frames[self.frame_index], (0, 0))
            self.game.draw_text('OPCOES', 35, self.mid_w, self.mid_h - 30)
            self.game.draw_text("Volume", 25, self.volx, self.voly)
            self.game.draw_text("Controles", 25, self.controlsx, self.controlsy)
            self.game.draw_text("Voltar", 25, self.sairx, self.sairy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        self.som_click.play()
        states = ['Volume', 'Controls', 'Sair']
        current_index = states.index(self.state)
        if self.game.UP_KEY:
            self.state = states[(current_index - 1) % len(states)]
        elif self.game.DOWN_KEY:
            self.state = states[(current_index + 1) % len(states)]
        if self.state == 'Volume':
            self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        elif self.state == 'Controls':
            self.cursor_rect.midtop = (self.controlsx + self.offset, self.controlsy)
        elif self.state == 'Sair':
            self.cursor_rect.midtop = (self.sairx + self.offset, self.sairy)

    def handle_selection(self):
        self.som_enter.play()
        if self.state == 'Volume':
            self.game.curr_menu = self.game.volume_menu
        elif self.state == 'Controls':
            self.game.curr_menu = self.game.controls
        elif self.state == 'Sair':
            self.game.curr_menu = self.game.main_menu
        self.run_display = False

    def check_input(self):
        if self.game.UP_KEY or self.game.DOWN_KEY:
            self.move_cursor()
        elif self.game.START_KEY:
            self.handle_selection()

class ControlsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.bg_frames = []
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()

        for i in range(1, 15):
            caminho = os.path.join("ImagensMenu", f"frame-{i:03d}.gif")
            img = pygame.image.load(caminho)
            img = pygame.transform.scale(img, (self.game.DISPLAY_W, self.game.DISPLAY_H))
            self.bg_frames.append(img)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.options
                self.run_display = False
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.bg_frames)

            self.game.display.blit(self.bg_frames[self.frame_index], (0, 0))

            self.game.draw_text('Controles', 35, self.mid_w, self.mid_h - 40)
            self.game.draw_text('Seta para cima -- andar para cima', 25, self.mid_w, self.mid_h + 0)
            self.game.draw_text('Seta para baixo -- andar para baixo', 25, self.mid_w, self.mid_h + 30)
            self.game.draw_text('Seta para esquerda -- andar para esquerda', 25, self.mid_w, self.mid_h + 60)
            self.game.draw_text('Seta para direita -- andar para direita', 25, self.mid_w, self.mid_h + 90)
            self.game.draw_text('Espaco -- atacar  ', 25, self.mid_w, self.mid_h + 120)
            self.blit_screen()

class VolumeMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.bg_frames = []
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()
        self.load_volume()  # Carrega o volume salvo

        for i in range(1, 15):
            caminho = os.path.join("ImagensMenu", f"frame-{i:03d}.gif")
            try:
                img = pygame.image.load(caminho)
                img = pygame.transform.scale(img, (self.game.DISPLAY_W, self.game.DISPLAY_H))
                self.bg_frames.append(img)
            except pygame.error as e:
                print(f"Error loading image {caminho}: {e}")

        self.volume = 5  # Volume inicial (0 a 10)
        self.max_volume = 10
        self.bar_width = 200
        self.bar_height = 20
        self.bar_x = self.mid_w - self.bar_width // 2
        self.bar_y = self.mid_h + 20
        self.dragging = False

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.frame_delay:
                self.frame_index = (self.frame_index + 1) % len(self.bg_frames)
                self.last_update = current_time

            # Controle do volume com as teclas de seta
            if self.game.LEFT_KEY:
                self.volume = max(0, self.volume - 1)
                self.game.reset_keys()
            elif self.game.RIGHT_KEY:
                self.volume = min(self.max_volume, self.volume + 1)
                self.game.reset_keys()

            # Controle do volume com o mouse
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if mouse_click[0]:  # Botão esquerdo do mouse pressionado
                if self.bar_x <= mouse_pos[0] <= self.bar_x + self.bar_width and self.bar_y <= mouse_pos[1] <= self.bar_y + self.bar_height:
                    self.dragging = True

            if self.dragging:
                if mouse_click[0]:  # Se ainda está pressionado
                    self.volume = int((mouse_pos[0] - self.bar_x) / self.bar_width * self.max_volume)
                    self.volume = max(0, min(self.max_volume, self.volume))
                else:
                    self.dragging = False

            pygame.mixer.music.set_volume(self.volume / self.max_volume)

            if self.game.START_KEY or self.game.BACK_KEY:
                self.save_volume()  # Save volume settings
                self.game.curr_menu = self.game.options
                self.run_display = False

            self.game.display.blit(self.bg_frames[self.frame_index], (0, 0))
            self.game.draw_text('Volume', 35, self.mid_w, self.mid_h - 20)
            pygame.draw.rect(self.game.display, (255, 255, 255), (self.bar_x, self.bar_y, self.bar_width, self.bar_height), 2)
            filled_width = int((self.volume / self.max_volume) * self.bar_width)
            pygame.draw.rect(self.game.display, (255, 255, 255), (self.bar_x, self.bar_y, filled_width, self.bar_height))

            self.blit_screen()

    def save_volume(self):
        try:
            with open("settings.cfg", "w") as file:
                file.write(f"volume={self.volume}")
        except IOError as e:
            print(f"Erro ao salvar o volume: {e}")

    def load_volume(self):
        try:
            with open("settings.cfg", "r") as file:
                for line in file:
                    if line.startswith("volume="):
                        self.volume = int(line.split("=")[1])
        except FileNotFoundError:
            self.volume = 5  # Volume padrão caso o arquivo não exista
        except IOError as e:
            print(f"Erro ao carregar o volume: {e}")

class CreditsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)

        self.bg_frames = []
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()

        for i in range(1, 15):
            caminho = os.path.join("ImagensMenu", f"frame-{i:03d}.gif")
            img = pygame.image.load(caminho)
            img = pygame.transform.scale(img, (self.game.DISPLAY_W, self.game.DISPLAY_H))
            self.bg_frames.append(img)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False

            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.bg_frames)

            self.game.display.blit(self.bg_frames[self.frame_index], (0, 0))

            self.game.draw_text('Creditos', 35, self.mid_w, self.mid_h - 40)
            self.game.draw_text('Caio', 25, self.mid_w, self.mid_h + 0)
            self.game.draw_text('Derik', 25, self.mid_w, self.mid_h + 30)
            self.game.draw_text('Karine', 25, self.mid_w, self.mid_h + 60)
            self.game.draw_text('Victor Hugo', 25, self.mid_w, self.mid_h + 90)
            self.blit_screen()