API_BASE = "https://api.owencloud.ru/v1"

STATUS_COLORS = {
    "Работа": "#4CAF50",
    "Остановка": "#757575",
    "Авария": "#E53935",
}

EVENT_LABELS = {
    "kotlovoy_pump1_status": "Котловой насос 1",
    "kotlovoy_pump2_status": "Котловой насос 2",
    "kotlovoy_pump1_alarm": "Котловой насос 1",
    "kotlovoy_pump2_alarm": "Котловой насос 2",

    "network_pump1_status": "Сетевой насос 1",
    "network_pump2_status": "Сетевой насос 2",
    "network_pump1_alarm": "Сетевой насос 1",
    "network_pump2_alarm": "Сетевой насос 2",

    "boiler_1_status": "Котёл 1",
    "boiler_2_status": "Котёл 2",
    "boiler_3_status": "Котёл 3",
    "boiler_1_alarm": "Котёл 1",
    "boiler_2_alarm": "Котёл 2",
    "boiler_3_alarm": "Котёл 3",

    "dymosos_1": "Дымосос 1",
    "dymosos_2": "Дымосос 2",
    "dymosos_1_alarm": "Дымосос 1",
    "dymosos_2_alarm": "Дымосос 2",
}

DARK_THEME_QSS = """
/* ---------- Base ---------- */
QWidget {
    background: #101215;
    color: #EDEDED;
    font-family: Arial;
}
QLabel, QCheckBox, QAbstractButton {
    background: transparent;
}

QFrame#Panel QWidget,
QFrame#Card QWidget {
    background: transparent;
}
QFrame#SideMenu {
    background: #15181C;
}

QFrame#Panel {
    background: #181A1F;
    border-radius: 10px;
    border: 1px solid #2A2F36;
}

QFrame#Card {
    background: #1F2226;
    border-radius: 10px;
    border: 1px solid #2A2F36;
}

QLabel#DimLabel {
    color: #B0B0B0;
}

/* ---------- Inputs ---------- */
QComboBox, QLineEdit, QDateTimeEdit, QSpinBox {
    background: #1F2226;
    color: #FFFFFF;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QComboBox QAbstractItemView {
    background: #1F2226;
    color: #FFFFFF;
    selection-background-color: #E53935;
}

/* ---------- Buttons ---------- */
QPushButton {
    background: #1F2226;
    color: #FFFFFF;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 6px 10px;
}

QPushButton:hover {
    border: 1px solid #555;
    background: #2A2F36;
}

QPushButton#Danger:hover {
    background: #E53935;
    border: 1px solid #E53935;
}

QPushButton#NavButton {
    background: transparent;
    border: none;
    color: #CCCCCC;
    text-align: left;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 11pt;
}

QPushButton#NavButton:hover {
    background: #1F2226;
}

QPushButton#NavButton:checked {
    background: #E53935;
    color: white;
    font-weight: bold;
}
QPushButton#LogoutBtn {
    background: transparent;
    color: #FFFFFF;
    font-size: 14pt;
    border: none;
}

QPushButton#LogoutBtn:hover {
    background: #E53935;
    color: white;
}

/* ---------- Scrollbar ---------- */
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
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
/* ---------- Top labels ---------- */
QLabel#OutdoorLabel {
    color: #E0E0E0;
}
QLabel#PlantLabel {
    color: #B0B0B0;
}

/* ---------- Auth card ---------- */
QFrame#AuthCard {
    background: #181A1F;
    border-radius: 18px;
    border: 1px solid #2A2F36;
}
QFrame#AuthCard QWidget {
    background: transparent;
}
/* ---------- Graph legend ---------- */
QLabel#LegendLabel {
    color: #CCCCCC;
}
/* ---------- Events table ---------- */
QTableWidget#EventsTable {
    background-color: #101215;
    color: #FFFFFF;
    gridline-color: #333333;
    font-size: 11pt;
    selection-background-color: #E53935;
    selection-color: #FFFFFF;
}

QTableWidget#EventsTable::item {
    padding: 6px;
}

QTableWidget#EventsTable::item:selected {
    background-color: #E53935;
    color: #FFFFFF;
}

QTableWidget#EventsTable QHeaderView::section {
    background-color: #181A1F;
    color: #FFFFFF;
    padding: 6px;
    border: none;
    font-size: 11pt;
}

QTableCornerButton::section {
    background-color: #181A1F;
    border: none;
}
"""

LIGHT_THEME_QSS = """
/* ---------- Base ---------- */
QWidget {
    background: #F3F5F7;
    color: #1C1F24;
    font-family: Arial;
}
QLabel, QCheckBox, QAbstractButton {
    background: transparent;
}

QFrame#Panel QWidget,
QFrame#Card QWidget {
    background: transparent;
}
QFrame#SideMenu {
    background: #FFFFFF;
}

QFrame#Panel {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E6EA;
}

QFrame#Card {
    background: #F9FAFB;
    border-radius: 10px;
    border: 1px solid #E2E6EA;
}

QLabel#DimLabel {
    color: #5E6A75;
}

/* ---------- Inputs ---------- */
QComboBox, QLineEdit, QDateTimeEdit, QSpinBox {
    background: #FFFFFF;
    color: #1C1F24;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 28px;
}

QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #1C1F24;
    selection-background-color: #E53935;
}

/* ---------- Buttons ---------- */
QPushButton {
    background: #FFFFFF;
    color: #1C1F24;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    padding: 6px 10px;
}

QPushButton:hover {
    background: #EEF2F6;
    border: 1px solid #C7D0D9;
}

QPushButton#Danger:hover {
    background: #E53935;
    border: 1px solid #E53935;
    color: #FFFFFF;
}

QPushButton#NavButton {
    background: transparent;
    border: none;
    color: #334155;
    text-align: left;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 11pt;
}

QPushButton#NavButton:hover {
    background: #EEF2F6;
}

QPushButton#NavButton:checked {
    background: #E53935;
    color: white;
    font-weight: bold;
}
QPushButton#LogoutBtn {
    background: transparent;
    color: #1C1F24;
    font-size: 14pt;
    border: none;
}

QPushButton#LogoutBtn:hover {
    background: #E53935;
    color: white;
}

/* ---------- Scrollbar ---------- */
QScrollBar:vertical {
    background: #FFFFFF;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #D0D7DE;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #B9C2CC;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
/* ---------- Top labels ---------- */
QLabel#OutdoorLabel {
    color: #1C1F24;
}
QLabel#PlantLabel {
    color: #1C1F24;
}

/* ---------- Auth card ---------- */
QFrame#AuthCard {
    background: #FFFFFF;
    border-radius: 18px;
    border: 1px solid #E2E6EA;
}
QFrame#AuthCard QWidget {
    background: transparent;
}
/* ---------- Graph legend ---------- */
QLabel#LegendLabel {
    color: #1C1F24;
}
/* ---------- Events table ---------- */
QTableWidget#EventsTable {
    background-color: #FFFFFF;
    color: #1C1F24;
    gridline-color: #E2E6EA;
    font-size: 11pt;
    selection-background-color: #E53935;
    selection-color: #FFFFFF;
}

QTableWidget#EventsTable::item {
    padding: 6px;
}

QTableWidget#EventsTable::item:selected {
    background-color: #E53935;
    color: #FFFFFF;
}

QTableWidget#EventsTable QHeaderView::section {
    background-color: #F3F5F7;
    color: #1C1F24;
    padding: 6px;
    border: none;
    font-size: 11pt;
}

QTableCornerButton::section {
    background-color: #F3F5F7;
    border: none;
}
"""