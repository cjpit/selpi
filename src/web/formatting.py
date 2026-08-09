from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

GENERATOR_STATUS = {
    0: "Not Running",
    1: "Running",
    2: "Low Fuel",
    3: "No Fuel",
    4: "Fault",
    5: "Not Available",
    6: "Starting",
    7: "Retry Pause",
    8: "Stopping",
    9: "Disabled",
    10: "AC Source Present",
}

GENERATOR_REASON = {
    0: "Not Running",
    1: "Front Panel",
    2: "Remote Run Request",
    3: "Run Schedule",
    4: "Hi Inverter Temp.",
    5: "Impending Inverter Shutdown",
    6: "Synchronisation Fault",
    7: "State of Charge",
    8: "Low Battery Volts",
    9: "Battery Mid Point Voltage Error",
    10: "Equalising Battery",
    11: "Hi AC Load",
    12: "Generator Exercise",
    13: "Generator Available",
    14: "Generator Fault",
    15: "Minimum Runtime",
    16: "Generator Lock Out Active",
    17: "Battery Float",
    18: "Cooling Down",
    19: "Confirmed Start",
    20: "Manual",
    21: "AC Source Present",
    22: "Disabled",
    23: "Support Mode",
    24: "Equalise",
    25: "Battery Load",
    29: "Warming Up",
}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def battery_size_wh() -> int:
    return _env_int("SELPI_BATTERY_SIZE_WH", 17000)


def shutdown_percent() -> int:
    return _env_int("SELPI_SHUTDOWN_PERCENT", 10)


def refresh_seconds() -> int:
    return _env_int("SELPI_HTTP_REFRESH_SECONDS", 5)


def generator_status_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return GENERATOR_STATUS.get(code, "Unknown")


def generator_reason_text(code: int | None) -> str:
    if code is None:
        return ""
    return GENERATOR_REASON.get(code, "")


def soc_color(soc: float) -> str:
    if soc < 30:
        return "red"
    if soc < 50:
        return "orange"
    return "green"


def hours_color(hours: float) -> str:
    if hours < 8:
        return "red"
    if hours < 12:
        return "orange"
    return "green"


def hours_remaining(battery_size_wh: int, soc: float, battery_power_w: float) -> float:
    if battery_power_w <= 0:
        discharge_w = 100.0
    else:
        discharge_w = battery_power_w
    watts_left = battery_size_wh * (soc / 100.0)
    hours = watts_left / discharge_w
    if hours > 24:
        hours = 24.0
    return hours


def charge_state(stats_by_name: dict[str, Any]) -> str:
    if stat_value(stats_by_name, "bulk") > 0:
        return "Bulk"
    if stat_value(stats_by_name, "absorb") > 0:
        return "Absorb"
    if stat_value(stats_by_name, "float") > 0:
        return "Float"
    return "Unknown"


