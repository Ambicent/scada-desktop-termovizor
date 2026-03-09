from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional
from widgets.misc import IconCircle


class BadgeLabel(QLabel):
    """Цветная квадратная метка статуса."""

    def __init__(self, text: str, color: str):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: black;
                border-radius: 8px;
                padding: 2px 6px;
                font-size: 9pt;
            }}
        """)


class StatusCard(QFrame):
    """Карточка параметра / насоса."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        value: Optional[str] = None,
        unit: str = "",
        status_text: Optional[str] = None,
        status_color: str = "#4CAF50",
        icon_text: str = "",
    ):
        super().__init__()

        self._unit = unit

        self.setObjectName("Card")
        self.setStyleSheet("")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Иконка
        icon = IconCircle(icon_text)
        main_layout.addWidget(icon)

        # Левая текстовая зона
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(self.title_label)

        self.value_label = QLabel("")
        self.value_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(self.value_label)

        if value is not None:
            self.value_label.setText(f"{value} {unit}".strip())
        else:
            self.value_label.hide()

        main_layout.addLayout(text_layout, 1)

        self.badge_label: Optional[BadgeLabel] = None
        if status_text:
            self.badge_label = BadgeLabel(status_text, status_color)
            self.badge_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(self.badge_label)

    def update_card(
        self,
        *,
        title: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        status: Optional[str] = None,
        color: Optional[str] = None,
    ):
        if title is not None:
            self.title_label.setText(title)

        if value is not None:
            if unit is not None:
                self._unit = unit
            self.value_label.setText(f"{value:.2f} {self._unit}".strip())
            self.value_label.show()

        if status is not None:
            if self.badge_label is None:
                self.badge_label = BadgeLabel(status, color or "#9E9E9E")
                self.badge_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.layout().addWidget(self.badge_label)

            self.badge_label.setText(status)

            if color is not None:
                self.badge_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {color};
                        color: black;
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 9pt;
                    }}
                """)

