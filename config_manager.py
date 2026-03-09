import json
import os

def get_app_data_dir(app_name: str) -> str:
    """
    Возвращает папку для хранения данных приложения:
    C:\\Users\\<User>\\AppData\\Local\\<app_name>
    """
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = os.path.expanduser("~")
    path = os.path.join(base, app_name)
    os.makedirs(path, exist_ok=True)
    return path


class ConfigManager:
    """
    Сохраняет и загружает настройки параметров для конкретного устройства OwenCloud.
    Файл лежит в:
    %LOCALAPPDATA%\\Thermovizor_SCADA\\configs\\device_<ID>.json
    """
    def __init__(self, device_id: int):
        app_root = get_app_data_dir("Thermovizor_SCADA")

        self.config_dir = os.path.join(app_root, "configs")
        os.makedirs(self.config_dir, exist_ok=True)

        self.path = os.path.join(self.config_dir, f"device_{device_id}.json")

    def load(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, config: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
