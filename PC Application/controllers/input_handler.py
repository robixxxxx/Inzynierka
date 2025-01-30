import pygame
import struct
from models.control_data_model import ControlDataModel
from controllers.settings_manager import SettingsManager

class InputHandler:
    def __init__(self, settings_manager: SettingsManager, control_data_model: ControlDataModel):
        self.settings_manager = settings_manager
        self.joystick = self.settings_manager.get_selected_controller()
        self.control_data = control_data_model
        self.selected_controller_index = settings_manager.selected_controller_index  # Default to 0 if not specified
        self.initialize_joystick(self.selected_controller_index)
        self.direction = 0  # 0: neutral, 1: forward, -1: reverse
        self.controller_config = settings_manager.get_controller_config()
        self.logitech_device = False

        self.shift_up_last_state = 0
        self.shift_down_last_states_state = 0
        self.lights_last_state = 0
        self.shift_up_last_state = 0
        self.shift_down_last_state = 0
        self.lights_last_state = 0

        self.gear = 0
        self.buttons = [0] * 12
        self.functions = [0] * 8

    def initialize_joystick(self, selected_controller_index=None):
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        self.selected_controller_index = selected_controller_index
        try:
            if joystick_count > 0 and self.selected_controller_index < joystick_count:
                self.joystick = pygame.joystick.Joystick(self.selected_controller_index)
                self.joystick.init()
                print(f"Joystick initialized: {self.joystick.get_name()}")
                self.logitech_device = self.settings_manager.is_logitech_device(self.selected_controller_index)
                print(f"logi dev: {self.logitech_device}")

            else:
                print(f"No joystick found or invalid controller index: {self.selected_controller_index}")
        except:
            print(f"No joystick found or invalid controller index: {self.selected_controller_index}")

    def update_control_data(self):
        if self.joystick != None:
            self._pygame_joystick_data()
        else:
            self._keyboard_data()

    def _pygame_joystick_data(self):
        pygame.event.pump()
        try:
            steering = self.joystick.get_axis(self.controller_config["steering"]["id"])
        except KeyError:
            print("Warning: 'steering' axis not configured in controller_config")
        try:
            throttle = self.joystick.get_axis(self.controller_config["throttle"]["id"])
        except KeyError:
            print("Warning: 'throttle' axis not configured in controller_config")
        try:
            brake = self.joystick.get_axis(self.controller_config["brake"]["id"])
        except KeyError:
            print("Warning: 'brake' axis not configured in controller_config")
        # Apply axis inversion
        if self.settings_manager.get_axis_inversion("steering"):
            steering *= -1
        if self.settings_manager.get_axis_inversion("throttle"):
            throttle *= -1
        if self.settings_manager.get_axis_inversion("brake"):
            brake *= -1
        for i in range(self.joystick.get_numbuttons()):
            self.buttons[i] = self.joystick.get_button(i)
        if "shift_up" in self.controller_config:
            shift_up_id = self.controller_config["shift_up"]["id"]
            if self.buttons[shift_up_id] and self.buttons[shift_up_id] != self.shift_up_last_state:
                self.gear = min(5, self.gear + 1)
            self.shift_up_last_state = self.buttons[shift_up_id]

        if "shift_down" in self.controller_config:
            shift_down_id = self.controller_config["shift_down"]["id"]
            if self.buttons[shift_down_id] and self.buttons[shift_down_id] != self.shift_down_last_states_state:
                self.gear = max(-1, self.gear - 1)
            self.shift_down_last_states_state = self.buttons[shift_down_id]

        if "lights" in self.controller_config:
            lights_id = self.controller_config["lights"]["id"]
            if self.buttons[lights_id] and self.buttons[lights_id] != self.lights_last_state:
                self.functions[0] = not self.functions[0]
            self.lights_last_state = self.buttons[lights_id]

        if "horn" in self.controller_config:
            horn_id = self.controller_config["horn"]["id"]
            if self.buttons[horn_id]:
                self.functions[1] = 1
            else:
                self.functions[1] = 0

        self.control_data.update(self.gear, steering, throttle, brake, self.functions)

    def _keyboard_data(self):
        keys = pygame.key.get_pressed()
        buttons = [0] * 12
        if keys[pygame.K_LEFT]:
            steering = -1.0
        elif keys[pygame.K_RIGHT]:
            steering = 1.0
        else:
            steering = 0.0

        if keys[pygame.K_UP]:
            throttle = 1.0
        else:
            throttle = 0.0
        if keys[pygame.K_DOWN]:
            brake = 1.0
        else:
            brake = 0.0

        w_state = keys[pygame.K_w]
        s_state = keys[pygame.K_s]
        if self.shift_up_last_state != w_state and w_state:
            gear = min(5, self.control_data.gear + 1)
        elif self.shift_down_last_states_state != s_state and s_state:
            gear = max(-1, self.control_data.gear - 1)
        if keys[pygame.K_h]:
            self.buttons[0] = 1
        else:
            self.buttons[0] = 0
        l_state = keys[pygame.K_l]
        if self.lights_last_state != l_state and l_state:
            self.buttons[1] != self.buttons[1]
        
        self.lights_last_state = l_state
        self.shift_up_last_state = w_state
        self.shift_down_last_state = s_state

        self.control_data.update(steering, throttle, brake, gear, buttons)

    def get_axis_value(self, axis_name):
        try:
            if self.joystick and axis_name in self.controller_config:
                return self.joystick.get_axis(self.controller_config[axis_name]["id"])
            return 0.0
        except Exception as e:
            print(f"Warning: exception error {e}")
            return 0.0
        