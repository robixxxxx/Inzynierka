import logidrivepy
import sys
sys.path.append('../logidrivepy')

class ForceFeedbackController:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.controller_index = settings_manager.selected_controller_index
        self.logitech_controller = None
        self.initialize_logitech_controller()

    def is_logitech_controller(self):
        return self.logitech_controller

    def initialize_logitech_controller(self):
        if self.settings_manager.is_logitech_device(self.controller_index):
            self.logitech_controller = logidrivepy.LogitechController()
            if self.logitech_controller.steering_initialize():
                print("Logitech controller initialized for force feedback.")
            else:
                print("Failed to initialize Logitech controller for force feedback.")
                self.logitech_controller = None

    def update_force_feedback(self, acceleration_x, acceleration_y, acceleration_z):
        if not self.logitech_controller:
            print("Logitech controller is not initialized. Skipping force feedback update.")
            return

        try:
            spring_force = int(acceleration_y + (acceleration_x - 9.81) * 100)

            # Walidacja wartości przed użyciem w metodach
            if not (-100 <= spring_force <= 100):
                print(f"Spring force out of bounds: {spring_force}")
                spring_force = max(-100, min(100, spring_force))

            # print(f"Setting spring force: {spring_force}")
            self.logitech_controller.LogiPlaySpringForce(self.controller_index, 0, spring_force, 40)

            # print(f"Setting constant force: {int(acceleration_z * 10)}")
            self.logitech_controller.LogiPlayConstantForce(self.controller_index, int(acceleration_z * 10))

            self.logitech_controller.logi_update()
        except Exception as e:
            print(f"Error updating force feedback: {e}")



    def shutdown(self):
        if self.logitech_controller:
            self.logitech_controller.steering_shutdown()