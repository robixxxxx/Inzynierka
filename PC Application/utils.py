import pygame

def initialize_pygame(settings_manager):
    pygame.init()
    resolution = settings_manager.get("resolution", (800, 600))
    fullscreen = settings_manager.get("fullscreen", False)
    pygame.display.set_caption("Your Game Title")
    flag = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode(resolution, flag)
    base_font_size = 36  # Base font size for a reference height (e.g., 768)
    screen_width, screen_height = screen.get_size()
    scale_factor = screen_height / 768
    font_size = int(base_font_size * scale_factor)
    font = pygame.font.Font(None, font_size)
    return screen, font