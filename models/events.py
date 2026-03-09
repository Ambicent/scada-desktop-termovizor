from dataclasses import dataclass
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class LocalEvent:
    ts: datetime
    message: str
    key: str
    severity: str  # "Инфо" | "Авария"
    cleared_ts: Optional[datetime] = None


class EventEngine:
    """
    Генератор событий по изменению значений параметров.
    Хранит предыдущее значение каждого key и формирует события при изменении.
    """

    def __init__(self, storage: "EventStorage", max_events: int = 200):
        self.prev: Dict[str, float] = {}
        self.events: List[LocalEvent] = []
        self.max_events = max_events
        self.storage = storage
        self.events = self.storage.load_events(limit=max_events)
        self.active_alarms = {}
        for ev in self.events:
            if ev.severity == "Авария" and ev.cleared_ts is None:
                self.active_alarms[ev.key] = ev
                self.prev[ev.key] = 1

    def push(self, *, key: str, value: float, label: str, kind: str):
        """
        kind: "status" или "alarm"
        """
        prev = self.prev.get(key)
        self.prev[key] = value

        # первое значение — не генерим событие
        if prev is None:
            self.prev[key] = value
            return

        # если реально не изменилось
        if float(prev) == float(value):
            return

        if kind == "status":
            # 0->1 запуск, 1->0 останов
            if int(prev) == 0 and int(value) == 1:
                self._add("Инфо", f"{label} запущен", key)
            elif int(prev) == 1 and int(value) == 0:
                self._add("Инфо", f"{label} остановлен", key)

        elif kind == "alarm":
            # авария появилась
            if int(prev) == 0 and int(value) == 1:
                ev = LocalEvent(
                    ts=datetime.now(),
                    message=f"Авария {label}",
                    key=key,
                    severity="Авария",
                    cleared_ts=None
                )
                self.active_alarms[key] = ev
                self.events.insert(0, ev)
                self.storage.save_event(ev)
                return
            # авария снята
            if int(prev) == 1 and int(value) == 0:
                ev = self.active_alarms.pop(key, None)
                if not ev:
                    return
                cleared_time = datetime.now()
                ev.cleared_ts = cleared_time
                # обновляем БД
                self.storage.update_cleared_time(key, cleared_time)
                return

    def _add(self, severity: str, message: str, key: str):
        ev = LocalEvent(datetime.now(), message, key, severity)
        self.events.insert(0, ev)
        self.storage.save_event(ev)
        if len(self.events) > self.max_events:
            self.events = self.events[: self.max_events]


class EventStorage:
    def __init__(self, device_id: int):
        os.makedirs("data", exist_ok=True)
        self.db_path = f"data/events_device_{device_id}.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    cleared_ts TEXT,
                    message TEXT NOT NULL,
                    param_key TEXT NOT NULL,
                    severity TEXT NOT NULL
                )
            """)

    def save_event(self, ev: LocalEvent):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO events (ts, cleared_ts, message, param_key, severity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ev.ts.isoformat(),
                    ev.cleared_ts.isoformat() if ev.cleared_ts else None,
                    ev.message,
                    ev.key,
                    ev.severity,
                )
            )

    def update_cleared_time(self, key: str, cleared_ts: datetime):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE events
                SET cleared_ts = ?
                WHERE id = (
                    SELECT id
                    FROM events
                    WHERE param_key = ?
                      AND severity = 'Авария'
                      AND cleared_ts IS NULL
                    ORDER BY id DESC
                    LIMIT 1
                )
                """,
                (cleared_ts.isoformat(), key)
            )

    def load_events(self, limit: int = 200) -> List[LocalEvent]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                    SELECT ts, cleared_ts, message, param_key, severity
                    FROM events
                    ORDER BY id DESC
                    LIMIT ?
                """,
                (limit,)
            ).fetchall()

        events = []
        for ts, cleared_ts, msg, key, sev in rows:
            events.append(
                LocalEvent(
                    ts=datetime.fromisoformat(ts),
                    cleared_ts=datetime.fromisoformat(cleared_ts) if cleared_ts else None,
                    message=msg,
                    key=key,
                    severity=sev
                )
            )
        return events

