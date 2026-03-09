import pyqtgraph as pg
import time

from pyqtgraph import DateAxisItem
from typing import Dict, List, Optional

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from widgets.status_card import StatusCard
from widgets.bunker_bar import BunkerBar


class DashboardPage(QWidget):
    """Главная страница - дашборд параметров объекта."""
    logout_requested = pyqtSignal()
    device_changed = pyqtSignal(int)
    boiler_changed = pyqtSignal(int)
    range_changed = pyqtSignal(int)
    period_changed = pyqtSignal(int, int)
    live_clicked = pyqtSignal()
    theme_toggled = pyqtSignal(str)  # "dark" | "light"
    archive_requested = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        # --- настройки приложения (сохраняем диапазон и т.п.) ---
        self.settings = QSettings("Thermovizor", "ThermovizorSCADA")

        saved_hours = self.settings.value("graph/window_hours", None)
        if saved_hours is not None:
            try:
                self.graph_window_hours = int(saved_hours)
            except Exception:
                self.graph_window_hours = 4

        self.card_refs: Dict[str, StatusCard] = {}
        self.main_plot: Optional[pg.PlotWidget] = None
        self.graph_time: List[float] = []
        self.user_is_panning = False
        self.selected_boiler = 1
        self.graph_window_hours = 4
        self.period_mode = False
        self.period_start_ts: Optional[int] = None
        self.period_end_ts: Optional[int] = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя строка
        top_row = QHBoxLayout()
        title_lbl = QLabel("Главное меню")
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(self._build_outdoor_temp())
        top_row.addSpacing(12)
        plant_lbl = QLabel("Иркутский завод тепловой автоматики")
        plant_lbl.setObjectName("PlantLabel")
        plant_lbl.setStyleSheet("font-size:10pt;")
        top_row.addWidget(plant_lbl)

        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #1F2226;
                color: white;
                padding: 4px 8px;
                border-radius: 6px;
                min-width: 220px;
            }
        """)

        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        top_row.addWidget(self.device_combo)
        # Кнопка переключения темы (между котельной и выходом)
        self.theme_btn = QPushButton("☀")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setToolTip("Переключить тему")
        self.theme_btn.setStyleSheet("")  # стиль придёт из QSS
        top_row.addSpacing(8)
        top_row.addWidget(self.theme_btn)

        logout_btn = QPushButton("➜]")
        logout_btn.setFixedSize(36, 36)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setToolTip("Выйти из аккаунта")
        logout_btn.setStyleSheet("")
        logout_btn.setObjectName("LogoutBtn")

        logout_btn.clicked.connect(self.logout_requested.emit)

        top_row.addSpacing(8)
        top_row.addWidget(logout_btn)

        main_layout.addLayout(top_row)

        # ==========================
        # ПРАВАЯ КОЛОНКА (график)
        # ==========================
        right_top = QWidget()
        right_layout = QVBoxLayout(right_top)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)  # можно 0, чтобы график занял максимум

        right_layout.addWidget(self._build_main_graph(), 1)

        # Сетка 2x2
        grid_2x2 = QGridLayout()
        grid_2x2.setSpacing(10)

        grid_2x2.addWidget(self._build_setevoy_kontur(), 0, 0)
        grid_2x2.addWidget(self._build_kotlovoy_kontur(), 1, 0)
        grid_2x2.addWidget(right_top, 0, 1, 2, 1)

        main_layout.addLayout(grid_2x2)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        bottom_row.addWidget(self._build_kotly(), 2)
        bottom_row.addWidget(self._build_dymososy(), 1)

        main_layout.addLayout(bottom_row)

    def apply_theme(self, theme: str):
        # theme: "dark" | "light"
        if not self.main_plot:
            return

        if theme == "light":
            bg = "#FFFFFF"
            axis = "#1C1F24"
            grid_alpha = 0.12
        else:
            bg = "#181A1F"
            axis = "#DADADA"
            grid_alpha = 0.15

        self.main_plot.setBackground(bg)
        self.main_plot.showGrid(x=True, y=True, alpha=grid_alpha)

        plot = self.main_plot.getPlotItem()
        plot.getAxis("bottom").setPen(axis)
        plot.getAxis("left").setPen(axis)
        plot.getAxis("bottom").setTextPen(axis)
        plot.getAxis("left").setTextPen(axis)

    def set_devices(self, devices: list, current_device_id: int):
        """
        devices: список dict от OwenCloud
        """
        self.device_combo.blockSignals(True)
        self.device_combo.clear()

        current_index = 0

        for i, dev in enumerate(devices):
            name = dev.get("name", "Без имени")
            dev_id = dev.get("id")
            self.device_combo.addItem(name, dev_id)

            if dev_id == current_device_id:
                current_index = i

        self.device_combo.setCurrentIndex(current_index)
        self.device_combo.blockSignals(False)

    def _on_device_changed(self, index: int):
        device_id = self.device_combo.itemData(index)
        if device_id is not None:
            self.device_changed.emit(int(device_id))

    # Вспомогательные блоки

    def _wrap_block(self, title: str, inner_widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        label = QLabel(title)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label)

        layout.addWidget(inner_widget)
        return frame

    def legend_item(self, text: str, color: str, curve: pg.PlotDataItem) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        cb = QCheckBox()
        cb.setChecked(True)
        cb.setTristate(False)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)

        dot = QFrame()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

        lbl = QLabel(text)
        lbl.setObjectName("LegendLabel")
        lbl.setStyleSheet("font-size: 9pt;")

        cb.toggled.connect(curve.setVisible)

        h.addWidget(cb)
        h.addWidget(dot)
        h.addWidget(lbl)
        h.addStretch()

        return w

    def _build_kotlovoy_kontur(self) -> QFrame:
        inner = QWidget()
        gl = QGridLayout(inner)
        gl.setSpacing(8)

        row = 0
        for i in range(1, 3):  # только насос 1 и 2
            card = StatusCard(
                f"Насос {i}",
                status_text="Остановка",
                status_color="#757575",
                icon_text="⛽"
            )
            self.card_refs[f"kotlovoy_pump{i}"] = card
            gl.addWidget(card, row, 0)

            row += 1

        return self._wrap_block("Котловой контур", inner)

    def _build_setevoy_kontur(self) -> QFrame:
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setSpacing(8)

        row1 = QWidget()
        r1 = QGridLayout(row1)
        r1.setSpacing(8)

        # Насос 1
        card_pump1 = StatusCard(
            "Насос 1",
            status_text="Остановка",
            status_color="#757575",
            icon_text="⛽"
        )
        self.card_refs["network_pump1"] = card_pump1
        r1.addWidget(card_pump1, 0, 0)

        # Давление подачи
        card_press_before = StatusCard(
            "Давление подачи", value="0", unit="Bar", icon_text="🕠"
        )
        self.card_refs["network_pressure_before"] = card_press_before
        r1.addWidget(card_press_before, 0, 1)

        # Насос 2
        card_pump2 = StatusCard(
            "Насос 2",
            status_text="Остановка",
            status_color="#757575",
            icon_text="⛽"
        )
        self.card_refs["network_pump2"] = card_pump2
        r1.addWidget(card_pump2, 1, 0)

        # Давление обратки
        card_press_after = StatusCard(
            "Давление обратки", value="0", unit="Bar", icon_text="🕛"
        )
        self.card_refs["network_pressure_after"] = card_press_after
        r1.addWidget(card_press_after, 1, 1)

        v.addWidget(row1)

        # Температуры
        temps_row = QWidget()
        tr = QHBoxLayout(temps_row)
        tr.setSpacing(8)

        card_temp_supply = StatusCard(
            "Температура подачи", value="0", unit="°C", icon_text="🌡️"
        )
        self.card_refs["network_temp_supply"] = card_temp_supply
        tr.addWidget(card_temp_supply)

        card_temp_return = StatusCard(
            "Температура обратки", value="0", unit="°C", icon_text="🌡️"
        )
        self.card_refs["network_temp_return"] = card_temp_return
        tr.addWidget(card_temp_return)

        v.addWidget(temps_row)

        return self._wrap_block("Сетевой контур", inner)

    def _build_main_graph(self) -> QFrame:
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        # ===== верхняя панель: выбор котла =====
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self.boiler_btn = QPushButton("Котёл 1 ▼")
        self.boiler_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boiler_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2226;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #333;
                font-size: 10pt;
                min-width: 120px;
                text-align: left;
            }
            QPushButton:hover { border: 1px solid #555; }
        """)

        menu = QMenu(self.boiler_btn)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1F2226;
                color: white;
                border: 1px solid #333;
            }
            QMenu::item:selected {
                background-color: #E53935;
            }
        """)

        def set_boiler(n: int):
            self.selected_boiler = n
            self.boiler_btn.setText(f"Котёл {n} ▼")

            # чтобы график не смешивал данные разных котлов - очищаем серии
            self.graph_time.clear()
            self.graph_temp_supply.clear()
            self.graph_temp_return.clear()
            self.graph_press_supply.clear()

            self.curve_temp_supply.clear()
            self.curve_temp_return.clear()
            self.curve_press_supply.clear()

            self.user_is_panning = False

            self.boiler_changed.emit(n)

        for n in (1, 2, 3):
            act = QAction(f"Котёл {n}", self.boiler_btn)
            act.triggered.connect(lambda _, nn=n: set_boiler(nn))
            menu.addAction(act)

        self.boiler_btn.setMenu(menu)

        top_bar.addWidget(self.boiler_btn)
        top_bar.addSpacing(8)

        self.range_btn = QPushButton(f"Диапазон: {self.graph_window_hours} ч ▼")
        self.range_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.range_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2226;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #333;
                font-size: 10pt;
                min-width: 150px;
                text-align: left;
            }
            QPushButton:hover { border: 1px solid #555; }
        """)

        def pick_range_hours():
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Диапазон данных")
            dlg.setLabelText("Показать последние (часов):")
            dlg.setInputMode(QInputDialog.InputMode.IntInput)
            dlg.setIntRange(1, 24)
            dlg.setIntStep(1)
            dlg.setIntValue(int(self.graph_window_hours))

            # стиль: белые числа, белые OK/Cancel, тёмный фон
            dlg.setStyleSheet("""
                QInputDialog, QWidget {
                    background-color: #101215;
                    color: white;
                    font-size: 10pt;
                }

                QLabel {
                    color: white;
                }

                QSpinBox {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 4px 8px;
                    min-height: 28px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #1F2226;
                    border: 1px solid #333;
                    width: 18px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    border: 1px solid #555;
                }
                QSpinBox::up-arrow, QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }

                QPushButton {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 14px;
                    min-width: 90px;
                }
                QPushButton:hover {
                    border: 1px solid #555;
                    background-color: #2A2F36;
                }
                QPushButton:pressed {
                    background-color: #161A20;
                }
                QPushButton:disabled {
                    color: #777;
                }
            """)

            # Переименовать кнопки на русские:
            bb = dlg.findChild(QDialogButtonBox)
            if bb:
                ok_btn = bb.button(QDialogButtonBox.StandardButton.Ok)
                cancel_btn = bb.button(QDialogButtonBox.StandardButton.Cancel)
                if ok_btn:
                    ok_btn.setText("Ок")
                if cancel_btn:
                    cancel_btn.setText("Отмена")

            if dlg.exec() != dlg.DialogCode.Accepted:
                return

            value = int(dlg.intValue())

            self.graph_window_hours = value
            self.settings.setValue("graph/window_hours", int(self.graph_window_hours))
            self.range_btn.setText(f"Диапазон: {self.graph_window_hours} ч ▼")

            # очистка серий
            self.graph_time.clear()
            self.graph_temp_supply.clear()
            self.graph_temp_return.clear()
            self.graph_press_supply.clear()

            self.curve_temp_supply.clear()
            self.curve_temp_return.clear()
            self.curve_press_supply.clear()

            self.user_is_panning = False
            self.range_changed.emit(self.graph_window_hours)

        self.range_btn.clicked.connect(pick_range_hours)
        top_bar.addWidget(self.range_btn)
        top_bar.addSpacing(8)

        # --- кнопка Live ---
        self.live_btn = QPushButton("Live")
        self.live_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.live_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2226;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #333;
                font-size: 10pt;
                min-width: 70px;
            }
            QPushButton:hover { border: 1px solid #555; background-color: #2A2F36; }
        """)

        def go_live():
            # выключаем режим периода
            self.period_mode = False
            self.period_start_ts = None
            self.period_end_ts = None
            self.period_btn.setText("Период ▼")

            # чистим серии (чтобы сразу перерисовалось)
            self.graph_time.clear()
            self.graph_temp_supply.clear()
            self.graph_temp_return.clear()
            self.graph_press_supply.clear()
            self.curve_temp_supply.clear()
            self.curve_temp_return.clear()
            self.curve_press_supply.clear()

            self.user_is_panning = False

            # сообщаем MainWindow - он перезагрузит историю последних N часов
            self.live_clicked.emit()

        self.live_btn.clicked.connect(go_live)
        top_bar.addWidget(self.live_btn)
        top_bar.addSpacing(8)

        # --- кнопка Период ---
        self.period_btn = QPushButton("Период ▼")
        self.period_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.period_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2226;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #333;
                font-size: 10pt;
                min-width: 140px;
                text-align: left;
            }
            QPushButton:hover { border: 1px solid #555; }
        """)

        def pick_period_range():
            dlg = QDialog(self)
            dlg.setWindowTitle("Выбор периода")
            dlg.setModal(True)
            dlg.setStyleSheet("""
                QDialog, QWidget {
                    background-color: #101215;
                    color: white;
                    font-size: 10pt;
                }
                QLabel { color: white; }
                QDateTimeEdit {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 10px;
                    min-height: 28px;
                }
                QPushButton {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 14px;
                    min-width: 90px;
                }
                QPushButton:hover { border: 1px solid #555; background-color: #2A2F36; }
                QPushButton:pressed { background-color: #161A20; }
            """)

            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(10)

            # поля С / По
            row_from = QHBoxLayout()
            row_from.addWidget(QLabel("С:"))
            dt_from = QDateTimeEdit(dlg)
            dt_from.setCalendarPopup(True)
            dt_from.setDisplayFormat("dd.MM.yyyy HH:mm")
            dt_from.setTimeSpec(Qt.TimeSpec.LocalTime)
            row_from.addWidget(dt_from, 1)
            layout.addLayout(row_from)

            row_to = QHBoxLayout()
            row_to.addWidget(QLabel("По:"))
            dt_to = QDateTimeEdit(dlg)
            dt_to.setCalendarPopup(True)
            dt_to.setDisplayFormat("dd.MM.yyyy HH:mm")
            dt_to.setTimeSpec(Qt.TimeSpec.LocalTime)
            row_to.addWidget(dt_to, 1)
            layout.addLayout(row_to)

            # дефолты:
            # если период уже выбран показываем его, иначе: по умолчанию последние N часов
            if self.period_start_ts and self.period_end_ts:
                dt_from.setDateTime(QDateTime.fromSecsSinceEpoch(int(self.period_start_ts)))
                dt_to.setDateTime(QDateTime.fromSecsSinceEpoch(int(self.period_end_ts)))
            else:
                now_dt = QDateTime.currentDateTime()
                dt_to.setDateTime(now_dt)
                dt_from.setDateTime(now_dt.addSecs(-int(self.graph_window_hours) * 3600))

            btns = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                parent=dlg
            )
            ok_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
            cancel_btn = btns.button(QDialogButtonBox.StandardButton.Cancel)
            if ok_btn: ok_btn.setText("Ок")
            if cancel_btn: cancel_btn.setText("Отмена")

            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)

            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            start_ts = int(dt_from.dateTime().toSecsSinceEpoch())
            end_ts = int(dt_to.dateTime().toSecsSinceEpoch())

            if end_ts <= start_ts:
                msg = QMessageBox(self)
                msg.setWindowTitle("Ошибка периода")
                msg.setText("Дата 'По' должна быть больше даты 'С'.")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStyleSheet("""
                    QMessageBox { background-color: #101215; }
                    QLabel { color: white; font-size: 11pt; }
                    QPushButton {
                        background-color: #1F2226;
                        color: white;
                        border-radius: 6px;
                        padding: 6px 14px;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #E53935; }
                """)
                msg.exec()
                return

            # включаем режим периода
            self.period_mode = True
            self.period_start_ts = start_ts
            self.period_end_ts = end_ts
            self.period_btn.setText("Период: выбран ▼")

            # чистим серии
            self.graph_time.clear()
            self.graph_temp_supply.clear()
            self.graph_temp_return.clear()
            self.graph_press_supply.clear()
            self.curve_temp_supply.clear()
            self.curve_temp_return.clear()
            self.curve_press_supply.clear()

            self.user_is_panning = True  # в режиме периода не автоскроллим

            # сообщаем MainWindow
            self.period_changed.emit(start_ts, end_ts)

        self.period_btn.clicked.connect(pick_period_range)
        top_bar.addWidget(self.period_btn)
        top_bar.addSpacing(8)

        # --- кнопка Выгрузка архива ---
        self.archive_btn = QPushButton("Выгрузка архива")
        self.archive_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.archive_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2226;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid #333;
                font-size: 10pt;
                min-width: 170px;
                text-align: center;
            }
            QPushButton:hover { border: 1px solid #555; background-color: #2A2F36; }
        """)

        def archive_flow():
            # 1) окно выбора котла
            dlg1 = QDialog(self)
            dlg1.setWindowTitle("Выбор котла")
            dlg1.setModal(True)
            dlg1.setStyleSheet("""
                QDialog, QWidget {
                    background-color: #101215;
                    color: white;
                    font-size: 10pt;
                }
                QLabel { color: white; }
                QComboBox {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 10px;
                    min-height: 28px;
                }
                QPushButton {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 14px;
                    min-width: 110px;
                }
                QPushButton:hover { border: 1px solid #555; background-color: #2A2F36; }
                QPushButton:pressed { background-color: #161A20; }
            """)

            lay1 = QVBoxLayout(dlg1)
            lay1.setContentsMargins(12, 12, 12, 12)
            lay1.setSpacing(10)

            lay1.addWidget(QLabel("Выберите котёл:"))
            cb_boiler = QComboBox(dlg1)
            cb_boiler.addItem("Котёл 1", 1)
            cb_boiler.addItem("Котёл 2", 2)
            cb_boiler.addItem("Котёл 3", 3)
            lay1.addWidget(cb_boiler)

            btns1 = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                parent=dlg1
            )
            ok1 = btns1.button(QDialogButtonBox.StandardButton.Ok)
            cn1 = btns1.button(QDialogButtonBox.StandardButton.Cancel)
            if ok1: ok1.setText("Далее")
            if cn1: cn1.setText("Отмена")
            btns1.accepted.connect(dlg1.accept)
            btns1.rejected.connect(dlg1.reject)
            lay1.addWidget(btns1)

            if dlg1.exec() != QDialog.DialogCode.Accepted:
                return

            boiler_n = int(cb_boiler.currentData())

            # 2) окно выбора периода
            dlg2 = QDialog(self)
            dlg2.setWindowTitle("Выгрузка архива — период")
            dlg2.setModal(True)
            dlg2.setStyleSheet("""
                QDialog, QWidget {
                    background-color: #101215;
                    color: white;
                    font-size: 10pt;
                }
                QLabel { color: white; }
                QDateTimeEdit {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 10px;
                    min-height: 28px;
                }
                QPushButton {
                    background-color: #1F2226;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 14px;
                    min-width: 140px;
                }
                QPushButton:hover { border: 1px solid #555; background-color: #2A2F36; }
                QPushButton:pressed { background-color: #161A20; }
            """)

            lay2 = QVBoxLayout(dlg2)
            lay2.setContentsMargins(12, 12, 12, 12)
            lay2.setSpacing(10)

            row_from = QHBoxLayout()
            row_from.addWidget(QLabel("С:"))
            dt_from = QDateTimeEdit(dlg2)
            dt_from.setCalendarPopup(True)
            dt_from.setDisplayFormat("dd.MM.yyyy HH:mm")
            dt_from.setTimeSpec(Qt.TimeSpec.LocalTime)
            row_from.addWidget(dt_from, 1)
            lay2.addLayout(row_from)

            row_to = QHBoxLayout()
            row_to.addWidget(QLabel("По:"))
            dt_to = QDateTimeEdit(dlg2)
            dt_to.setCalendarPopup(True)
            dt_to.setDisplayFormat("dd.MM.yyyy HH:mm")
            dt_to.setTimeSpec(Qt.TimeSpec.LocalTime)
            row_to.addWidget(dt_to, 1)
            lay2.addLayout(row_to)

            # дефолт: последние 4 часа
            now_dt = QDateTime.currentDateTime()
            dt_to.setDateTime(now_dt)
            dt_from.setDateTime(now_dt.addSecs(-4 * 3600))

            btn_export = QPushButton("Выгрузить данные")
            btn_cancel = QPushButton("Отмена")

            row_btns = QHBoxLayout()
            row_btns.addStretch()
            row_btns.addWidget(btn_cancel)
            row_btns.addWidget(btn_export)
            lay2.addLayout(row_btns)

            def show_warn(title: str, text: str):
                msg = QMessageBox(self)
                msg.setWindowTitle(title)
                msg.setText(text)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStyleSheet("""
                    QMessageBox { background-color: #101215; }
                    QLabel { color: white; font-size: 11pt; }
                    QPushButton {
                        background-color: #1F2226;
                        color: white;
                        border-radius: 6px;
                        padding: 6px 14px;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #E53935; }
                """)
                msg.exec()

            def on_export_clicked():
                start_ts = int(dt_from.dateTime().toSecsSinceEpoch())
                end_ts = int(dt_to.dateTime().toSecsSinceEpoch())

                if end_ts <= start_ts:
                    show_warn("Ошибка периода", "Дата 'По' должна быть больше даты 'С'.")
                    return

                # Ограничение: не старше 1 календарного года от текущей даты
                now_ts = int(QDateTime.currentDateTime().toSecsSinceEpoch())
                year_sec = 365 * 24 * 3600

                # если пользователь выставил дату "слишком давно"
                if (now_ts - start_ts) > year_sec or (now_ts - end_ts) > year_sec:
                    show_warn("Ошибка периода", "Дата превышает календарный год от сегодняшнего дня.")
                    return

                # (опционально) запретить будущее
                if end_ts > now_ts:
                    show_warn("Ошибка периода", "Дата 'По' не может быть больше текущего времени.")
                    return

                dlg2.accept()
                self.archive_requested.emit(boiler_n, start_ts, end_ts)

            btn_export.clicked.connect(on_export_clicked)
            btn_cancel.clicked.connect(dlg2.reject)

            dlg2.exec()

        self.archive_btn.clicked.connect(archive_flow)
        top_bar.addWidget(self.archive_btn)

        top_bar.addStretch()
        v.addLayout(top_bar)

        # ===== график =====
        time_axis = DateAxisItem(orientation="bottom")
        time_axis.setStyle(showValues=True)
        time_axis.enableAutoSIPrefix(False)
        self.main_plot = pg.PlotWidget(axisItems={"bottom": time_axis})
        t = time.time()
        self.main_plot.setXRange(t - 4 * 60 * 60, t, padding=0)
        self.main_plot.setBackground("#181A1F")
        self.main_plot.showGrid(x=True, y=True, alpha=0.15)
        self.main_plot.setLabel("left", "Значение")

        plot = self.main_plot.getPlotItem()
        plot.sigXRangeChanged.connect(self._on_xrange_changed)
        plot.hideAxis("right")
        plot.hideAxis("top")

        # ===== линии графика =====
        self.graph_time: List[float] = []
        self.curve_temp_supply = self.main_plot.plot(
            pen=pg.mkPen("#FF3B30", width=2), name="Температура подачи"
        )
        self.curve_temp_return = self.main_plot.plot(
            pen=pg.mkPen("#007AFF", width=2), name="Температура обратки"
        )
        self.curve_press_supply = self.main_plot.plot(
            pen=pg.mkPen("#FF9500", width=2), name="Давление обратки"
        )

        # данные
        self.graph_temp_supply: List[float] = []
        self.graph_temp_return: List[float] = []
        self.graph_press_supply: List[float] = []

        v.addWidget(self.main_plot, 1)

        legend_row = QHBoxLayout()
        legend_row.setSpacing(15)
        legend_row.addWidget(self.legend_item("Температура подачи", "#FF3B30", self.curve_temp_supply))
        legend_row.addWidget(self.legend_item("Температура обратки", "#007AFF", self.curve_temp_return))
        legend_row.addWidget(self.legend_item("Давление обратки", "#FF9500", self.curve_press_supply))
        legend_row.addStretch()
        v.addLayout(legend_row)

        return self._wrap_block("Основной график", inner)

    def _on_xrange_changed(self):
        self.user_is_panning = True

    def _build_kotly(self) -> QFrame:
        inner = QWidget()
        h = QHBoxLayout(inner)
        h.setSpacing(12)

        # ======================
        # КОТЛЫ
        # ======================
        boilers_widget = QWidget()
        bl = QGridLayout(boilers_widget)
        bl.setSpacing(8)

        for i in range(1, 4):
            status = "Остановка"
            color = "#757575"

            if i in (1, 3):
                status = "Авария"
                color = "#E53935"
            elif i == 2:
                status = "Работа"
                color = "#4CAF50"

            card = StatusCard(
                f"Котёл {i}",
                value="0",
                unit="°C",
                status_text=status,
                status_color=color,
                icon_text="🛢️"
            )

            bunker = BunkerBar()
            self.card_refs[f"boiler_{i}_bunker"] = bunker

            wrapper = QWidget()
            vl = QVBoxLayout(wrapper)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(4)
            vl.addWidget(card)
            vl.addWidget(bunker)
            self.card_refs[f"boiler_{i}"] = card

            row = (i - 1) // 2
            col = (i - 1) % 2
            bl.addWidget(wrapper, row, col)

        h.addWidget(boilers_widget)

        return self._wrap_block("Котлы", inner)

    def _build_dymososy(self) -> QFrame:
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setSpacing(8)

        for i in (1, 2):
            card = StatusCard(
                f"Дымосос {i}",
                status_text="Остановка",
                status_color="#757575",
                icon_text="💨"
            )
            self.card_refs[f"dymosos_{i}"] = card
            v.addWidget(card)

        v.addStretch()

        return self._wrap_block("Дымососы", inner)

    def _build_outdoor_temp(self) -> QLabel:
        self.outdoor_temp_label = QLabel("🌤️ Улица: 0.0 °C")
        self.outdoor_temp_label.setObjectName("OutdoorLabel")
        self.outdoor_temp_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.outdoor_temp_label.setStyleSheet("padding: 0px;")
        self.outdoor_temp_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        return self.outdoor_temp_label


class EventsStrip(QWidget):
    """Компактная лента событий для Dashboard (над графиком)."""

    def __init__(self, max_rows: int = 6):
        super().__init__()
        self.max_rows = max_rows

        self.setStyleSheet("""
            QFrame {
                background-color: #181A1F;
                border-radius: 8px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 9.5pt;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(4)

    def update_events(self, events: List[LocalEvent]):
        # очищаем старые строки
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for ev in events[: self.max_rows]:
            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(6, 3, 6, 3)

            msg_lbl = QLabel(ev.message)
            time_lbl = QLabel(ev.ts.strftime("%d.%m %H:%M:%S"))
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            time_lbl.setFixedWidth(120)
            time_lbl.setStyleSheet("color: #B0B0B0; font-size: 9pt;")

            row_layout.addWidget(msg_lbl, 1)
            row_layout.addWidget(time_lbl)

            if ev.severity == "Авария":
                row.setStyleSheet("""
                    QFrame {
                        background-color: #8B0000;
                        border-radius: 4px;
                    }
                    QLabel {
                        color: white;
                        font-weight: bold;
                    }
                """)
            else:
                row.setStyleSheet("""
                    QFrame {
                        background-color: #1F2226;
                        border-radius: 4px;
                    }
                """)

            self.layout.addWidget(row)