import requests
from typing import Dict, List, Optional
from constants import API_BASE
from datetime import datetime, timedelta, timezone
from typing import Union


class OwenCloudClient:
    def __init__(self):
        self.token: Optional[str] = None
        self.session = requests.Session()

    @property
    def headers(self) -> Dict[str, str]:
        if not self.token:
            return {}
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "*/*",
        }

    def auth(self, login: str, password: str) -> None:
        resp = self.session.post(
            f"{API_BASE}/auth/open",
            json={"login": login, "password": password},
            timeout=10
        )
        resp.raise_for_status()
        self.token = resp.json()["token"]

    def get_devices(self) -> List[Dict]:
        resp = self.session.post(
            f"{API_BASE}/device/index",
            headers=self.headers,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def get_device_parameters(self, device_id: int) -> List[Dict]:
        resp = self.session.post(
            f"{API_BASE}/device/{device_id}",
            headers=self.headers,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("parameters", [])

    def get_last_values_by_ids(self, ids: List[int]) -> Dict[int, float]:
        if not ids:
            return {}

        resp = self.session.post(
            f"{API_BASE}/parameters/last-data",
            headers=self.headers,
            json={"ids": ids},
            timeout=10
        )
        resp.raise_for_status()

        result = {}
        for item in resp.json():
            if item.get("values"):
                result[item["id"]] = float(item["values"][0]["v"])
        return result

    @staticmethod
    def _parse_iso_ts(s: str) -> float:
        # "2026-02-18T10:01:00Z" -> "2026-02-18T10:01:00+00:00"
        s = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt.timestamp()

    def get_history(
        self,
        ids: list[int],
        start: Union[str, int, float, datetime],
        end: Union[str, int, float, datetime],
        step_sec: int = 60,
        *,
        tz_offset_hours: int = 3,   # как в мобилке
    ) -> dict[int, list[tuple[float, float]]]:
        if not ids:
            return {}

        def to_api_time(x) -> str:
            # OwenCloud часто ожидает "YYYY-MM-DD HH:MM:SS" в МСК(+3)
            if isinstance(x, datetime):
                dt_utc = x.astimezone(timezone.utc) if x.tzinfo else x.replace(tzinfo=timezone.utc)
                dt = dt_utc + timedelta(hours=tz_offset_hours)
                return dt.strftime("%Y-%m-%d %H:%M:%S")

            if isinstance(x, (int, float)):
                # epoch -> UTC -> +3 -> string
                dt = datetime.utcfromtimestamp(int(x)) + timedelta(hours=tz_offset_hours)
                return dt.strftime("%Y-%m-%d %H:%M:%S")

            # строка: попробуем распарсить, если не получится — отправим как есть
            s = str(x).strip()
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                dt_utc = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                dt2 = dt_utc + timedelta(hours=tz_offset_hours)
                return dt2.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return s

        payload = {
            "ids": ids,
            "start": to_api_time(start),
            "end": to_api_time(end),
            "step": int(step_sec),
        }

        resp = self.session.post(
            f"{API_BASE}/parameters/data",
            headers=self.headers,
            json=payload,
            timeout=20,
        )

        if not resp.ok:
            print("[HISTORY] HTTP:", resp.status_code)
            print("[HISTORY] URL:", resp.url)
            print("[HISTORY] REQUEST JSON:", payload)
            print("[HISTORY] RESPONSE:", resp.text[:2000])
            resp.raise_for_status()

        data = resp.json()

        # отладка
        if isinstance(data, list) and data and isinstance(data[0], dict):
            print("[HISTORY] sample item keys:", list(data[0].keys()))
            v0 = data[0].get("values")
            if isinstance(v0, list) and not v0:
                print("[HISTORY] values is empty list")

        out: dict[int, list[tuple[float, float]]] = {}

        if not isinstance(data, list):
            return out

        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue

            pid = int(item["id"])
            series: list[tuple[float, float]] = []

            values = item.get("values")
            if not isinstance(values, list):
                out[pid] = series
                continue

            for p in values:
                if not isinstance(p, dict):
                    continue

                # OwenCloud часто отдаёт время в "d" (epoch), либо "t/ts/time"
                tt = p.get("d", p.get("t", p.get("ts", p.get("time"))))
                vv = p.get("v", p.get("value", p.get("val", p.get("f"))))

                if tt is None or vv is None:
                    continue

                try:
                    # tt: чаще epoch (int), иногда строка
                    if isinstance(tt, (int, float)):
                        ts = float(tt)
                    else:
                        s = str(tt).replace("Z", "+00:00")
                        ts = datetime.fromisoformat(s).timestamp()

                    series.append((ts, float(vv)))
                except Exception:
                    continue

            out[pid] = series

        return out