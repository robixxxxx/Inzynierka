import json

class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.settings = self.load_settings()

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
        self.save_settings()

    def toggle_fullscreen(self):
        self.settings["fullscreen"] = not self.settings.get("fullscreen", False)
        self.save_settings()