"""Tests for history.HistoryStore."""

from __future__ import annotations

import os
import tempfile

import pytest

from history import HistoryStore, TRACKED_METRICS


@pytest.fixture()
def store(tmp_path):
    """Create a HistoryStore backed by a temporary SQLite file."""
    db_path = str(tmp_path / "test-history.db")
    s = HistoryStore(db_path=db_path)
    yield s
    s.close()


def _make_stats(**overrides: float) -> list[dict]:
    """Build a minimal raw_stats list with sensible defaults for tracked metrics."""
    defaults = {
        "CombinedKacoAcPowerHiRes": 1500.0,
        "LoadAcPower": 800.0,
        "DCBatteryPower": -200.0,
        "BatteryVolts": 52.4,
        "BattSocPercent": 78.0,
        "BatteryTemperature": 25.0,
        "BattOutToday": 3200.0,
        "BattInToday": 1800.0,
        "LoadAccumulatedToday": 5400.0,
        "ACInputToday": 0.0,
        "PercentageSolarOutput": 45.0,
        "Heatsink1Temp": 38.0,
        "FanSpeed": 1200.0,
        "absorb": 0.0,
        "bulk": 0.0,
        "float": 1.0,
        "GeneratorStatus": 0.0,
        "FloatHours": 3.5,
    }
    defaults.update(overrides)
    return [
        {"name": name, "value": value, "units": "", "description": ""}
        for name, value in defaults.items()
    ]


# ------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------

class TestSchema:
    def test_tables_created(self, store: HistoryStore):
        """All three tables should exist after init."""
        import sqlite3

        conn = sqlite3.connect(store._db_path)
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        assert "readings" in tables
        assert "readings_hourly" in tables
        assert "readings_daily" in tables
        assert "schema_version" in tables

    def test_schema_version(self, store: HistoryStore):
        import sqlite3

        conn = sqlite3.connect(store._db_path)
        row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
        conn.close()
        assert row[0] == 1


# ------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------

class TestRecord:
    def test_record_inserts_tracked_metrics(self, store: HistoryStore):
        stats = _make_stats()
        store.record(stats)
        counts = store.row_count()
        # Should have at least one row per tracked metric present in stats
        tracked_present = len([s for s in stats if s["name"] in TRACKED_METRICS])
        assert counts["readings"] == tracked_present

    def test_record_ignores_untracked_metrics(self, store: HistoryStore):
        stats = _make_stats()
        stats.append({"name": "UnitSerialNumber", "value": 12345, "units": "", "description": ""})
        store.record(stats)
        variables = store.available_variables()
        assert "UnitSerialNumber" not in variables

    def test_record_ignores_none_values(self, store: HistoryStore):
        stats = _make_stats()
        stats.append({"name": "BatteryVolts", "value": None, "units": "V", "description": ""})
        # BatteryVolts with None should be skipped, but the default one should still be inserted
        # Remove the default BatteryVolts first
        stats = [s for s in stats if not (s["name"] == "BatteryVolts" and s["value"] is not None)]
        stats.append({"name": "BatteryVolts", "value": None, "units": "V", "description": ""})
        store.record(stats)
        variables = store.available_variables()
        assert "BatteryVolts" not in variables

    def test_record_empty_list_is_noop(self, store: HistoryStore):
        store.record([])
        assert store.row_count()["readings"] == 0

    def test_multiple_records_accumulate(self, store: HistoryStore):
        store.record(_make_stats(BattSocPercent=80.0))
        store.record(_make_stats(BattSocPercent=79.0))
        # Each call should insert all tracked metrics
        counts = store.row_count()
        assert counts["readings"] > 0


# ------------------------------------------------------------------
# Querying
# ------------------------------------------------------------------

class TestQuery:
    def test_query_returns_raw_within_range(self, store: HistoryStore):
        store.record(_make_stats(BattSocPercent=80.0))
        results = store.query("BattSocPercent", "24h")
        assert len(results) >= 1
        assert "ts" in results[0]
        assert "value" in results[0]
        assert results[0]["value"] == pytest.approx(80.0)

    def test_query_returns_empty_for_unknown_variable(self, store: HistoryStore):
        store.record(_make_stats())
        results = store.query("NonExistentVar", "24h")
        assert results == []

    def test_query_different_ranges(self, store: HistoryStore):
        store.record(_make_stats())
        for r in ("1h", "6h", "24h", "7d", "30d", "1y"):
            results = store.query("BattSocPercent", r)
            assert isinstance(results, list)

    def test_available_variables(self, store: HistoryStore):
        store.record(_make_stats())
        variables = store.available_variables()
        assert "BattSocPercent" in variables
        assert "BatteryVolts" in variables
        assert len(variables) >= 10


# ------------------------------------------------------------------
# Aggregation
# ------------------------------------------------------------------

class TestAggregation:
    def test_aggregate_hourly_noop_when_no_old_data(self, store: HistoryStore):
        store.record(_make_stats())
        store.aggregate_hourly()
        assert store.row_count()["readings_hourly"] == 0

    def test_aggregate_daily_noop_when_no_old_data(self, store: HistoryStore):
        store.record(_make_stats())
        store.aggregate_daily()
        assert store.row_count()["readings_daily"] == 0


# ------------------------------------------------------------------
# Pruning
# ------------------------------------------------------------------

class TestPruning:
    def test_prune_does_not_delete_recent_data(self, store: HistoryStore):
        store.record(_make_stats())
        store.prune(raw_days=7, hourly_days=90)
        assert store.row_count()["readings"] > 0

    def test_prune_deletes_old_data(self, store: HistoryStore):
        """Insert a reading with an old timestamp, then prune it."""
        import sqlite3

        conn = sqlite3.connect(store._db_path)
        conn.execute(
            "INSERT INTO readings (ts, name, value, units) "
            "VALUES ('2020-01-01T00:00:00', 'BattSocPercent', 50.0, '%')"
        )
        conn.commit()
        conn.close()

        assert store.row_count()["readings"] == 1
        store.prune(raw_days=0)
        assert store.row_count()["readings"] == 0


# ------------------------------------------------------------------
# Row counts
# ------------------------------------------------------------------

class TestRowCounts:
    def test_row_count_empty_db(self, store: HistoryStore):
        counts = store.row_count()
        assert counts == {"readings": 0, "readings_hourly": 0, "readings_daily": 0}

    def test_row_count_after_record(self, store: HistoryStore):
        store.record(_make_stats())
        counts = store.row_count()
        assert counts["readings"] > 0
        assert counts["readings_hourly"] == 0
        assert counts["readings_daily"] == 0
