import pygame
from game import Game

pygame.init()

g = Game()

while g.running:
    if g.playing:
        g.game_loop()
    elif g.curr_menu:
        g.curr_menu.display_menu()

pygame.quit()