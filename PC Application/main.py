from controllers.main_controller import MainController
from controllers.settings_manager import SettingsManager
from utils import initialize_pygame


def main():
    settings_manager = SettingsManager("settings.json")
    screen, font = initialize_pygame(settings_manager)

    selected_controller = settings_manager.get_selected_controller()
    if selected_controller:
        print(f"Joystick initialized: {settings_manager.get_controller_name()}")
    else:
        print("No joystick found or invalid controller index")

    main_controller = MainController(screen, font, settings_manager)
    main_controller.run()

if __name__ == "__main__":
    main()