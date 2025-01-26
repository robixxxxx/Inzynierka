import pygame
from consts import *

class ConfigureControllerView:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.background_color = RAL9017
        self.text_color = BLACK
        self.highlight_color = RAL5014

    def render_settings(
        self,
        functions,
        function_descriptions,
        controllers,
        control_mappings,
        selected_controller_index,
        selected_option,
        is_setting_function,
        axis_inversion,
        axis_values,
        is_logitech_device
    ):
        self.screen.fill(self.background_color)
        width, height = self.screen.get_size()
        scale = height / 768

        text_height = self.font.size("Tg")[1]
        spacing = text_height + 10 * scale

        y_offset = 50
        for i, function in enumerate(functions):
            color = self.highlight_color if i == selected_option and not is_setting_function else self.text_color
            description = function_descriptions.get(function, function)
            mapping = control_mappings[function] 
            text = self.font.render(f"{description}: {mapping}", True, color)
            self.screen.blit(text, (50, y_offset))
            y_offset += spacing

        # Separate label for controllers
        y_offset += 20
        controller_label = self.font.render("Kontrolery:", True, (255, 255, 255))
        self.screen.blit(controller_label, (50, y_offset))
        y_offset += spacing

        # Display selected controller
        controller_text = f"Kontroler: {controllers[selected_controller_index]}" if controllers else "Brak kontrolerów"
        color = self.highlight_color if selected_option == len(functions) and not is_setting_function else self.text_color
        text = self.font.render(controller_text, True, color)
        self.screen.blit(text, (50, y_offset))
        y_offset += spacing

        # Separate label for axis inversion options
        y_offset += 20
        inversion_label = self.font.render("Inwersja osi:", True, (255, 255, 255))
        self.screen.blit(inversion_label, (50, y_offset))
        y_offset += spacing

        # Display axis inversion options
        for i, axis in enumerate(["steering", "throttle", "brake"]):
            inversion_text = f"Inwersja {axis}: {'TAK' if axis_inversion.get(axis, False) else 'NIE'}"
            color = self.highlight_color if selected_option == len(functions) + i + 1 and not is_setting_function else self.text_color
            text = self.font.render(inversion_text, True, color)
            self.screen.blit(text, (50, y_offset))
            y_offset += spacing

        # Separate label for exit option
        y_offset += 20
        exit_label = self.font.render("Opcje:", True, (255, 255, 255))
        self.screen.blit(exit_label, (50, y_offset))
        y_offset += spacing

        exit_text = "Powrót"
        color = self.highlight_color if selected_option == len(functions) + 5 and not is_setting_function else self.text_color
        text = self.font.render(exit_text, True, color)
        self.screen.blit(text, (50, y_offset))

        # If waiting for button/axis press
        if is_setting_function:
            info_text = self.font.render("Naciśnij przycisk / porusz osią / hat na kontrolerze...", True, (255,255,255))
            self.screen.blit(info_text, (50, y_offset+spacing))

        # Draw axis visualizations
        self.draw_axis_visualizations(axis_values)

        pygame.display.flip()

    def draw_axis_visualizations(self, axis_values):
        width, height = self.screen.get_size()
        center_x = width // 2
        center_y = height // 2

        # Draw steering axis visualization
        steering_value = axis_values.get("steering", 0.0)
        steering_rect = pygame.Rect(center_x - 150, 50, 300, 20)
        pygame.draw.rect(self.screen, GRAY, steering_rect)
        steering_pos = int((steering_value + 1) / 2 * 300)
        pygame.draw.rect(self.screen, RED, (center_x - 150 + steering_pos, 50, 10, 20))

        # Draw throttle axis visualization
        throttle_value = axis_values.get("throttle", 0.0)
        throttle_rect = pygame.Rect(center_x - 150, 90, 300, 20)
        pygame.draw.rect(self.screen, GRAY, throttle_rect)
        throttle_pos = int((throttle_value + 1) / 2 * 300)
        pygame.draw.rect(self.screen, GREEN, (center_x - 150 + throttle_pos, 90, 10, 20))

        # Draw brake axis visualization
        brake_value = axis_values.get("brake", 0.0)
        brake_rect = pygame.Rect(center_x - 150, 130, 300, 20)
        pygame.draw.rect(self.screen, GRAY, brake_rect)
        brake_pos = int((brake_value + 1) / 2 * 300)
        pygame.draw.rect(self.screen, BLUE, (center_x - 150 + brake_pos, 130, 10, 20))