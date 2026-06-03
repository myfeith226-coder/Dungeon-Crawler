import pygame

pygame.init()
pygame.mixer.init()
MONITOR_INFO = pygame.display.Info()
SCREEN_WIDTH = MONITOR_INFO.current_w
SCREEN_HEIGHT = MONITOR_INFO.current_h

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Soul Knight Style - Tile Indexing System")

