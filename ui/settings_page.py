from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Dict
from api.owencloud import OwenCloudClient
from config_manager import ConfigManager


class SettingsPage(QWidget):
    """
    Настройки параметров OwenCloud.
    Пользователь вручную вводит КОД параметра (например A6, A4, A21)
    """
    settings_saved = pyqtSignal()
    GROUPS = {
        "Температура на улице": {
            "outdoor_temperature": "Температура на улице",
        },
        "Котловой контур": {
            "kotlovoy_pump1_status": "Статус котлового насоса 1",
            "kotlovoy_pump2_status": "Статус котлового насоса 2",

            "kotlovoy_pump1_alarm": "Авария котлового насоса 1",
            "kotlovoy_pump2_alarm": "Авария котлового насоса 2",
        },
        "Сетевой контур": {
            "network_pump1_status": "Статуса сетевого насоса 1",
            "network_pump2_status": "Статуса сетевого насоса 2",

            "network_pump1_alarm": "Авария сетевого насоса 1",
            "network_pump2_alarm": "Авария сетевого насоса 2",

            "network_pressure_before": "Давление подачи",
            "network_pressure_after": "Давление обратки",

            "network_temp_supply": "Температура подачи",
            "network_temp_return": "Температура обратки",
        },
        "Котлы": {
            "boiler_1_status": "Статус котла 1",
            "boiler_2_status": "Статус котла 2",
            "boiler_3_status": "Статус котла 3",

            "boiler_1_alarm": "Авария котла 1",
            "boiler_2_alarm": "Авария котла 2",
            "boiler_3_alarm": "Авария котла 3",

            "boiler_1": "Температура подачи котла 1",
            "boiler_2": "Температура подачи котла 2",
            "boiler_3": "Температура подачи котла 3",

            "boiler_1_return": "Температура обратки котла 1",
            "boiler_2_return": "Температура обратки котла 2",
            "boiler_3_return": "Температура обратки котла 3",

            "boiler_1_pressure": "Давление обратки котла 1",
            "boiler_2_pressure": "Давление обратки котла 2",
            "boiler_3_pressure": "Давление обратки котла 3",

            "boiler_1_bunker": "Уровень бункера котла 1",
            "boiler_2_bunker": "Уровень бункера котла 2",
            "boiler_3_bunker": "Уровень бункера котла 3",
        },
        "Дымососы": {
            "dymosos_1_alarm": "Авария дымососа 1",
            "dymosos_2_alarm": "Авария дымососа 2",

            "dymosos_1": "Статус дымососа 1",
            "dymosos_2": "Статус дымососа 2",
        }
    }

    def __init__(self, api_client: OwenCloudClient, device_id: int, config_manager: ConfigManager):
        super().__init__()

        self.api_client = api_client
        self.device_id = device_id
        self.config_manager = config_manager

        self.inputs: Dict[str, QLineEdit] = {}

        self.setStyleSheet("")

        # =========================
        # SCROLL AREA
        # =========================
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #15181C;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3A3F45;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555A60;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # =========================
        # CONTENT WIDGET
        # =========================
        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # =========================
        # HEADER
        # =========================
        title = QLabel("Настройки параметров")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        descr = QLabel("Введите код параметра.")
        descr.setStyleSheet("color: #AAAAAA; font-size: 11pt;")
        layout.addWidget(descr)

        # =========================
        # LOAD SAVED CONFIG
        # =========================
        saved = self.config_manager.load()
        mapping = saved.get("mapping", {})

        # =========================
        # GENERATE FORMS
        # =========================
        for group_title, fields in self.GROUPS.items():

            grp_label = QLabel(group_title)
            grp_label.setFont(QFont("Arial", 17, QFont.Weight.Bold))
            layout.addWidget(grp_label)

            grid = QGridLayout()
            grid.setSpacing(10)
            layout.addLayout(grid)

            row = 0
            for key, label in fields.items():
                lbl = QLabel(label)
                grid.addWidget(lbl, row, 0)

                inp = QLineEdit()
                inp.setPlaceholderText("Введите код параметра")
                inp.setText(mapping.get(key, ""))

                self.inputs[key] = inp
                grid.addWidget(inp, row, 1)

                row += 1

        layout.addSpacing(20)

        save_btn = QPushButton("Сохранить настройки")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        layout.addStretch()

        # =========================
        # MAIN LAYOUT
        # =========================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def save_config(self):
        cfg = {"mapping": {}}

        for key, inp in self.inputs.items():
            code = inp.text().strip()
            if code:
                cfg["mapping"][key] = code

        self.config_manager.save(cfg)

        self.settings_saved.emit()

        QMessageBox.information(self, "Готово", "Настройки параметров сохранены.")