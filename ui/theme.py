# ui/theme.py
from __future__ import annotations
from PyQt6.QtCore import QSettings
from constants import DARK_THEME_QSS, LIGHT_THEME_QSS


class ThemeManager:
    KEY = "ui/theme"  # "dark" | "light"

    def __init__(self) -> None:
        self.settings = QSettings("Thermovizor", "ThermovizorSCADA")

    def get_theme(self) -> str:
        v = str(self.settings.value(self.KEY, "dark")).lower()
        return "light" if v == "light" else "dark"

    def set_theme(self, theme: str) -> None:
        theme = "light" if str(theme).lower() == "light" else "dark"
        self.settings.setValue(self.KEY, theme)

    def toggle(self) -> str:
        new_theme = "light" if self.get_theme() == "dark" else "dark"
        self.set_theme(new_theme)
        return new_theme

    def apply_to_app(self, app) -> None:
        theme = self.get_theme()
        app.setStyleSheet(LIGHT_THEME_QSS if theme == "light" else DARK_THEME_QSS)