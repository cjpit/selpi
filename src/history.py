"""SQLite-backed time-series storage for inverter telemetry.

Records a subset of metrics from each Statistics.get() poll and provides
query methods that auto-select the appropriate resolution tier (raw / hourly /
daily) based on the requested time range.

No external dependencies — uses stdlib sqlite3.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Only persist metrics useful for graphing. Skip firmware info, serial numbers,
# digital I/O states, and service-reason codes.
TRACKED_METRICS: set[str] = {
    # Power flows
    "CombinedKacoAcPowerHiRes",  # Solar AC Power (W)
    "LoadAcPower",               # Load AC Power (W)
    "DCBatteryPower",            # Battery Power (W)
    "ACGeneratorPower",          # Generator Power (W)
    "Shunt1Power",               # Shunt 1 Power (W)
    "Shunt2Power",               # Shunt 2 Power (W)
    # Battery
    "BatteryVolts",              # Battery Voltage (V)
    "BattSocPercent",            # State of Charge (%)
    "DCBatteryCurrent",          # Battery Current (A)
    "BatteryTemperature",        # Battery Temp (C)
    # Energy today
    "BattOutToday",              # Battery Out Today (Wh)
    "BattInToday",               # Battery In Today (Wh)
    "LoadAccumulatedToday",      # Load Today (Wh)
    "ACInputToday",              # AC Input Today (Wh)
    # Solar
    "PercentageSolarOutput",     # Solar Output (%)
    # Temperatures
    "Heatsink1Temp",
    "Heatsink2Temp",
    "ControlBoardTemp",
    "InletTemp",
    "TransformerTemp",
    # Fan
    "FanSpeed",
    # Charge state (stored as numeric 0/1)
    "absorb",
    "bulk",
    "float",
    # Generator
    "GeneratorStatus",
    # Float hours
    "FloatHours",
}

SCHEMA_VERSION = 2

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    name TEXT NOT NULL,
    value REAL,
    units TEXT
);
CREATE INDEX IF NOT EXISTS idx_readings_name_ts ON readings(name, ts);

CREATE TABLE IF NOT EXISTS readings_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    name TEXT NOT NULL,
    avg_value REAL,
    min_value REAL,
    max_value REAL,
    samples INTEGER
);
CREATE INDEX IF NOT EXISTS idx_hourly_name_ts ON readings_hourly(name, ts);

CREATE TABLE IF NOT EXISTS readings_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    name TEXT NOT NULL,
    avg_value REAL,
    min_value REAL,
    max_value REAL,
    samples INTEGER
);
CREATE INDEX IF NOT EXISTS idx_daily_name_ts ON readings_daily(name, ts);
"""

# Map range strings to (timedelta, table) — ordered by threshold ascending.
_RANGE_TIERS: list[tuple[timedelta, str]] = [
    (timedelta(hours=24), "readings"),
    (timedelta(days=30), "readings_hourly"),
    (timedelta(days=365), "readings_daily"),
]

_RANGE_ALIASES: dict[str, str] = {
    "1h": "1h",
    "6h": "6h",
    "24h": "24h",
    "7d": "7d",
    "30d": "30d",
    "1y": "1y",
}


def _db_path() -> str:
    return os.getenv("SELPI_HISTORY_DB_PATH", "selpi-history.db")


def _raw_days() -> int:
    return int(os.getenv("SELPI_HISTORY_RAW_DAYS", "7"))


def _hourly_days() -> int:
    return int(os.getenv("SELPI_HISTORY_HOURLY_DAYS", "90"))


def _table_for_range(range_str: str) -> tuple[str, str]:
    """Return (table_name, sql_interval) for the given range string.

    sql_interval is a value suitable for datetime('now', ?, 'localtime').
    """
    mapping = {
        "1h":  ("readings",         "-1 hours"),
        "6h":  ("readings",         "-6 hours"),
        "24h": ("readings",         "-24 hours"),
        "7d":  ("readings_hourly",  "-7 days"),
        "30d": ("readings_hourly",  "-30 days"),
        "1y":  ("readings_daily",   "-365 days"),
    }
    return mapping.get(range_str, ("readings", "-24 hours"))


