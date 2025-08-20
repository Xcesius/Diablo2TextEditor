import json
import threading

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.lock = threading.Lock()
        # Load initial config
        self.config = self.load_config()

    def _load_config_unlocked(self):
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"settings": {}}

        # Ensure default settings are present
        settings = config.get("settings", {})
        settings.setdefault("multi_column_selection_enabled", False)
        settings.setdefault("ignore_empty_cells_on_column_select", False)
        settings.setdefault("debug_mode_enabled", False)
        # Add the new setting for the frozen column's header
        settings.setdefault("show_row_numbers_on_frozen_column", False)
        # Undo/Redo depth configuration
        settings.setdefault("undo_stack_max_size", 10)
        # Crosshair guides configuration
        settings.setdefault("crosshair_enabled", True)
        settings.setdefault("crosshair_thickness", 1)
        # Add the new setting for freezing the first row
        #settings.setdefault("freeze_first_row_enabled", False)
        config["settings"] = settings
        return config

    def load_config(self):
        with self.lock:
            return self._load_config_unlocked()

    def save_config(self):
        with self.lock:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)

    def get_setting(self, key, default=None):
        with self.lock:
            # Reload config from file to get latest settings
            current_config = self._load_config_unlocked()
            return current_config.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        with self.lock:
            if "settings" not in self.config:
                self.config["settings"] = {}
            self.config["settings"][key] = value
        self.save_config()
