import pygame
from consts import *

class SettingsView:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.background_color = RAL9017
        self.text_color = BLACK
        self.highlight_color = RAL5014

    def render(self, options, selected_index):
        self.screen.fill(self.background_color)
        width, height = self.screen.get_size()
        scale = height / 768  # Assuming 768 is the base height for scaling

        # Calculate the spacing based on the font size
        text_height = self.font.size("Tg")[1]
        spacing = text_height + 10 * scale  # Add some extra spacing

        for i, option in enumerate(options):
            color = self.highlight_color if i == selected_index else self.text_color
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(width // 2, height // 2 - (len(options) // 2 - i) * spacing))
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()