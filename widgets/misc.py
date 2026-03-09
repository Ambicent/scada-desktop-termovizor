from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class IconCircle(QFrame):
    """Иконка-заглушка - круглый блок с текстовой пиктограммой."""

    def __init__(self, inner_text: str = ""):
        super().__init__()
        self.setFixedSize(36, 36)
        self.setStyleSheet("""
            QFrame {
                background-color: #2C3136;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(inner_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #E0E0E0; font-size: 10pt;")
        layout.addWidget(label)