def stat_value(stats_by_name: dict[str, Any], name: str, default: float = 0.0) -> float:
    item = stats_by_name.get(name)
    if item is None:
        return default
    value = item.get("value")
    if value is None:
        return default
    if isinstance(value, dict):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_view_model(raw_stats: list[dict[str, Any]]) -> dict[str, Any]:
    stats_by_name = {item["name"]: item for item in raw_stats}

    batt_soc = stat_value(stats_by_name, "BattSocPercent")
    battery_power = stat_value(stats_by_name, "DCBatteryPower")
    battery_size = battery_size_wh()
    shutdown = shutdown_percent()
    total_kwh_avail = battery_size * ((100 - shutdown) / 100)
    primary_kwh_avail = total_kwh_avail * (batt_soc / 100)
    soc_pct = (primary_kwh_avail / total_kwh_avail * 100) if total_kwh_avail else 0.0
    hours = hours_remaining(battery_size, batt_soc, battery_power)
    hours_pct = (hours / 24.0 * 100) if hours else 0.0

    alarms = []
    if stat_value(stats_by_name, "GeneratorRed") > 0:
        alarms.append({"id": "generator", "label": "Generator Alarm", "active": True})
    if stat_value(stats_by_name, "OverTempRed") > 0:
        alarms.append({"id": "over_temp", "label": "Over Temp Alarm", "active": True})
    if stat_value(stats_by_name, "ServiceRequiredRed") > 0:
        alarms.append({"id": "service", "label": "Service Required Alarm", "active": True})
    if stat_value(stats_by_name, "ShutdownRed") > 0:
        alarms.append({"id": "shutdown", "label": "Shutdown Alarm", "active": True})

    return {
        "meta": {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "connected": True,
            "error": None,
        },
        "overview": {
            "soc": round(soc_pct, 1),
            "soc_color": soc_color(soc_pct),
            "hours_remaining": round(hours, 1),
            "hours_color": hours_color(hours),
            "hours_pct": round(hours_pct, 1),
            "solar_w": int(round(stat_value(stats_by_name, "CombinedKacoAcPowerHiRes"))),
            "load_w": int(round(stat_value(stats_by_name, "LoadAcPower"))),
            "battery_w": int(round(stat_value(stats_by_name, "DCBatteryPower"))),
            "battery_state": charge_state(stats_by_name),
        },
        "battery": {
            "volts": round(stat_value(stats_by_name, "BatteryVolts"), 2),
            "soc": round(batt_soc, 1),
            "power_w": int(round(stat_value(stats_by_name, "DCBatteryPower"))),
            "temp_c": int(round(stat_value(stats_by_name, "BatteryTemperature"))),
            "in_today_kwh": round(stat_value(stats_by_name, "BattInToday") / 1000, 2),
            "out_today_kwh": round(stat_value(stats_by_name, "BattOutToday") / 1000, 2),
            "net_today_kwh": round(stat_value(stats_by_name, "BattNetToday") / 1000, 2),
            "in_yesterday_kwh": round(stat_value(stats_by_name, "BattInYesterday") / 1000, 2),
            "out_yesterday_kwh": round(stat_value(stats_by_name, "BattOutYesterday") / 1000, 2),
            "float_hours": int(round(stat_value(stats_by_name, "FloatHours"))),
        },
        "solar": {
            "power_w": int(round(stat_value(stats_by_name, "CombinedKacoAcPowerHiRes"))),
            "percent": int(round(stat_value(stats_by_name, "PercentageSolarOutput"))),
        },
        "load": {
            "power_w": int(round(stat_value(stats_by_name, "LoadAcPower"))),
            "today_kwh": round(stat_value(stats_by_name, "LoadAccumulatedToday") / 1000, 2),
        },
        "generator": {
            "status": generator_status_text(int(stat_value(stats_by_name, "GeneratorStatus"))),
            "start_reason": generator_reason_text(int(stat_value(stats_by_name, "GeneratorStartReason"))),
            "running_reason": generator_reason_text(int(stat_value(stats_by_name, "GeneratorRunningReason"))),
            "ac_today_kwh": round(stat_value(stats_by_name, "ACInputToday") / 1000, 2),
            "ac_yesterday_kwh": round(stat_value(stats_by_name, "ACInputYesterday") / 1000, 2),
        },
        "temperatures": {
            "battery_c": int(round(stat_value(stats_by_name, "BatteryTemperature"))),
            "inlet_c": int(round(stat_value(stats_by_name, "InletTemp"))),
            "board_c": int(round(stat_value(stats_by_name, "ControlBoardTemp"))),
            "heatsink1_c": int(round(stat_value(stats_by_name, "Heatsink1Temp"))),
            "heatsink2_c": int(round(stat_value(stats_by_name, "Heatsink2Temp"))),
            "transformer_c": int(round(stat_value(stats_by_name, "TransformerTemp"))),
            "fan_rpm": int(round(stat_value(stats_by_name, "FanSpeed"))),
        },
        "alarms": {
            "any": len(alarms) > 0,
            "items": alarms,
        },
    }
