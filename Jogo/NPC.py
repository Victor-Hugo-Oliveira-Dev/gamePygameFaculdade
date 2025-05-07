import pygame
import os

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, dialog_data):
        super().__init__()
        self.game = game
        self.dialog_sounds = []
        self.current_sound = None
        original_image = pygame.image.load(os.path.join("NPC", "NPC.png"))
        self.image = pygame.transform.scale(original_image, (original_image.get_width() * 3, original_image.get_height() * 3))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dialog_triggered = False
        
        # Configurações do diálogo
        self.dialog_config = {
            'box_height': 120,
            'box_color': (40, 40, 60),
            'border_color': (150, 150, 200),
            'border_width': 4,
            'text_color': (255, 255, 255),
            'continue_color': (180, 180, 180),
            'font_size': 26,
            'portrait_size': (90, 90),
            'padding': 20
        }
        
        
        self.confirmation_image = pygame.image.load(os.path.join("item", "antidoto.png"))  # Substitua pelo caminho correto
        self.confirmation_image = pygame.transform.scale(self.confirmation_image, (60, 60))  # Ajuste o tamanho conforme necessário
        #self.dialog_end_sound = pygame.mixer.Sound(os.path.join("Sons", "dialog_end.wav"))  # Substitua pelo caminho correto
        
        self.show_confirmation = False
        self.confirmation_timer = 0
        self.confirmation_duration = 3000  
        
        self.collision_rect = pygame.Rect(0, 0, self.rect.width * 0.6, self.rect.height * 0.6)
        self.collision_rect.center = self.rect.center
        
        self.interaction_rect = pygame.Rect(0, 0, self.rect.width * 1.5, self.rect.height * 1.5)
        self.interaction_rect.center = self.rect.center
        
        self.dialog_data = dialog_data
        self.current_line = 0
        self.dialog_active = False
        self.dialog_completed = False
        
        self.font = pygame.font.Font(None, self.dialog_config['font_size'])
        self.dialog_box_height = self.dialog_config['box_height']
        self.portrait_size = self.dialog_config['portrait_size']

    def update(self, player_rect=None):
        if player_rect is not None and not self.dialog_completed:
            if self.interaction_rect.colliderect(player_rect):
                if not self.dialog_triggered:
                    self.dialog_active = True
                    self.current_line = 0
                    self.dialog_triggered = True
                    if hasattr(self.game, 'som_andando'):
                        self.game.som_andando.stop()
                    # Toca o som da primeira linha
                    self.play_dialog_sound(self.current_line)
                    
                if self.dialog_active and self.game.START_KEY:
                    # Para o som atual antes de avançar
                    self.stop_current_sound()
                    self.current_line += 1
                    if self.current_line >= len(self.dialog_data):
                        self.dialog_active = False
                        self.dialog_completed = True
                        self.show_confirmation = True
                        self.confirmation_timer = pygame.time.get_ticks()
                    else:
                        # Toca o som da nova linha
                        self.play_dialog_sound(self.current_line)
                    self.game.START_KEY = False
            else:
                self.dialog_triggered = False
                if not self.dialog_active:
                    self.current_line = 0
                    self.stop_current_sound()

    def play_dialog_sound(self, line_index):
        """Reproduz o som correspondente à linha de diálogo"""
        self.stop_current_sound()
        if line_index < len(self.dialog_sounds) and self.dialog_sounds[line_index]:
            self.current_sound = self.dialog_sounds[line_index]
            self.current_sound.play()
    
    def stop_current_sound(self):
        """Para o som que está tocando atualmente"""
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None

    def draw_dialog(self, surface):
        if self.dialog_active and self.current_line < len(self.dialog_data):
            current_dialog = self.dialog_data[self.current_line]
            config = self.dialog_config
            dialog_box = pygame.Rect(
                0, 
                self.game.DISPLAY_H - config['box_height'], 
                self.game.DISPLAY_W, 
                config['box_height']
            )
            
            pygame.draw.rect(surface, config['box_color'], dialog_box)
            pygame.draw.rect(surface, config['border_color'], dialog_box, config['border_width'])
            
            try:
                portrait = pygame.transform.scale(
                    pygame.image.load(current_dialog['image']), 
                    config['portrait_size']
                )
                surface.blit(
                    portrait, 
                    (config['padding'], self.game.DISPLAY_H - config['box_height'] + config['padding'])
                )
            except:
                pygame.draw.rect(
                    surface, 
                    (100, 100, 100), 
                    (config['padding'], self.game.DISPLAY_H - config['box_height'] + config['padding'], 
                     *config['portrait_size'])
                )
            
            name_surface = self.font.render(current_dialog['speaker'], True, config['text_color'])
            surface.blit(
                name_surface, 
                (config['portrait_size'][0] + 2*config['padding'], 
                 self.game.DISPLAY_H - config['box_height'] + config['padding'])
            )
            
            text_surface = self.font.render(current_dialog['text'], True, config['text_color'])
            surface.blit(
                text_surface, 
                (config['portrait_size'][0] + 2*config['padding'], 
                 self.game.DISPLAY_H - config['box_height'] + config['padding'] + 30)
            )
            
            continue_surface = self.font.render("Pressione ENTER para continuar...", True, config['continue_color'])
            surface.blit(
                continue_surface, 
                (self.game.DISPLAY_W - 280, self.game.DISPLAY_H - config['padding'])
            )
        
        # Desenha a imagem de confirmação se necessário
        if self.show_confirmation:
            surface.blit(
                self.confirmation_image, 
                (self.game.DISPLAY_W - self.confirmation_image.get_width() - 10, 10)  # Canto superior direito
            )
    
    def load_dialog_sounds(self, sound_files):
        """Carrega os sons para cada linha de diálogo"""
        self.dialog_sounds = []
        for sound_file in sound_files:
            try:
                sound = pygame.mixer.Sound(sound_file)
                self.dialog_sounds.append(sound)
            except:
                print(f"Erro ao carregar som: {sound_file}")
                self.dialog_sounds.append(None)