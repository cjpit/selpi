from __future__ import annotations

from statistics import Statistics
from typing import Any

from web.formatting import build_view_model


class DashboardViewModel:
    def __init__(self) -> None:
        self.__statistics = Statistics()
        self.__snapshot: dict[str, Any] | None = None
        self.__error: str | None = None

    def refresh(self) -> dict[str, Any]:
        try:
            raw = self.__statistics.get()
            self.__snapshot = build_view_model(raw)
            self.__error = None
        except Exception as exc:  # pragma: no cover - hardware path
            self.__error = str(exc)
            if self.__snapshot is None:
                self.__snapshot = {
                    "meta": {"last_updated": None, "connected": False, "error": self.__error},
                    "overview": {},
                    "battery": {},
                    "solar": {},
                    "load": {},
                    "generator": {},
                    "temperatures": {},
                    "alarms": {"any": False, "items": []},
                }
            else:
                self.__snapshot["meta"]["error"] = self.__error
                self.__snapshot["meta"]["connected"] = False
        return self.__snapshot

    @property
    def snapshot(self) -> dict[str, Any]:
        if self.__snapshot is None:
            return self.refresh()
        return self.__snapshot
