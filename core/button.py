import pygame
from core.config import LIGHT_BLUE, BLACK

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen, font):
        pygame.draw.rect(screen, LIGHT_BLUE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)