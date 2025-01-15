import pygame
import json
import logidrivepy

class SettingsManager:
    def __init__(self, settings_file):
        pygame.joystick.init()
        self.settings_file = settings_file
        self.settings = self.load_settings()
        self.axis_inversion = self.settings.get("axis_inversion", {
            "steering": False,
            "throttle": False,
            "brake": False
        })
        self.joysticks = []
        self.selected_controller_index = self.settings.get("selected_controller_index", 0)
        self.initialize_joysticks()

    def initialize_joysticks(self):
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)

        # Ensure the selected controller is valid
        if not self.joysticks or self.selected_controller_index >= len(self.joysticks):
            self.selected_controller_index = 0 if self.joysticks else None

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Settings file {self.settings_file} not found. Using default settings.")
            return {}

    def save_settings(self):
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def set_resolution(self, resolution):
        self.settings["resolution"] = resolution

    def toggle_fullscreen(self):
        self.settings["fullscreen"] = not self.settings["fullscreen"]

    def get_controllers(self):
        return [joystick.get_name() for joystick in self.joysticks]

    def assign_mapping(self, function_name, input_type, input_id):
        if "controller_config" not in self.settings:
            self.settings["controller_config"] = {}

        self.settings["controller_config"][function_name] = {
            "type": input_type,
            "id": input_id
        }
        self.save_settings()
    
    def get_controller_config(self):
        return self.settings.get("controller_config", {})

    def is_logitech_device(self, index:int):
        try:
            controller = logidrivepy.LogitechController()
            controller.steering_initialize()
            is_logitech = controller.LogiIsManufacturerConnected(int(index), controller.LOGI_MANUFACTURER_LOGITECH)
            controller.steering_shutdown()
            return is_logitech
        except Exception as e:
            print(f"Error checking if device is Logitech: {e}")
            return False

    def get_axis_inversion(self, axis_name):
        return self.axis_inversion.get(axis_name, False)

    def set_axis_inversion(self, axis_name, inverted):
        self.axis_inversion[axis_name] = inverted
        self.settings["axis_inversion"] = self.axis_inversion
        self.save_settings()

    def set_selected_controller_index(self, index):
        self.selected_controller_index = index
        self.settings["selected_controller_index"] = index
        self.save_settings()

    def get_selected_controller(self):
        if self.joysticks and self.selected_controller_index is not None and self.selected_controller_index < len(self.joysticks):
            return self.joysticks[self.selected_controller_index]
        return None

    def get_controller_name(self):
        if self.selected_controller_index is not None and self.selected_controller_index < len(self.joysticks):
            return self.joysticks[self.selected_controller_index].get_name()
        return "No controller selected"