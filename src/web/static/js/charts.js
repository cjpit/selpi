/**
 * Selpi Charts — uPlot-based time-series charting.
 *
 * Fetches data from /api/history/<var>?range=<range> and renders into
 * chart containers using uPlot (loaded from CDN).
 */

/* global uPlot */

"use strict";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let currentRange = "24h";
let activeCharts = {};   // variableName → uPlot instance
let refreshTimer = null;

// Human-friendly labels for tracked metrics
const METRIC_LABELS = {
    CombinedKacoAcPowerHiRes: "Solar Power",
    LoadAcPower: "Load Power",
    DCBatteryPower: "Battery Power",
    ACGeneratorPower: "Generator Power",
    Shunt1Power: "Shunt 1 Power",
    Shunt2Power: "Shunt 2 Power",
    BatteryVolts: "Battery Voltage",
    BattSocPercent: "State of Charge",
    DCBatteryCurrent: "Battery Current",
    BatteryTemperature: "Battery Temp",
    BattOutToday: "Battery Out Today",
    BattInToday: "Battery In Today",
    LoadAccumulatedToday: "Load Today",
    ACInputToday: "AC Input Today",
    PercentageSolarOutput: "Solar Output %",
    Heatsink1Temp: "Heatsink 1 Temp",
    Heatsink2Temp: "Heatsink 2 Temp",
    ControlBoardTemp: "Control Board Temp",
    InletTemp: "Inlet Temp",
    TransformerTemp: "Transformer Temp",
    FanSpeed: "Fan Speed",
    absorb: "Absorb",
    bulk: "Bulk",
    float: "Float",
    GeneratorStatus: "Generator Status",
    FloatHours: "Float Hours",
};

// Predefined chart groups
const CHART_GROUPS = [
    {
        id: "power",
        title: "Power (W)",
        metrics: ["CombinedKacoAcPowerHiRes", "LoadAcPower", "DCBatteryPower", "Shunt1Power", "Shunt2Power"],
    },
    {
        id: "battery",
        title: "Battery",
        metrics: ["BatteryVolts", "BattSocPercent", "DCBatteryCurrent", "BatteryTemperature"],
    },
    {
        id: "energy",
        title: "Energy Today (Wh)",
        metrics: ["BattOutToday", "BattInToday", "LoadAccumulatedToday", "ACInputToday"],
    },
    {
        id: "solar",
        title: "Solar",
        metrics: ["PercentageSolarOutput"],
    },
    {
        id: "temps",
        title: "Temperatures (°C)",
        metrics: ["Heatsink1Temp", "Heatsink2Temp", "ControlBoardTemp", "InletTemp", "TransformerTemp", "BatteryTemperature"],
    },
    {
        id: "generator",
        title: "Generator",
        metrics: ["ACGeneratorPower", "GeneratorStatus"],
    },
];

// Series colours (cycle for multi-metric charts)
const SERIES_COLORS = [
    "#4fc3f7", "#81c784", "#ffb74d", "#f06292",
    "#ba68c8", "#4db6ac", "#ff8a65", "#aed581",
];

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function fetchHistory(variable, range) {
    const resp = await fetch(`/api/history/${encodeURIComponent(variable)}?range=${encodeURIComponent(range)}`);
    if (!resp.ok) return null;
    return await resp.json();
}

// ---------------------------------------------------------------------------
// uPlot rendering
// ---------------------------------------------------------------------------

function parseTs(ts) {
    // Parse "YYYY-MM-DDTHH:MM:SS" as local time → unix epoch seconds
    return new Date(ts.replace("T", " ") + " UTC").getTime() / 1000;
}

function buildSeriesOpts(metricNames) {
    return metricNames.map((name, i) => ({
        label: METRIC_LABELS[name] || name,
        stroke: SERIES_COLORS[i % SERIES_COLORS.length],
        width: 1.5,
    }));
}

