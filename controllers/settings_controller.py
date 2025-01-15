import pygame
from models.settings_model import Settings
from controllers.configure_controller import ConfigureControllerController
from utils import initialize_pygame
from views.settings_view import SettingsView

class SettingsController:
    def __init__(self, screen, font, settings_manager: Settings):
        self.screen = screen
        self.font = font
        self.settings_manager = settings_manager
        self.settings_view = SettingsView(screen, font)
        self.setting_descriptions = {
            "resolution": "Resolution",
            "fullscreen": "Fullscreen",
            "controller_config": "Configure Controller",
            "return": "Back"
        }
        self.selected_option = 0
        self.running = False
        self._update_options()

    def __del__(self):
        try:
            self.settings_manager.save_settings()
        except Exception as e:
            print(f"Error saving settings: {e}")

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        self._handle_option(self.selected_option)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            self.settings_view.render(self.options, self.selected_option)
            clock.tick(30)

    def _handle_option(self, option_index):
        if option_index == 0:
            self._change_resolution()
        elif option_index == 1:
            self._toggle_fullscreen()
        elif option_index == 2:
            self._configure_controller()
        elif option_index == 3:
            self.running = False

    def _change_resolution(self):
        current_resolution = self.settings_manager.get("resolution", (800, 600))
        resolutions = pygame.display.list_modes()
        if current_resolution not in resolutions:
            resolutions.append(current_resolution)
        current_index = resolutions.index(current_resolution)
        new_index = (current_index + 1) % len(resolutions)
        new_resolution = resolutions[new_index]
        self.settings_manager.set_resolution(new_resolution)
        self._update_options()
        self._adjust_font_size(new_resolution)
        self._reinitialize_display()
        print(f"Resolution changed to: {new_resolution}")

    def _adjust_font_size(self, resolution):
        width, height = resolution
        new_font_size = max(12, int(height / 30))  # Example calculation for font size
        self.font = pygame.font.Font(None, new_font_size)
        self.settings_view.font = self.font

    def _toggle_fullscreen(self):
        self.settings_manager.toggle_fullscreen()
        self._update_options()
        self._reinitialize_display()
        print(f"Fullscreen mode: {'Enabled' if self.settings_manager.get('fullscreen', False) else 'Disabled'}")

    def _configure_controller(self):
        ConfigureControllerController(self.screen, self.font, self.settings_manager).run()

    def _update_options(self):
        resolution = f"{self.settings_manager.get('resolution')[0]}x{self.settings_manager.get('resolution')[1]}"
        fullscreen = "YES" if self.settings_manager.get('fullscreen') else "NO"
        self.options = [
            f"{self.setting_descriptions['resolution']}: {resolution}",
            f"{self.setting_descriptions['fullscreen']}: {fullscreen}",
            self.setting_descriptions['controller_config'],
            self.setting_descriptions['return']
        ]

    def _reinitialize_display(self):
        self.screen, self.font = initialize_pygame(self.settings_manager)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_option]
            elif event.key == pygame.K_ESCAPE:
                self.running = False
        return None