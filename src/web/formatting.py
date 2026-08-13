from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

INVERTER_MODE = {
    0: "Idle",
    1: "Econo",
    2: "On",
    3: "Sync",
}

AC_SOURCE_STATUS = {
    0: "AC Source Not Present",
    1: "E-N Link Not Detected",
    2: "AC Source in Tolerance",
    3: "AC Source in Tolerance",
    4: "AC Source in Tolerance",
    5: "AC Source in Tolerance",
    6: "Outside operating range",
    7: "AC Source in Tolerance",
    8: "Volts too high for freq",
    9: "Disconnected by DRM 0",
}

CHARGER_STATUS = {
    0: "Normal charge",
    1: "Override charge",
    2: "Charger Off",
    3: "Renewable charge",
    4: "Restricted charge",
}

MOD_STATUS = {
    0: "Not Fitted",
    1: "OK",
    2: "Fault",
}

STRING_INVERTER_SUPPORT = {
    0: "None",
    1: "ABB",
    2: "Fronius",
    3: "SMA",
    4: "Kaco",
    5: "Generic",
    6: "Selectronic",
}

DIGITAL_IO_STATUS = {
    0: "Off",
    1: "On",
}

# Service Required / Alert event codes (from mDataConvert.fnConvertAlertEventValueToString)
ALERT_EVENT = {
    2: "Inverter - Low Battery Voltage Alert",
    3: "Inverter - Low Battery Voltage Alert cleared",
    4: "Inverter - DC Shutdown",
    5: "Inverter - DC Shutdown cleared - Recovery Voltage reached",
    6: "Battery - Hi Battery Alert",
    7: "Battery - Hi Battery Alert Clear",
    10: "Charger - Battery Capacity Alert - Provided 120% Capacity and voltage target not achieved",
    11: "Charger - Battery Capacity Alert cleared - Voltage target achieved",
    12: "Inverter - Low SoC Alert",
    13: "Inverter - Low SoC Alert Cleared",
    14: "Inverter - SoC Shutdown",
    15: "Inverter - SoC Shutdown cleared",
    16: "Battery - Over Temp Protection Alert",
    17: "Battery - Over Temp Protection Alert cleared",
    18: "Generator Controller - Low Fuel Alert",
    19: "Generator Controller - Low Fuel Alert cleared",
    20: "Generator Controller - Generator Fault Alert - Stop generator",
    21: "Generator Controller - Generator Fault Alert cleared",
    22: "Generator Controller - No Fuel Alert - Stop generator",
    23: "Generator Controller - No Fuel Alert cleared",
    24: "Service - Fan Alert - Fan not spinning",
    25: "Service - Fan Alert cleared - Fan spinning or not required",
    26: "Inverter - Low AC Alert",
    27: "Inverter - Low AC Alert cleared",
    28: "Inverter - Low AC Shutdown",
    29: "Inverter - Low AC Shutdown cleared",
    30: "System - AC Load Voltage Alert - Volts detected from unknown source",
    31: "System - AC Load Voltage Alert cleared - No volts detected",
    32: "Battery - Outside Mid Point Range",
    33: "Battery - Within Mid Point Range",
    34: "Battery - Mid Point Fault - Outside Range after Equalise",
    35: "Battery - Mid Point Fault cleared",
    36: "AC Source - Safety Monitor Alert - Neutral and Earth are not at same potential",
    37: "AC Source - Safety Monitor Alert cleared",
    38: "Unit - Self Test Fault - Power Module",
    39: "Unit - Self Test Fault cleared - Power Module",
    40: "System - Power Module - Current Limit Shutdown",
    41: "System - Power Module - Current Limit Shutdown cleared",
    42: "System - Batt Sense Alert - measurement out of range - using internal voltage sense",
    43: "System - Batt Sense Alert cleared - using Batt Sense",
    44: "Unit - Self Test Fault - Auto Zero",
    45: "Unit - Self Test Fault cleared - Auto Zero",
    48: "Unit - Instant Hi DC Voltage Fault",
    49: "Unit - Instant Hi DC Voltage Fault cleared",
    50: "Unit - Instant Low DC Voltage Fault",
    51: "Unit - Instant Low DC Voltage Fault cleared",
    52: "Unit - Power Supply Shutdown",
    53: "Unit - Power Supply Shutdown cleared",
    54: "Unit - Power Module - Low 14V Shutdown",
    55: "Unit - Power Module - Low 14V Shutdown cleared",
    56: "System - AC Source Contactor Fault - Contactor stuck open",
    57: "System - AC Source Contactor Fault cleared - was open",
    58: "Unit - AC Source Contactor Fault - Contactor stuck closed",
    59: "Unit - AC Source Contactor Fault cleared - was closed",
    60: "Unit - AC Source Contactor Fault - Contactor stuck closed - Earth Neutral link not present",
    61: "Unit - AC Source Contactor Fault cleared - was closed - EN Link not present",
    62: "System - Synchronised Overload Shutdown",
    63: "System - Synchronised Overload Shutdown cleared",
    64: "System - Hi Temperature Alert",
    65: "System - Hi Temperature Alert cleared",
    66: "System - Hi Temperature Shutdown",
    67: "System - Hi Temperature Shutdown cleared",
    68: "Service - AC Source Safety Monitor State does not match State of Actual Switch",
    69: "Service - AC Source Safety Monitor State matches State of Actual Switch",
    74: "Service - Power Module 1 Capacitor Life Alert - Life at or above 95%",
    75: "Service - Power Module 1 Capacitor Life Alert cleared",
    76: "Service - Power Module 2 Capacitor Life Alert - Life at or above 95%",
    77: "Service - Power Module 2 Capacitor Life Alert cleared",
    78: "Service - Fan Speed Alert - Speed lower than expected - Check Fan",
    79: "Service - Fan Speed Alert cleared - Speed as expected",
    80: "Service - Fan Life Alert - Life at or above 100% - Replace Fan",
    81: "Service - Fan Life Alert cleared - Life reset to 0.",
    82: "Service - Fan Filter Alert - Clean Filter",
    83: "Service - Fan Filter Alert cleared - Filter clean button pressed",
    84: "Unit - AC Source contactor fault - inverter volts detected at AC Source",
    85: "Unit - AC Source contactor fault cleared",
    88: "Unit - Loading Configuration Settings has timed out - retrying",
    90: "Unit - Hi DC Voltage Fault",
    91: "Unit - Hi DC Voltage Fault cleared",
    92: "System - AC Load exceeding AC Source plus Inverter Rating",
    93: "System - AC Load below AC Source plus Inverter Rating",
    94: "System - Battery Temp sensor reading too high",
    95: "System - Battery Temp sensor ok - was too high",
    96: "System - Battery Temp sensor reading too low",
    97: "System - Battery Temp sensor ok - was too low",
    98: "System - Battery Temp sensor short circuit",
    99: "System - Battery Temp sensor ok - was shorted",
    100: "System - Battery Temp sensor open circuit",
    101: "System - Battery Temp sensor ok - was open",
    102: "Unit - Transformer Temp Fault - sensor reading too high",
    103: "Unit - Transformer Temp Fault cleared - was too high",
    104: "Unit - Transformer Temp Fault - sensor reading too low",
    105: "Unit - Transformer Temp Fault cleared - was too low",
    106: "Unit - Self Test Fault - Real Time Clock",
    107: "Unit - Self Test Fault cleared - Real Time Clock",
    108: "Unit - Real Time Clock - Reading same time",
    109: "Unit - Real Time Clock - Reading older time",
    110: "Unit - Real Time Clock - Reading newer time",
    111: "Unit - Real Time Clock - Did not interrupt",
    112: "Unit - Control PCA Factory defaults loaded",
    113: "Unit - Power Module 1 - Factory defaults loaded",
    114: "Unit - Power Module 2 - Factory defaults loaded",
    115: "System - Common defaults loaded",
    116: "System - Off Grid Unit Application defaults loaded",
    117: "System - Sealed Battery Type defaults loaded",
    118: "System - Service defaults loaded",
    119: "Unit - Output Mode button fault - button stuck down",
    120: "Unit - Generator button fault - button stuck down",
    121: "Unit - Alarm Silence button fault - button stuck down",
    122: "System - Reset",
    125: "Generator Controller - Stopped due to no AC Volts Fault",
    126: "Generator Controller - Stopped due to no AC Volts Fault Cleared",
    127: "System - Main DC Supply Cable Open Circuit Fault",
    128: "System - Main DC Supply Cable Open Circuit Fault Cleared",
    129: "System - Synchronisation Fail - AC Source unsuitable",
    130: "System - Synchronisation Fail - Cleared for retry",
    131: "Unit - Power Module - Current Limit Shutdown",
    132: "Unit - Power Module - Current Limit Shutdown Cleared",
    133: "Inverter - AC Source out of tolerance Beeper On",
    134: "Inverter - AC Source out of tolerance Beeper Off",
    135: "Inverter - AC Source out of phase On",
    136: "Inverter - AC Source out of phase Off",
    137: "System - Lost SP SYNCH connection On",
    138: "System - Lost SP SYNCH connection Off",
    139: "System - multi-phase system fault On",
    140: "System - multi-phase system fault Off",
    141: "System - multi-phase system fault forcing shutdown On",
    142: "System - multi-phase system fault forcing shutdown Off",
    143: "System - Hi Battery Shutdown (AC Coupled) Fault",
    144: "System - Hi Battery Shutdown (AC Coupled) Cleared",
    145: "System - AC Coupled Inverter #1 communication Fault",
    146: "System - AC Coupled Inverter #1 communication Fault Cleared",
    147: "System - AC Coupled Inverter #2 communication Fault",
    148: "System - AC Coupled Inverter #2 communication Fault Cleared",
    149: "System - AC Coupled Inverter #3 communication Fault",
    150: "System - AC Coupled Inverter #3 communication Fault Cleared",
    151: "System - AC Coupled Inverter #4 communication Fault",
    152: "System - AC Coupled Inverter #4 communication Fault Cleared",
    153: "System - AC Coupled Inverter #5 communication Fault",
    154: "System - AC Coupled Inverter #5 communication Fault Cleared",
    155: "System - AC Coupled frequency ramp invoked",
    156: "System - AC Coupled frequency ramp invoked off",
    157: "System - Glitch prevention",
    158: "System - Permanent Factory defaults loaded",
    159: "System - System Scheduler defaults loaded",
    160: "Inverter - Shutdown Input Active",
    161: "Inverter - Shutdown Input Active Cleared",
    162: "Battery Management - Alarm",
    163: "Battery Management - Alarm Cleared",
    164: "System - MPPT Fault",
    165: "System - MPPT Fault Cleared",
    166: "System - AC Coupled Inverter - Invalid device detected",
    167: "System - AC Coupled Inverter - Invalid device detected Cleared",
    168: "Service - Output Capacitor Life Alert - May need to replace capacitors",
    169: "Service - Output Capacitor Life Alert - May need to replace capacitors Cleared",
    170: "Service - High Frequency Output Ripple Detected - May need to replace capacitors",
    171: "Service - High Frequency Output Ripple Detected - May need to replace capacitors Cleared",
}


