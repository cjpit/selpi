from __future__ import annotations

import asyncio
import logging
from statistics import Statistics
from typing import Any

from history import HistoryStore
from web.formatting import build_view_model

logger = logging.getLogger(__name__)


class DashboardViewModel:
    def __init__(self) -> None:
        self.__statistics = Statistics()
        self.__history = HistoryStore()
        self.__snapshot: dict[str, Any] = {
            "meta": {"last_updated": None, "connected": False, "error": None},
            "overview": {},
            "battery": {},
            "solar": {},
            "load": {},
            "generator": {},
            "temperatures": {},
            "alarms": {"any": False, "items": []},
            "attention": {"any": False, "reasons": []},
            "history": {"dc": {}, "ac": {}},
            "extra": {},
            "flow": {},
        }
        self.__error: str | None = None

    def refresh(self) -> dict[str, Any]:
        try:
            raw = self.__statistics.get()
            self.__snapshot = build_view_model(raw)
            try:
                self.__history.record(raw)
            except Exception:
                logger.warning("Failed to record history", exc_info=True)
            self.__error = None
        except Exception as exc:  # pragma: no cover - hardware path
            self.__error = str(exc)
            self.__snapshot["meta"]["error"] = self.__error
            self.__snapshot["meta"]["connected"] = False
        return self.__snapshot

    async def refresh_async(self) -> dict[str, Any]:
        return await asyncio.to_thread(self.refresh)

    @property
    def snapshot(self) -> dict[str, Any]:
        return self.__snapshot
