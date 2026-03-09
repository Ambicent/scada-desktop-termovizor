from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt
from typing import List
from models.events import LocalEvent


class EventsPage(QWidget):
    """Страница отображения событий OwenCloud."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setObjectName("EventsTable")

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Сообщение",
            "Время фиксации",
            "Время снятия",
            "Параметр",
            "Критичность"
        ])

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   # Сообщение
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

    def update_local_events(self, events: List[LocalEvent]):
        self.table.setRowCount(len(events))

        for row, ev in enumerate(events):
            items = [
                QTableWidgetItem(ev.message),
                QTableWidgetItem(ev.ts.strftime("%d.%m.%Y %H:%M:%S")),
                QTableWidgetItem(ev.cleared_ts.strftime("%d.%m.%Y %H:%M:%S") if ev.cleared_ts else ""),
                QTableWidgetItem(ev.key),
                QTableWidgetItem(ev.severity),
            ]

            for col, it in enumerate(items):
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, it)

            if ev.severity == "Авария":
                for it in items:
                    it.setBackground(QColor("#8B0000"))
                    it.setForeground(QColor("#FFFFFF"))
            else:
                # сброс - пусть цвета берутся из темы (QSS)
                for it in items:
                    it.setBackground(QBrush())
                    it.setForeground(QBrush())