def alert_event_text(code: int | None) -> str:
    if code is None:
        return ""
    return ALERT_EVENT.get(code, "")


def inverter_mode_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return INVERTER_MODE.get(code, f"Unknown ({code})")


def ac_source_status_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return AC_SOURCE_STATUS.get(code, f"Unknown ({code})")


def charger_status_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return CHARGER_STATUS.get(code, f"Unknown ({code})")


def mod_status_text(code: int | None) -> str:
    if code is None:
        return ""
    return MOD_STATUS.get(code, f"Unknown ({code})")


def string_inverter_support_text(code: int | None) -> str:
    if code is None:
        return ""
    return STRING_INVERTER_SUPPORT.get(code, f"Unknown ({code})")


def digital_io_status_text(code: int | None) -> str:
    if code is None:
        return ""
    return DIGITAL_IO_STATUS.get(code, f"Unknown ({code})")


def software_version_text(code: int | None) -> str:
    if code is None or code == 0:
        return ""
    return f"{code / 100.0:.2f}"


def bcd_date_text(day_month: int | None, year: int | None) -> str:
    """Decode two BCD words into DD/MM/YYYY (see mDataConvert.fnConvertDateThatWasStoredInBCDToString)."""
    if day_month is None or year is None or day_month == 0 or year == 0:
        return ""
    day = ((day_month >> 12) & 0xF) * 10 + ((day_month >> 8) & 0xF)
    month = ((day_month >> 4) & 0xF) * 10 + (day_month & 0xF)
    yr = ((year >> 12) & 0xF) * 1000 + ((year >> 8) & 0xF) * 100 + ((year >> 4) & 0xF) * 10 + (year & 0xF)
    if day == 0 or month == 0 or yr == 0:
        return ""
    return f"{day:02d}/{month:02d}/{yr:04d}"


