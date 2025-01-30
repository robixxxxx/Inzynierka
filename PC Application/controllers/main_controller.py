import pygame
from views.menu_view import MenuView
from controllers.device_controller import DeviceController
from controllers.settings_controller import SettingsController
from controllers.communication_controller import CommunicationController

class MainController:
    def __init__(self, screen, font, settings_manager):
        self.screen = screen
        self.font = font
        self.menu_view = MenuView(screen, font)
        self.settings_manager = settings_manager
        self.menu_items = ["Szukanie pojazdów", "Ustawienia", "Wyjście"]
        self.selected_index = 0

    def run(self):
        while True:
            self.menu_view.render(self.menu_items, self.selected_index)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_index == 0:
                            result = self.run_device_discovery()
                            if result == "exit_to_menu":
                                continue
                        elif self.selected_index == 1:
                            self.run_settings()
                        elif self.selected_index == 2:
                            pygame.quit()
                            return

    def run_device_discovery(self):
        device_discovery_controller = DeviceController(self.screen, self.font, self.settings_manager)
        device_discovery_controller.run()

    def run_settings(self):
        settings_controller = SettingsController(self.screen, self.font, self.settings_manager)
        settings_controller.run()
