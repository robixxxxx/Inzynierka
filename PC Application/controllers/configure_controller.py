import pygame
from views.configure_controller_view import ConfigureControllerView
from controllers.input_handler import InputHandler
from models.settings_manager import SettingsManager
from models.control_data_model import ControlDataModel
import logidrivepy
import time

class ConfigureControllerController:
    def __init__(self, screen, font, settings_manager:SettingsManager):
        self.screen = screen
        self.font = font
        self.settings_manager = settings_manager
        self.settings_view = ConfigureControllerView(screen, font)
        self.selected_option = 0
        self.function_descriptions = {
            "steering": "Skręcanie",
            "throttle": "Gaz",
            "brake": "Hamulec",
            "shift_up": "Zmiana biegu w górę",
            "shift_down": "Zmiana biegu w dół",
            "lights": "Przełącz światła",
            "horn": "Klakson"
        }
        self.functions = list(self.function_descriptions.keys())  # Use descriptions keys to avoid duplicates
        self.is_setting_function = False
        self.is_listening = False
        self.current_function = None
        self.input_handler = InputHandler(self.settings_manager, ControlDataModel())
        self.is_logitech_device = self.settings_manager.is_logitech_device(self.settings_manager.selected_controller_index)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
                
                if self.is_listening:
                    if event.type == pygame.JOYBUTTONDOWN:
                        self._assign_current_function("button", event.button)
                    elif event.type == pygame.JOYAXISMOTION:
                        if abs(event.value) > 0.5:
                            self._assign_current_function("axis", event.axis)
                    elif event.type == pygame.JOYHATMOTION:
                        if event.value != (0, 0):
                            self._assign_current_function("hat", 0)
                
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % (len(self.functions) + 6)
                        elif event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % (len(self.functions) + 6)
                        elif event.key == pygame.K_RETURN:
                            if self.selected_option < len(self.functions):
                                self.current_function = self.functions[self.selected_option]
                                self.is_listening = True
                                print(f"Konfiguruj funkcję: {self.current_function}. Naciśnij przycisk/porusz osią/hat.")
                            elif self.selected_option == len(self.functions):
                                self._change_controller()
                            elif self.selected_option == len(self.functions) + 1:
                                self._toggle_axis_inversion("steering")
                            elif self.selected_option == len(self.functions) + 2:
                                self._toggle_axis_inversion("throttle")
                            elif self.selected_option == len(self.functions) + 3:
                                self._toggle_axis_inversion("brake")
                            elif self.selected_option == len(self.functions) + 4 and self.is_logitech_device:
                                self._test_force_feedback()
                            elif self.selected_option == len(self.functions) + 5:
                                running = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            self._render_view()
            clock.tick(30)
        return

    def _assign_current_function(self, input_type, input_id):
        if self.current_function is not None:
            self.settings_manager.assign_mapping(self.current_function, input_type, input_id)
            print(f"Przypisano {self.current_function} do {input_type} {input_id}")
        self.is_listening = False
        self.current_function = None

    def _toggle_axis_inversion(self, axis_name):
        current_inversion = self.settings_manager.get_axis_inversion(axis_name)
        self.settings_manager.set_axis_inversion(axis_name, not current_inversion)
        print(f"Inversion for {axis_name}: {'Enabled' if not current_inversion else 'Disabled'}")

    def _change_controller(self):
        self.settings_manager.selected_controller_index = (
            self.settings_manager.selected_controller_index + 1
        ) % len(self.settings_manager.get_controllers())
        self.settings_manager.set_selected_controller_index(self.settings_manager.selected_controller_index)
        self.input_handler.initialize_joystick(self.settings_manager.selected_controller_index)
        print(f"Selected controller changed to: {self.settings_manager.get_controller_name()}")

    def _render_view(self):
        config = self.settings_manager.get_controller_config()
        axis_values = {
            "steering": self._get_inverted_axis_value("steering"),
            "throttle": self._get_inverted_axis_value("throttle"),
            "brake": self._get_inverted_axis_value("brake")
        }
        self.settings_view.render_settings(
            functions=self.functions,
            function_descriptions=self.function_descriptions,
            controllers=self.settings_manager.get_controllers(),
            control_mappings=self._format_control_mappings(config),
            selected_controller_index=self.settings_manager.selected_controller_index,
            selected_option=self.selected_option,
            is_setting_function=self.is_listening,
            axis_inversion=self.settings_manager.axis_inversion,
            axis_values=axis_values,
            is_logitech_device=self.is_logitech_device
        )

    def _get_inverted_axis_value(self, axis_name):
        value = self.input_handler.get_axis_value(axis_name)
        if self.settings_manager.get_axis_inversion(axis_name):
            value *= -1
        return value

    def _format_control_mappings(self, config):
        mappings = {}
        for f in self.functions:
            mapping = config.get(f)
            if isinstance(mapping, dict):
                mappings[f] = f"{mapping['type']} {mapping['id']}"
            else:
                mappings[f] = "Nieprzypisane"
        return mappings

    def _test_force_feedback(self):
        if self.is_logitech_device:
            try:
                self.logitech_controller = logidrivepy.LogitechController()
                self.logitech_controller.steering_initialize()
                self.logitech_controller.LogiPlaySpringForce(self.settings_manager.selected_controller_index, 0, 50, 40)
                self.logitech_controller.logi_update()
                time.sleep(2)
                self.logitech_controller.steering_shutdown()
                print("Force feedback test completed.")
            except Exception as e:
                print(f"Error testing force feedback: {e}")