def bcd_time_text(time_bcd: int | None) -> str:
    """Decode a BCD word into HH:MM (see mDataConvert.fnConvertTimeThatWasStoredInBCDToString)."""
    if time_bcd is None or time_bcd == 0:
        return ""
    hour = ((time_bcd >> 12) & 0xF) * 10 + ((time_bcd >> 8) & 0xF)
    minute = ((time_bcd >> 4) & 0xF) * 10 + (time_bcd & 0xF)
    return f"{hour:02d}:{minute:02d}"


def serial_number_text(value: int | None) -> str:
    if value is None or value == 0 or value == 0xFFFFFFFF:
        return ""
    return f"{value:08d}"


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
    return _env_int("SELPI_BATTERY_SIZE_WH", 20000)


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


def _active_schedule_text(code: float) -> str:
    if code <= 0:
        return "None"
    if code >= 255:
        return "Alt AC Input"
    return f"Priority {int(code)}"


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


def kv(label: str, value: Any, unit: str = "") -> dict[str, Any]:
    """Compact key/value metric for list-style sections (history / extra)."""
    return {"label": label, "value": value, "unit": unit}


def _kwh(value: float) -> float:
    return round(value / 1000.0, 2)


def _kv_kwh(stat: float, decimals: int = 2) -> float:
    return round(stat / 1000.0, decimals)


