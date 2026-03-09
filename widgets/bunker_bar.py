from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt


class BunkerBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(22)
        self._percent = 0.0

        self.bar = QFrame(self)
        self.bar.setStyleSheet("""
            QFrame {
                background-color: #3A3F45;
                border-radius: 4px;
            }
        """)
        self.bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bar.setFixedHeight(16)

        self.fill = QFrame(self.bar)
        self.fill.setFixedHeight(16)

        self.label = QLabel("0 %")
        self.label.setFixedWidth(42)
        self.label.setStyleSheet("color: #FFFFFF; font-size: 9pt;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.label, 0)

        self.set_value(0)

    # ---------- Цвет по уровню ----------
    def _color_for_percent(self, p: float) -> str:
        if p < 20:
            return "#E53935"
        elif p < 80:
            return "#FBC02D"
        else:
            return "#4CAF50"

    def _update_fill(self):
        rect = self.bar.contentsRect()
        w = rect.width()
        h = rect.height()

        fill_w = int(w * self._percent / 100.0)
        self.fill.setGeometry(0, 0, fill_w, h)

        color = self._color_for_percent(self._percent)
        self.fill.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    def set_value(self, percent: float):
        percent = max(0.0, min(100.0, float(percent)))
        self._percent = percent
        self.label.setText(f"{int(percent)} %")
        self._update_fill()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_fill()