function renderChart(container, metricNames, datasets, range) {
    // datasets: [{ts, value}...] per metric
    // Merge all timestamps into a sorted unique array
    const allTs = new Set();
    for (const ds of datasets) {
        if (!ds) continue;
        for (const p of ds) {
            allTs.add(parseTs(p.ts));
        }
    }
    const timestamps = Array.from(allTs).sort((a, b) => a - b);
    if (timestamps.length === 0) {
        container.innerHTML = '<div class="chart-empty">No data available</div>';
        return null;
    }

    // Build a lookup: metricIdx → {ts → value}
    const lookups = datasets.map(ds => {
        if (!ds) return {};
        const m = {};
        for (const p of ds) {
            m[parseTs(p.ts)] = p.avg !== undefined ? p.avg : p.value;
        }
        return m;
    });

    // Build uPlot data: [timestamps, ...seriesValues]
    const data = [new Float64Array(timestamps)];
    for (let mi = 0; mi < metricNames.length; mi++) {
        const vals = new Float64Array(timestamps.length);
        const lookup = lookups[mi];
        for (let ti = 0; ti < timestamps.length; ti++) {
            const v = lookup[timestamps[ti]];
            vals[ti] = v !== undefined ? v : null;
        }
        data.push(vals);
    }

    const seriesOpts = [{}].concat(buildSeriesOpts(metricNames));

    // Determine time axis format based on range
    let fmtDate;
    if (range === "1h" || range === "6h") {
        fmtDate = uPlot.fmtDate("{HH}:{mm}");
    } else if (range === "24h") {
        fmtDate = uPlot.fmtDate("{HH}:{mm}");
    } else {
        fmtDate = uPlot.fmtDate("{DD}/{MM}");
    }

    const opts = {
        width: container.clientWidth || 800,
        height: 300,
        series: seriesOpts,
        axes: [
            {
                stroke: "#888",
                grid: { stroke: "rgba(255,255,255,0.05)" },
                values: (u, vals) => vals.map(v => fmtDate(new Date(v * 1000))),
            },
            {
                stroke: "#888",
                grid: { stroke: "rgba(255,255,255,0.08)" },
            },
        ],
        cursor: {
            y: false,
        },
    };

    container.innerHTML = "";
    const uplot = new uPlot(opts, data, container);
    return uplot;
}

// ---------------------------------------------------------------------------
// Chart group rendering
// ---------------------------------------------------------------------------

async function renderChartGroup(group, range) {
    const container = document.getElementById(`chart-group-${group.id}`);
    if (!container) return;

    // Fetch data for all metrics in parallel
    const results = await Promise.all(
        group.metrics.map(m => fetchHistory(m, range))
    );

    // Find which metrics actually have data
    const activeMetrics = [];
    const activeData = [];
    for (let i = 0; i < group.metrics.length; i++) {
        if (results[i] && results[i].points && results[i].points.length > 0) {
            activeMetrics.push(group.metrics[i]);
            activeData.push(results[i].points);
        }
    }

    if (activeMetrics.length === 0) {
        container.innerHTML = '<div class="chart-empty">No data yet — charts will appear once history is collected.</div>';
        return;
    }

    // Destroy old chart if exists
    if (activeCharts[group.id]) {
        activeCharts[group.id].destroy();
    }

    activeCharts[group.id] = renderChart(container, activeMetrics, activeData, range);
}

async function renderAllCharts() {
    for (const group of CHART_GROUPS) {
        await renderChartGroup(group, currentRange);
    }
}

// ---------------------------------------------------------------------------
// Range button handlers
// ---------------------------------------------------------------------------

function setRange(range) {
    currentRange = range;

    // Update active button state
    document.querySelectorAll(".chart-range-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.range === range);
    });

    renderAllCharts();
}

// ---------------------------------------------------------------------------
// Tab activation & auto-refresh
// ---------------------------------------------------------------------------

function startRefresh() {
    stopRefresh();
    refreshTimer = setInterval(renderAllCharts, 60000); // refresh every 60s
}

function stopRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

// Called when the Charts tab becomes visible
function onChartsTabActive() {
    renderAllCharts();
    startRefresh();
}

function onChartsTabInactive() {
    stopRefresh();
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

function initCharts() {
    // Range buttons
    document.querySelectorAll(".chart-range-btn").forEach(btn => {
        btn.addEventListener("click", () => setRange(btn.dataset.range));
    });

    // Observe tab changes via MutationObserver on the charts panel
    const panel = document.getElementById("tab-charts");
    if (panel) {
        const observer = new MutationObserver(mutations => {
            for (const m of mutations) {
                if (m.attributeName === "style") {
                    const visible = panel.style.display !== "none" &&
                                   !panel.hasAttribute("data-show-hidden");
                    if (visible) {
                        onChartsTabActive();
                    } else {
                        onChartsTabInactive();
                    }
                }
            }
        });
        observer.observe(panel, { attributes: true, attributeFilter: ["style"] });

        // Also check initial state
        const display = getComputedStyle(panel).display;
        if (display !== "none") {
            onChartsTabActive();
        }
    }
}

// Datastar uses data-show which toggles display. We need a simpler approach:
// Hook into the Datastar signal for tab changes.
document.addEventListener("click", (e) => {
    if (e.target.closest('[data-on:click*="charts"]')) {
        // Small delay to let Datastar update the visibility
        setTimeout(onChartsTabActive, 50);
    }
});

// Initialise when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCharts);
} else {
    initCharts();
}