# System capacity constants for parametric speed tiers
_MAX_SOLAR_W = 6000   # ABB string inverter max
_MAX_SP_PRO_W = 5000  # Selectronic SP PRO max
_MAX_SYSTEM_W = 11000 # Total system capacity (solar + SP PRO)


def _flow_speed(watts: float, max_watts: float) -> str:
    """Return CSS animation duration based on % of max rated power.

    Returns empty string for inactive connections (≤10W) so templates
    can skip rendering dots entirely.
    """
    if watts < 10:
        return ""
    ratio = watts / max_watts
    if ratio < 0.33:
        return "3s"
    if ratio < 0.66:
        return "1.5s"
    return "0.8s"


def _build_flow(stats_by_name: dict[str, Any]) -> dict[str, Any]:
    """Build the energy flow diagram data."""
    solar_w = stat_value(stats_by_name, "CombinedKacoAcPowerHiRes")
    load_w = stat_value(stats_by_name, "LoadAcPower")
    battery_w = stat_value(stats_by_name, "DCBatteryPower")
    gen_power = stat_value(stats_by_name, "ACGeneratorPower")

    # ABB string inverter (AC-coupled solar)
    abb_power_w = solar_w
    abb_percent = stat_value(stats_by_name, "PercentageSolarOutput")

    # Dynamic available max: 11kW when solar active, 5kW when not
    solar_active = solar_w > 10
    available_max = _MAX_SYSTEM_W if solar_active else _MAX_SP_PRO_W

    # Battery enrichment for the battery node
    batt_soc = stat_value(stats_by_name, "BattSocPercent")
    battery_size = battery_size_wh()
    shutdown = shutdown_percent()
    total_kwh_avail = battery_size * ((100 - shutdown) / 100)
    primary_kwh_avail = total_kwh_avail * (batt_soc / 100)
    soc_pct = (primary_kwh_avail / total_kwh_avail * 100) if total_kwh_avail else 0.0
    hours = hours_remaining(battery_size, batt_soc, battery_w)

    return {
        "solar_w": int(round(solar_w)),
        "solar_active": solar_active,
        "solar_speed": _flow_speed(solar_w, _MAX_SOLAR_W),
        "load_w": int(round(load_w)),
        "load_active": load_w > 10,
        "load_speed": _flow_speed(load_w, available_max),
        "battery_w": int(round(battery_w)),
        "battery_charging": battery_w < -10,
        "battery_discharging": battery_w > 10,
        "battery_active": abs(battery_w) > 10,
        "battery_speed": _flow_speed(abs(battery_w), _MAX_SP_PRO_W),
        "generator_w": int(round(gen_power)),
        "generator_active": gen_power > 10,
        "generator_speed": _flow_speed(gen_power, _MAX_SP_PRO_W),
        # ABB inverter enrichment
        "abb_power_w": int(round(abb_power_w)),
        "abb_percent": int(round(abb_percent)),
        "abb_active": abb_power_w > 10,
        # Battery enrichment for the battery node
        "soc_pct": round(soc_pct, 1),
        "soc_color": soc_color(soc_pct),
        "hours_remaining": round(hours, 1),
        "charge_state": charge_state(stats_by_name),
        "inv_freq_hz": round(stat_value(stats_by_name, "InvFreq"), 2),
    }


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

    # --- Attention Required (service required reasons) ---
    attention_reasons = []
    for i in range(20):
        code = stat_value(stats_by_name, f"ServiceRequiredReason{i}")
        if code > 0:
            text = alert_event_text(code)
            if text:
                attention_reasons.append(text)
    attention = {
        "any": len(attention_reasons) > 0 or stat_value(stats_by_name, "ServiceRequiredRed") > 0,
        "reasons": attention_reasons,
    }

    # --- History section (DC + AC accumulators) ---
    history = {
        "dc": {
            "inverter": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhPreviousAcc"))),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "InverterDCkWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhResetableAccAvg"), 3)),
                kv("Total", _kv_kwh(stat_value(stats_by_name, "InverterDCkWhTotalAcc"))),
            ],
            "shunt1": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhPreviousAcc"))),
                kv("Peak Power Prev", int(round(stat_value(stats_by_name, "Shunt1PeakPowerPrevious"))), "W"),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt1kWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhResetableAccAvg"), 3)),
                kv("Total", _kv_kwh(stat_value(stats_by_name, "Shunt1kWhTotalAcc"))),
            ],
            "shunt2": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhPreviousAcc"))),
                kv("Peak Power Prev", int(round(stat_value(stats_by_name, "Shunt2PeakPowerPrevious"))), "W"),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "Shunt2kWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhResetableAccAvg"), 3)),
                kv("Total", _kv_kwh(stat_value(stats_by_name, "Shunt2kWhTotalAcc"))),
            ],
            "battery": [
                kv("In Prev", _kv_kwh(stat_value(stats_by_name, "BattInkWhPreviousAcc"))),
                kv("In 7 Day", _kv_kwh(stat_value(stats_by_name, "BattInkWh7DayAcc"))),
                kv("In 7 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattInkWh7DayAccAvg"), 3)),
                kv("In 30 Day", _kv_kwh(stat_value(stats_by_name, "BattInkWh30DayAcc"))),
                kv("In 30 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattInkWh30DayAccAvg"), 3)),
                kv("In 365 Day", _kv_kwh(stat_value(stats_by_name, "BattInkWh365DayAcc"))),
                kv("In 365 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattInkWh365DayAccAvg"), 3)),
                kv("In Year", _kv_kwh(stat_value(stats_by_name, "BattInkWhYearAcc"))),
                kv("In Year Avg", _kv_kwh(stat_value(stats_by_name, "BattInkWhYearAccAvg"), 3)),
                kv("In Resetable", _kv_kwh(stat_value(stats_by_name, "BattInkWhResetableAcc"))),
                kv("In Resetable Avg", _kv_kwh(stat_value(stats_by_name, "BattInkWhResetableAccAvg"), 3)),
                kv("In Total", _kv_kwh(stat_value(stats_by_name, "BattInkWhTotalAcc"))),
                kv("Out Prev", _kv_kwh(stat_value(stats_by_name, "BattOutkWhPreviousAcc"))),
                kv("Out 7 Day", _kv_kwh(stat_value(stats_by_name, "BattOutkWh7DayAcc"))),
                kv("Out 7 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattOutkWh7DayAccAvg"), 3)),
                kv("Out 30 Day", _kv_kwh(stat_value(stats_by_name, "BattOutkWh30DayAcc"))),
                kv("Out 30 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattOutkWh30DayAccAvg"), 3)),
                kv("Out 365 Day", _kv_kwh(stat_value(stats_by_name, "BattOutkWh365DayAcc"))),
                kv("Out 365 Day Avg", _kv_kwh(stat_value(stats_by_name, "BattOutkWh365DayAccAvg"), 3)),
                kv("Out Year", _kv_kwh(stat_value(stats_by_name, "BattOutkWhYearAcc"))),
                kv("Out Year Avg", _kv_kwh(stat_value(stats_by_name, "BattOutkWhYearAccAvg"), 3)),
                kv("Out Resetable", _kv_kwh(stat_value(stats_by_name, "BattOutkWhResetableAcc"))),
                kv("Out Resetable Avg", _kv_kwh(stat_value(stats_by_name, "BattOutkWhResetableAccAvg"), 3)),
                kv("Out Total", _kv_kwh(stat_value(stats_by_name, "BattOutkWhTotalAcc"))),
                kv("Float Hrs Prev", int(round(stat_value(stats_by_name, "FloatHrsPreviousAcc"))), "h"),
                kv("Float Hrs 7 Day", int(round(stat_value(stats_by_name, "FloatHrs7DayAcc"))), "h"),
                kv("Float Hrs 7 Day Avg", int(round(stat_value(stats_by_name, "FloatHrs7DayAccAvg"))), "h"),
                kv("Float Hrs 30 Day", int(round(stat_value(stats_by_name, "FloatHrs30DayAcc"))), "h"),
                kv("Float Hrs 30 Day Avg", int(round(stat_value(stats_by_name, "FloatHrs30DayAccAvg"))), "h"),
                kv("Float Hrs 365 Day", int(round(stat_value(stats_by_name, "FloatHrs365DayAcc"))), "h"),
                kv("Float Hrs 365 Day Avg", int(round(stat_value(stats_by_name, "FloatHrs365DayAccAvg"))), "h"),
                kv("Float Hrs Year", int(round(stat_value(stats_by_name, "FloatHrsYearAcc"))), "h"),
                kv("Float Hrs Year Avg", int(round(stat_value(stats_by_name, "FloatHrsYearAccAvg"))), "h"),
            ],
        },
        "ac": {
            "load": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "ACLoadkWhPreviousAcc"))),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACLoadkWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "ACLoadkWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "ACLoadkWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "ACLoadkWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "ACLoadkWhResetableAccAvg"), 3)),
            ],
            "input": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "ACInputkWhPrevious"))),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "ACInputkWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACInputkWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "ACInputkWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACInputkWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "ACInputkWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACInputkWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "ACInputkWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "ACInputkWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "ACInputkWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "ACInputkWhResetableAccAvg"), 3)),
                kv("Input Hrs Prev", int(round(stat_value(stats_by_name, "ACInputHrsPreviousAcc"))), "h"),
                kv("Input Hrs 7 Day", int(round(stat_value(stats_by_name, "ACInputHrs7DayAcc"))), "h"),
                kv("Input Hrs 7 Day Avg", int(round(stat_value(stats_by_name, "ACInputHrs7DayAccAvg"))), "h"),
                kv("Input Hrs 30 Day", int(round(stat_value(stats_by_name, "ACInputHrs30DayAcc"))), "h"),
                kv("Input Hrs 30 Day Avg", int(round(stat_value(stats_by_name, "ACInputHrs30DayAccAvg"))), "h"),
                kv("Input Hrs 365 Day", int(round(stat_value(stats_by_name, "ACInputHrs365DayAcc"))), "h"),
                kv("Input Hrs 365 Day Avg", int(round(stat_value(stats_by_name, "ACInputHrs365DayAccAvg"))), "h"),
                kv("Input Hrs Year", int(round(stat_value(stats_by_name, "ACInputHrsYearAcc"))), "h"),
                kv("Input Hrs Year Avg", int(round(stat_value(stats_by_name, "ACInputHrsYearAccAvg"))), "h"),
                kv("Input Hrs Resetable", int(round(stat_value(stats_by_name, "ACInputHrsResetableAcc"))), "h"),
                kv("Input Hrs Resetable Avg", int(round(stat_value(stats_by_name, "ACInputHrsResetableAccAvg"))), "h"),
                kv("Input Hrs Total", int(round(stat_value(stats_by_name, "ACInputHrsTotalAcc"))), "h"),
            ],
            "export": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "ACExportkWhPrevious"))),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "ACExportkWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACExportkWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "ACExportkWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACExportkWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "ACExportkWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "ACExportkWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "ACExportkWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "ACExportkWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "ACExportkWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "ACExportkWhResetableAccAvg"), 3)),
                kv("Total", _kv_kwh(stat_value(stats_by_name, "ACExportkWhTotalAcc"))),
            ],
            "solar": [
                kv("Previous", _kv_kwh(stat_value(stats_by_name, "TotalKacokWhPreviousAcc"))),
                kv("7 Day", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh7DayAcc"))),
                kv("7 Day Avg", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh7DayAccAvg"), 3)),
                kv("30 Day", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh30DayAcc"))),
                kv("30 Day Avg", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh30DayAccAvg"), 3)),
                kv("365 Day", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh365DayAcc"))),
                kv("365 Day Avg", _kv_kwh(stat_value(stats_by_name, "TotalKacokWh365DayAccAvg"), 3)),
                kv("Year", _kv_kwh(stat_value(stats_by_name, "TotalKacokWhYearAcc"))),
                kv("Year Avg", _kv_kwh(stat_value(stats_by_name, "TotalKacokWhYearAccAvg"), 3)),
                kv("Resetable", _kv_kwh(stat_value(stats_by_name, "TotalKacokWhResetableAcc"))),
                kv("Resetable Avg", _kv_kwh(stat_value(stats_by_name, "TotalKacokWhResetableAccAvg"), 3)),
            ],
        },
    }

    # --- Extra section (tech data / system regulation / component life / IO) ---
    extra = {
        "system_regulation": [
            kv("Active Schedule", _active_schedule_text(stat_value(stats_by_name, "ActiveScheduler"))),
            kv("Charger Status", charger_status_text(int(stat_value(stats_by_name, "ChargerStatus")))),
            kv("Input Power Limit", int(round(stat_value(stats_by_name, "AcInputCapacity"))), "W"),
            kv("Export Power Limit", int(round(stat_value(stats_by_name, "AcExportCapacity"))), "W"),
            kv("Charge Power Limit", int(round(stat_value(stats_by_name, "InvDcChargeCapacity"))), "W"),
            kv("Support Power Limit", int(round(stat_value(stats_by_name, "InvDcSupportCapacity"))), "W"),
            kv("Export On Demand Target", int(round(stat_value(stats_by_name, "ExportOnDemandTarget"))), "W"),
            kv("Inverter Lockout", "Yes" if stat_value(stats_by_name, "InverterLockoutActive") > 0 else "No"),
            kv("AC Input Lockout", "Yes" if stat_value(stats_by_name, "AcInputLockoutActive") > 0 else "No"),
            kv("SoC Recovery Active", "Yes" if stat_value(stats_by_name, "SoCRecoveryIsActive") > 0 else "No"),
        ],
        "battery": [
            kv("DC Volts", round(stat_value(stats_by_name, "DCVolts"), 1), "V"),
            kv("Battery Sense Volts", round(stat_value(stats_by_name, "BatterySenseVolts"), 1), "V"),
            kv("Battery Mid Point", round(stat_value(stats_by_name, "BatteryMidPoint"), 1), "V"),
            kv("Charge Index", int(round(stat_value(stats_by_name, "ChargeIndex")))),
            kv("Battery Cable Loss", int(round(stat_value(stats_by_name, "BatteryCableLoss"))), "W"),
            kv("Days Since Equalise", int(round(stat_value(stats_by_name, "DaysSinceEqualise"))), "d"),
            kv("Days To Equalise", int(round(stat_value(stats_by_name, "DaysToEqualise"))), "d"),
            kv("Days To Recharge", int(round(stat_value(stats_by_name, "DaysToRecharge"))), "d"),
            kv("5 Min Battery Load", int(round(stat_value(stats_by_name, "BattLoad5Min"))), "W"),
            kv("15 Min Battery Load", int(round(stat_value(stats_by_name, "BattLoad15Min"))), "W"),
        ],
        "power": [
            kv("AC Inverter Power", int(round(stat_value(stats_by_name, "ACInverterPower"))), "W"),
            kv("Inverter Reactive Power", round(stat_value(stats_by_name, "InverterReactivePower"), 1)),
            kv("Load Volts HF Ripple", round(stat_value(stats_by_name, "LoadVoltsHighFrequencyRipple"), 1), "V"),
        ],
        "unit": [
            kv("Model Number", int(round(stat_value(stats_by_name, "UnitModelNumber")))),
            kv("Serial Number", serial_number_text(int(stat_value(stats_by_name, "UnitSerialNumber")))),
            kv("Rev Number", int(round(stat_value(stats_by_name, "UnitRevNumber")))),
            kv("Mod Status", mod_status_text(int(stat_value(stats_by_name, "UnitModStatus")))),
            kv("Software Version", software_version_text(int(stat_value(stats_by_name, "VersionNumber")))),
            kv("String Inverter Support", string_inverter_support_text(int(stat_value(stats_by_name, "StringInverterSupport")))),
            kv("Grid Software Version", software_version_text(int(stat_value(stats_by_name, "GridFirmwareVersion")))),
            kv("Build Date", bcd_date_text(int(stat_value(stats_by_name, "BuildDate1")), int(stat_value(stats_by_name, "BuildDate2")))),
            kv("Build Time", bcd_time_text(int(stat_value(stats_by_name, "BuildTime")))),
            kv("Control PCA Serial", serial_number_text(int(stat_value(stats_by_name, "ControlPCASerialNumber")))),
            kv("Control PCA Rev", int(round(stat_value(stats_by_name, "ControlPCARevNumber")))),
            kv("Control PCA Mod Status", mod_status_text(int(stat_value(stats_by_name, "ControlPCAModStatus")))),
            kv("PM1 Serial", serial_number_text(int(stat_value(stats_by_name, "PM1SerialNumber")))),
            kv("PM1 Rev", int(round(stat_value(stats_by_name, "PM1RevNumber")))),
            kv("PM1 Mod Status", mod_status_text(int(stat_value(stats_by_name, "PM1ModStatus")))),
            kv("PM2 Serial", serial_number_text(int(stat_value(stats_by_name, "PM2SerialNumber")))),
            kv("PM2 Rev", int(round(stat_value(stats_by_name, "PM2RevNumber")))),
            kv("PM2 Mod Status", mod_status_text(int(stat_value(stats_by_name, "PM2ModStatus")))),
        ],
        "component_life": [
            kv("Inverter Run Hours", int(round(stat_value(stats_by_name, "InverterRunHrsTotalAcc"))), "h"),
            kv("Fan Life", int(round(stat_value(stats_by_name, "FanLife"))), "%"),
            kv("Capacitor Life PM1", int(round(stat_value(stats_by_name, "CapacitorLifeConsumedPM1"))), "%"),
            kv("Capacitor Life PM2", int(round(stat_value(stats_by_name, "CapacitorLifeConsumedPM2"))), "%"),
            kv("AC Capacitor Life", int(round(stat_value(stats_by_name, "AcCapacitorPercentage"))), "%"),
        ],
        "io": [
            kv("Digital In 1", digital_io_status_text(int(stat_value(stats_by_name, "DigitalInStatus1")))),
            kv("Digital In 2", digital_io_status_text(int(stat_value(stats_by_name, "DigitalInStatus2")))),
            kv("Digital In 3", digital_io_status_text(int(stat_value(stats_by_name, "DigitalInStatus3")))),
            kv("Digital In 4", digital_io_status_text(int(stat_value(stats_by_name, "DigitalInStatus4")))),
            kv("Digital Out 1", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus1")))),
            kv("Digital Out 2", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus2")))),
            kv("Digital Out 3", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus3")))),
            kv("Digital Out 4", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus4")))),
            kv("Digital Out 5", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus5")))),
            kv("Digital Out 6", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus6")))),
            kv("Digital Out 7", digital_io_status_text(int(stat_value(stats_by_name, "DigitalOutStatus7")))),
            kv("General Purpose 1", round(stat_value(stats_by_name, "GeneralPurpose1"), 1), "V"),
            kv("General Purpose 2", round(stat_value(stats_by_name, "GeneralPurpose2"), 1), "V"),
        ],
    }

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
            "ac_out_status": inverter_mode_text(int(stat_value(stats_by_name, "AcOutStatus"))),
            "ac_source_status": ac_source_status_text(int(stat_value(stats_by_name, "AcSourceStatus"))),
            "charge_status": charger_status_text(int(stat_value(stats_by_name, "ChargeStatusForNow"))),
            "inv_freq_hz": round(stat_value(stats_by_name, "InvFreq"), 2),
        },
        "battery": {
            "volts": round(stat_value(stats_by_name, "BatteryVolts"), 2),
            "soc": round(batt_soc, 1),
            "soc_pct": round(soc_pct, 1),
            "soc_color": soc_color(soc_pct),
            "power_w": int(round(stat_value(stats_by_name, "DCBatteryPower"))),
            "temp_c": int(round(stat_value(stats_by_name, "BatteryTemperature"))),
            "current_a": round(stat_value(stats_by_name, "DCBatteryCurrent"), 2),
            "dc_current_a": round(stat_value(stats_by_name, "DCCurrent"), 2),
            "shunt1_amps": round(stat_value(stats_by_name, "Shunt1Amps"), 2),
            "shunt2_amps": round(stat_value(stats_by_name, "Shunt2Amps"), 2),
            "shunt1_power_w": int(round(stat_value(stats_by_name, "Shunt1Power"))),
            "shunt2_power_w": int(round(stat_value(stats_by_name, "Shunt2Power"))),
            "in_today_kwh": round(stat_value(stats_by_name, "BattInToday") / 1000, 2),
            "out_today_kwh": round(stat_value(stats_by_name, "BattOutToday") / 1000, 2),
            "net_today_kwh": round(stat_value(stats_by_name, "BattNetToday") / 1000, 2),
            "in_yesterday_kwh": round(stat_value(stats_by_name, "BattInYesterday") / 1000, 2),
            "out_yesterday_kwh": round(stat_value(stats_by_name, "BattOutYesterday") / 1000, 2),
            "float_hours": round(stat_value(stats_by_name, "FloatHours") / 60, 1),
        },
        "solar": {
            "power_w": int(round(stat_value(stats_by_name, "CombinedKacoAcPowerHiRes"))),
            "percent": int(round(stat_value(stats_by_name, "PercentageSolarOutput"))),
            "kaco1_w": int(round(stat_value(stats_by_name, "NowKaco1AcPower"))),
            "kaco2_w": int(round(stat_value(stats_by_name, "NowKaco2AcPower"))),
            "kaco3_w": int(round(stat_value(stats_by_name, "NowKaco3AcPower"))),
            "kaco4_w": int(round(stat_value(stats_by_name, "NowKaco4AcPower"))),
            "kaco5_w": int(round(stat_value(stats_by_name, "NowKaco5AcPower"))),
        },
        "load": {
            "power_w": int(round(stat_value(stats_by_name, "LoadAcPower"))),
            "today_kwh": round(stat_value(stats_by_name, "LoadAccumulatedToday") / 1000, 2),
            "inverter_power_w": int(round(stat_value(stats_by_name, "ACInverterPower"))),
            "inverter_rms_volts": round(stat_value(stats_by_name, "ACInverterRmsVolts"), 1),
            "inverter_rms_amps": round(stat_value(stats_by_name, "ACInverterRmsAmps"), 2),
        },
        "generator": {
            "status": generator_status_text(int(stat_value(stats_by_name, "GeneratorStatus"))),
            "start_reason": generator_reason_text(int(stat_value(stats_by_name, "GeneratorStartReason"))),
            "running_reason": generator_reason_text(int(stat_value(stats_by_name, "GeneratorRunningReason"))),
            "ac_today_kwh": round(stat_value(stats_by_name, "ACInputToday") / 1000, 2),
            "ac_yesterday_kwh": round(stat_value(stats_by_name, "ACInputYesterday") / 1000, 2),
            "power_w": int(round(stat_value(stats_by_name, "ACGeneratorPower"))),
            "power_5min_avg_w": int(round(stat_value(stats_by_name, "ACGeneratorPower5minAvg"))),
            "rms_volts": round(stat_value(stats_by_name, "ACGeneratorRmsVolts"), 1),
            "rms_amps": round(stat_value(stats_by_name, "ACGeneratorRmsAmps"), 2),
            "input_hz": round(stat_value(stats_by_name, "InputACHz"), 2),
            "max_available_input_w": int(round(stat_value(stats_by_name, "MaxAvailableInputkW"))),
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
        "attention": attention,
        "history": history,
        "extra": extra,
        "flow": _build_flow(stats_by_name),
    }
