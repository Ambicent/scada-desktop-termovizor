import json
import os
from typing import Optional, Tuple

# Автологин
class AuthStorage:
    FILE_PATH = os.path.join("data", "auth.json")

    @classmethod
    def load(cls) -> Tuple[Optional[str], Optional[str]]:
        if not os.path.exists(cls.FILE_PATH):
            return None, None

        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("login"), data.get("password")
        except Exception:
            return None, None

    @classmethod
    def save(cls, login: str, password: str):
        os.makedirs("data", exist_ok=True)
        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {"login": login, "password": password},
                f,
                ensure_ascii=False,
                indent=2
            )

    @classmethod
    def clear(cls):
        if os.path.exists(cls.FILE_PATH):
            os.remove(cls.FILE_PATH)
