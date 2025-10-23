import configparser
import os
from pathlib import Path
import threading

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.config_path = Path.home() / ".config" / "aspi_shell" / "config.ini"
        self.config = configparser.ConfigParser()
        self._loaded = False

    def load(self):
        """Загружает конфигурацию из файла или создает его по умолчанию."""
        if not self.config_path.exists():
            self._create_default_config()
        
        self.config.read(self.config_path)
        self._loaded = True

    def get(self, section, key, fallback=None):
        """Получает значение из конфигурации."""
        if not self._loaded:
            self.load()
        return self.config.get(section, key, fallback=fallback)

    def _create_default_config(self):
        """Создает директорию и файл конфигурации по умолчанию."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = configparser.ConfigParser()
        
        # Секция аудио
        default_config['audio'] = {
            'hidden_devices': ''
        }

        with open(self.config_path, 'w') as configfile:
            configfile.write("# --- Audio Settings ---\n")
            configfile.write("# A comma-separated list of device names (or parts of names) to hide from the selector.\n")
            configfile.write("# Example: hidden_devices = Monitor,HDMI\n\n")
            default_config.write(configfile)

# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