class HistoryStore:
    """Thread-safe (connection-per-call) SQLite history store."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or _db_path()
        self._init_db()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(SCHEMA_SQL)
            # Check / set schema version
            row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
            if row is None:
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
            conn.commit()
            logger.info("History database initialised at %s", self._db_path)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(self, raw_stats: list[dict[str, Any]]) -> None:
        """Insert one row per tracked metric from a Statistics.get() result."""
        rows = []
        for item in raw_stats:
            name = item.get("name", "")
            if name not in TRACKED_METRICS:
                continue
            value = item.get("value")
            if value is None:
                continue
            rows.append((name, float(value), item.get("units", "")))

        if not rows:
            return

        conn = self._connect()
        try:
            conn.executemany(
                "INSERT INTO readings (name, value, units) VALUES (?, ?, ?)",
                rows,
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query(self, variable_name: str, range: str = "24h") -> list[dict[str, Any]]:
        """Return time-series data for *variable_name* over *range*.

        Returns a list of dicts. For raw data each dict has ``ts`` and ``value``.
        For aggregated tiers each dict also has ``avg``, ``min``, ``max``, ``samples``.
        """
        table, interval = _table_for_range(range)

        conn = self._connect()
        try:
            if table == "readings":
                rows = conn.execute(
                    "SELECT ts, value FROM readings "
                    "WHERE name = ? AND ts >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ?) "
                    "ORDER BY ts ASC",
                    (variable_name, interval),
                ).fetchall()
                return [{"ts": r["ts"], "value": r["value"]} for r in rows]
            else:
                rows = conn.execute(
                    f"SELECT ts, avg_value, min_value, max_value, samples FROM {table} "
                    "WHERE name = ? AND ts >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ?) "
                    "ORDER BY ts ASC",
                    (variable_name, interval),
                ).fetchall()
                return [
                    {
                        "ts": r["ts"],
                        "avg": r["avg_value"],
                        "min": r["min_value"],
                        "max": r["max_value"],
                        "samples": r["samples"],
                    }
                    for r in rows
                ]
        finally:
            conn.close()

    def available_variables(self) -> list[str]:
        """Return the set of variable names that have been recorded."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT DISTINCT name FROM readings ORDER BY name"
            ).fetchall()
            return [r["name"] for r in rows]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Aggregation & Pruning
    # ------------------------------------------------------------------

    def aggregate_hourly(self) -> None:
        """Aggregate raw readings into hourly summaries."""
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO readings_hourly (ts, name, avg_value, min_value, max_value, samples) "
                "SELECT "
                "    strftime('%Y-%m-%dT%H:00:00Z', ts) AS hour, "
                "    name, "
                "    AVG(value), "
                "    MIN(value), "
                "    MAX(value), "
                "    COUNT(*) "
                "FROM readings "
                "WHERE ts < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', '-1 hour') "
                "GROUP BY hour, name "
                "HAVING COUNT(*) > 0"
            )
            conn.commit()
            logger.info("Hourly aggregation complete")
        finally:
            conn.close()

    def aggregate_daily(self) -> None:
        """Aggregate hourly summaries into daily summaries."""
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO readings_daily (ts, name, avg_value, min_value, max_value, samples) "
                "SELECT "
                "    strftime('%Y-%m-%dT00:00:00Z', ts) AS day, "
                "    name, "
                "    AVG(avg_value), "
                "    MIN(min_value), "
                "    MAX(max_value), "
                "    SUM(samples) "
                "FROM readings_hourly "
                "WHERE ts < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', '-1 day') "
                "GROUP BY day, name "
                "HAVING COUNT(*) > 0"
            )
            conn.commit()
            logger.info("Daily aggregation complete")
        finally:
            conn.close()

    def prune(self, raw_days: int | None = None, hourly_days: int | None = None) -> None:
        """Delete old raw and hourly data."""
        raw_days = raw_days if raw_days is not None else _raw_days()
        hourly_days = hourly_days if hourly_days is not None else _hourly_days()

        conn = self._connect()
        try:
            c1 = conn.execute(
                "DELETE FROM readings WHERE ts < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ? || ' days')",
                (f"-{raw_days}",),
            ).rowcount
            c2 = conn.execute(
                "DELETE FROM readings_hourly WHERE ts < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ? || ' days')",
                (f"-{hourly_days}",),
            ).rowcount
            conn.commit()
            logger.info("Pruned %d raw rows, %d hourly rows", c1, c2)
        finally:
            conn.close()

    def run_cleanup(self) -> None:
        """Full cleanup cycle: aggregate then prune."""
        logger.info("Starting history cleanup cycle")
        self.aggregate_hourly()
        self.aggregate_daily()
        self.prune()
        logger.info("History cleanup cycle complete")

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------

    def close(self) -> None:
        """No-op — connections are opened and closed per call."""
        pass

    def row_count(self) -> dict[str, int]:
        """Return row counts per table for diagnostics."""
        conn = self._connect()
        try:
            raw = conn.execute("SELECT COUNT(*) AS c FROM readings").fetchone()["c"]
            hourly = conn.execute("SELECT COUNT(*) AS c FROM readings_hourly").fetchone()["c"]
            daily = conn.execute("SELECT COUNT(*) AS c FROM readings_daily").fetchone()["c"]
            return {"readings": raw, "readings_hourly": hourly, "readings_daily": daily}
        finally:
            conn.close()
