"use strict";

window.__consoleErrors = [];
window.addEventListener("error", (event) => {
  window.__consoleErrors.push(event.message || "Unknown browser error");
});
window.addEventListener("unhandledrejection", (event) => {
  window.__consoleErrors.push(String(event.reason || "Unhandled promise rejection"));
});

const state = { data: null, activeView: "executive" };
const money = new Intl.NumberFormat("th-TH", { maximumFractionDigits: 0 });
const decimal = new Intl.NumberFormat("th-TH", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const formatMillions = (value, digits = 3) => `${Number(value / 1_000_000).toLocaleString("th-TH", {
  minimumFractionDigits: digits,
  maximumFractionDigits: digits,
})} ลบ.`;

const formatBaht = (value) => `฿${money.format(Math.round(value))}`;
const formatPercent = (value, digits = 1) => `${(Number(value) * 100).toLocaleString("th-TH", {
  minimumFractionDigits: digits,
  maximumFractionDigits: digits,
})}%`;

const shortDate = (iso) => {
  if (!iso) return "ไม่ระบุ";
  return new Intl.DateTimeFormat("th-TH", { day: "numeric", month: "short", year: "numeric" })
    .format(new Date(iso));
};

function setActiveView(view) {
  state.activeView = view;
  document.querySelectorAll("[data-view-button]").forEach((button) => {
    const active = button.dataset.viewButton === view;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-current", active ? "page" : "false");
  });
  document.querySelectorAll("[data-view-panel]").forEach((panel) => {
    const active = panel.dataset.viewPanel === view;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  });
  const panel = document.querySelector(`[data-view-panel="${view}"]`);
  if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function metricCard({ label, value, context, chip, chipClass = "", className = "" }) {
  return `
    <article class="metric-card ${className}">
      <div class="metric-label"><span>${escapeHtml(label)}</span><span class="metric-chip ${chipClass}">${escapeHtml(chip)}</span></div>
      <div class="metric-value ${String(value).length > 13 ? "text-value" : ""}">${escapeHtml(value)}</div>
      <div class="metric-context">${escapeHtml(context)}</div>
    </article>`;
}

function renderMetrics(data) {
  const h = data.headline;
  const q = data.quality;
  const comparison = data.meta.comparison;
  const cards = [
    metricCard({
      label: "Actual baseline 2025",
      value: formatMillions(h.annual_2025_cost),
      context: `Rev.1 ต่างจาก baseline เดิม ${formatBaht(h.baseline_difference)}`,
      chip: "OBSERVED",
      className: "metric-primary",
    }),
    metricCard({
      label: `Actual ${comparison.current_year} comparable`,
      value: formatMillions(h.current_comparable_cost),
      context: `เทียบฐานช่วงเดียวกัน ${formatMillions(h.baseline_comparable_cost)}`,
      chip: "ACTUAL-ONLY",
      chipClass: "chip-warning",
      className: "metric-warning",
    }),
    metricCard({
      label: "Analytical reduction",
      value: formatPercent(h.apparent_reduction_pct, 2),
      context: `ส่วนต่าง ${formatMillions(h.gross_apparent_reduction)} · ยังไม่รวม exposure ครบ`,
      chip: "PROVISIONAL",
      chipClass: "chip-warning",
      className: "metric-warning",
    }),
    metricCard({
      label: "Finance-approved saving",
      value: "ยังไม่รับรอง",
      context: "รอ Commitment + Accrual + Finance reconciliation + Saving ledger",
      chip: "BLOCKED",
      chipClass: "chip-blocked",
      className: "metric-blocked",
    }),
    metricCard({
      label: "Data trust gates",
      value: `${q.pass_count}/${q.gates.length} ผ่าน`,
      context: `${q.fail_count} fail · ${q.blocked_count} blocked · SLA H1/2026 ${formatPercent(data.operations.current_sla_met_rate)}`,
      chip: "NEEDS ACTION",
      chipClass: "chip-blocked",
      className: "metric-blocked",
    }),
  ];
  document.getElementById("metric-grid").innerHTML = cards.join("");
}

function svgFrame(width, height, content, label) {
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}" preserveAspectRatio="xMidYMid meet">${content}</svg>`;
}

function renderMonthlyChart(data) {
  const rows = data.comparableMonths;
  const years = [...new Set(rows.map((row) => row.year))].sort();
  const months = [...new Set(rows.map((row) => row.month_number))].sort((a, b) => a - b);
  const monthNames = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
  const lookup = new Map(rows.map((row) => [`${row.year}-${row.month_number}`, row.cost]));
  const width = 960;
  const height = 310;
  const margin = { top: 30, right: 22, bottom: 54, left: 58 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const maxValue = Math.max(...rows.map((row) => row.cost)) * 1.14;
  const y = (value) => margin.top + innerH - (value / maxValue) * innerH;
  const groupW = innerW / months.length;
  const barW = Math.min(34, groupW * 0.28);
  let content = "";

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = (maxValue / 4) * tick;
    const yy = y(value);
    content += `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${yy}" y2="${yy}" />`;
    content += `<text x="${margin.left - 9}" y="${yy + 4}" text-anchor="end">${(value / 1_000_000).toFixed(1)}</text>`;
  }

  months.forEach((month, index) => {
    const center = margin.left + groupW * (index + 0.5);
    years.forEach((year, yearIndex) => {
      const value = lookup.get(`${year}-${month}`) || 0;
      const xx = center + (yearIndex === 0 ? -barW - 2 : 2);
      const yy = y(value);
      const barHeight = margin.top + innerH - yy;
      const klass = yearIndex === 0 ? "bar-baseline" : "bar-current";
      content += `<rect class="${klass}" x="${xx}" y="${yy}" width="${barW}" height="${barHeight}" rx="3"><title>${monthNames[month - 1]} ${year}: ${formatBaht(value)}</title></rect>`;
      content += `<text class="value-label" x="${xx + barW / 2}" y="${Math.max(14, yy - 6)}" text-anchor="middle">${(value / 1_000_000).toFixed(2)}</text>`;
    });
    content += `<text class="axis-label" x="${center}" y="${height - 23}" text-anchor="middle">${monthNames[month - 1]}</text>`;
  });
  content += `<line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${margin.top + innerH}" y2="${margin.top + innerH}" />`;

  document.getElementById("monthly-chart").innerHTML = svgFrame(width, height, content, `ค่าใช้จ่ายรายเดือน ${years.join(" เทียบ ")}`)
    + `<div class="chart-legend"><span class="legend-item"><i class="legend-swatch" style="background:#123452"></i>${years[0]} baseline</span><span class="legend-item"><i class="legend-swatch" style="background:#007a9e"></i>${years[1]} current</span></div>`;
}

function renderWaterfall(data) {
  const bridge = data.engineeringDecomposition;
  const stages = [
    { label: "H1/2025", type: "total", value: bridge.baseline },
    { label: "Volume", type: "delta", value: bridge.volume_effect },
    { label: "PM/CM mix", type: "delta", value: bridge.work_type_mix_effect },
    { label: "Rate / scope", type: "delta", value: bridge.rate_scope_and_exposure_effect },
    { label: "H1/2026", type: "total", value: bridge.current },
  ];
  const width = 650;
  const height = 310;
  const margin = { top: 30, right: 18, bottom: 58, left: 48 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const maxValue = bridge.baseline * 1.12;
  const y = (value) => margin.top + innerH - (value / maxValue) * innerH;
  const stepW = innerW / stages.length;
  const barW = Math.min(70, stepW * 0.62);
  let running = bridge.baseline;
  let content = "";

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = (maxValue / 4) * tick;
    const yy = y(value);
    content += `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${yy}" y2="${yy}" />`;
    content += `<text x="${margin.left - 7}" y="${yy + 4}" text-anchor="end">${(value / 1_000_000).toFixed(1)}</text>`;
  }

  stages.forEach((stage, index) => {
    const center = margin.left + stepW * (index + 0.5);
    let top;
    let bottom;
    let klass;
    if (stage.type === "total") {
      top = stage.value;
      bottom = 0;
      klass = "bar-total";
      running = stage.value;
    } else {
      const next = running + stage.value;
      top = Math.max(running, next);
      bottom = Math.min(running, next);
      klass = stage.value <= 0 ? "bar-negative" : "bar-positive";
      if (index < stages.length - 1) {
        const connectorY = y(next);
        content += `<line x1="${center + barW / 2}" x2="${center + stepW - barW / 2}" y1="${connectorY}" y2="${connectorY}" stroke="#aab6c0" stroke-dasharray="3 3" />`;
      }
      running = next;
    }
    const yy = y(top);
    const barHeight = Math.max(2, y(bottom) - yy);
    content += `<rect class="${klass}" x="${center - barW / 2}" y="${yy}" width="${barW}" height="${barHeight}" rx="4"><title>${stage.label}: ${stage.type === "delta" && stage.value > 0 ? "+" : ""}${formatBaht(stage.value)}</title></rect>`;
    const labelY = stage.type === "total" ? yy - 8 : (stage.value < 0 ? y(bottom) + 17 : yy - 8);
    const signed = stage.type === "delta" && stage.value > 0 ? "+" : "";
    content += `<text class="value-label" x="${center}" y="${labelY}" text-anchor="middle">${signed}${(stage.value / 1_000_000).toFixed(3)}</text>`;
    content += `<text class="axis-label" x="${center}" y="${height - 24}" text-anchor="middle">${escapeHtml(stage.label)}</text>`;
  });

  document.getElementById("waterfall-chart").innerHTML = svgFrame(width, height, content, "Engineering decomposition จาก baseline ไป current");
}

function renderHorizontalBars(elementId, rows, options = {}) {
  const selected = rows.slice(0, options.limit || 7);
  const width = options.width || 650;
  const left = options.left || 220;
  const rowH = options.rowH || 38;
  const top = 12;
  const height = top + selected.length * rowH + 18;
  const right = 90;
  const innerW = width - left - right;
  const maxValue = Math.max(...selected.map((row) => row.cost));
  let content = "";
  selected.forEach((row, index) => {
    const yy = top + index * rowH;
    const barWidth = (row.cost / maxValue) * innerW;
    const label = options.labelTransform ? options.labelTransform(row.category) : row.category;
    content += `<text class="axis-label" x="${left - 10}" y="${yy + 18}" text-anchor="end">${escapeHtml(label)}</text>`;
    content += `<rect class="pareto-bar" x="${left}" y="${yy + 3}" width="${barWidth}" height="22" rx="3"><title>${escapeHtml(row.category)}: ${formatBaht(row.cost)} · ${money.format(row.rows)} งาน</title></rect>`;
    content += `<text class="value-label" x="${left + barWidth + 8}" y="${yy + 19}">${(row.cost / 1_000_000).toFixed(2)}M</text>`;
  });
  document.getElementById(elementId).innerHTML = svgFrame(width, height, content, options.ariaLabel || "กราฟแท่งค่าใช้จ่าย");
}

function renderProblemChart(data) {
  const rows = data.problemType;
  renderHorizontalBars("problem-chart", rows, {
    limit: 6,
    width: 650,
    left: 250,
    ariaLabel: "ค่าใช้จ่ายตามระบบงาน",
    labelTransform: (label) => String(label).replace(/^[A-Z0-9]+\s*-\s*/, ""),
  });
  const topTwoShare = rows.slice(0, 2).reduce((sum, row) => sum + row.share, 0);
  document.getElementById("concentration-insight").innerHTML = `<b>${formatPercent(topTwoShare, 2)}</b> ของต้นทุนอยู่ในสองระบบแรก — ตู้จ่ายเหมาะกับ standardization; ถังต้องใช้ high-consequence/HSE route`;
}

function renderWorkTypeChart(data) {
  const rows = data.workTypeComparison;
  const types = [...new Set(rows.map((row) => row.work_type))];
  const width = 650;
  const height = 310;
  const margin = { top: 38, right: 18, bottom: 62, left: 56 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const maxValue = Math.max(...rows.map((row) => row.cost)) * 1.12;
  const y = (value) => margin.top + innerH - (value / maxValue) * innerH;
  const groupW = innerW / types.length;
  const barW = 72;
  let content = "";

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = (maxValue / 4) * tick;
    const yy = y(value);
    content += `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${yy}" y2="${yy}" />`;
    content += `<text x="${margin.left - 7}" y="${yy + 4}" text-anchor="end">${(value / 1_000_000).toFixed(1)}</text>`;
  }

  types.forEach((type, index) => {
    const center = margin.left + groupW * (index + 0.5);
    const base = rows.find((row) => row.work_type === type && row.period === "baseline");
    const current = rows.find((row) => row.work_type === type && row.period === "current");
    [base, current].forEach((row, rowIndex) => {
      const xx = center + (rowIndex === 0 ? -barW - 4 : 4);
      const yy = y(row.cost);
      const klass = rowIndex === 0 ? "bar-baseline" : "bar-current";
      content += `<rect class="${klass}" x="${xx}" y="${yy}" width="${barW}" height="${margin.top + innerH - yy}" rx="4"><title>${type} ${row.period}: ${formatBaht(row.cost)}, ${row.rows} งาน, ${formatBaht(row.average_cost)}/งาน</title></rect>`;
      content += `<text class="value-label" x="${xx + barW / 2}" y="${Math.max(15, yy - 7)}" text-anchor="middle">${(row.cost / 1_000_000).toFixed(2)}</text>`;
    });
    content += `<text class="axis-label" x="${center}" y="${height - 34}" text-anchor="middle">${type}</text>`;
    content += `<text x="${center}" y="${height - 18}" text-anchor="middle">${current.rows} งาน · ${formatBaht(current.average_cost)}/งาน</text>`;
  });
  document.getElementById("worktype-chart").innerHTML = svgFrame(width, height, content, "ค่าใช้จ่าย PM และ CM ช่วง baseline เทียบ current")
    + `<div class="chart-legend"><span class="legend-item"><i class="legend-swatch" style="background:#123452"></i>Baseline</span><span class="legend-item"><i class="legend-swatch" style="background:#007a9e"></i>Current</span></div>`;
}

function renderPareto(data) {
  const rows = data.resolutionPareto.slice(0, 8);
  const width = 960;
  const left = 300;
  const right = 70;
  const top = 16;
  const rowH = 36;
  const height = top + rows.length * rowH + 26;
  const innerW = width - left - right;
  const maxValue = Math.max(...rows.map((row) => row.cost));
  let content = "";
  rows.forEach((row, index) => {
    const yy = top + index * rowH;
    const barWidth = (row.cost / maxValue) * innerW;
    const lineX = left + row.cumulative_share * innerW;
    content += `<text class="axis-label" x="${left - 12}" y="${yy + 18}" text-anchor="end">${escapeHtml(row.category)}</text>`;
    content += `<rect class="pareto-bar" x="${left}" y="${yy + 3}" width="${barWidth}" height="22" rx="3"><title>${escapeHtml(row.category)}: ${formatBaht(row.cost)}</title></rect>`;
    content += `<circle class="pareto-dot" cx="${lineX}" cy="${yy + 14}" r="4"><title>สะสม ${formatPercent(row.cumulative_share)}</title></circle>`;
    if (index > 0) {
      const previous = rows[index - 1];
      const previousX = left + previous.cumulative_share * innerW;
      const previousY = top + (index - 1) * rowH + 14;
      content += `<line class="pareto-line" x1="${previousX}" y1="${previousY}" x2="${lineX}" y2="${yy + 14}" />`;
    }
    content += `<text class="value-label" x="${left + barWidth + 8}" y="${yy + 19}">${(row.cost / 1_000_000).toFixed(2)}M</text>`;
  });
  document.getElementById("pareto-chart").innerHTML = svgFrame(width, height, content, "Pareto ค่าใช้จ่ายตามกลุ่มงานและสัดส่วนสะสม");
}

function displayGateActual(item) {
  if (item.actual === null) return "N/A";
  if (item.unit === "ratio") return formatPercent(item.actual, item.actual < 0.2 ? 2 : 1);
  if (item.unit === "days") return `${decimal.format(item.actual)} วัน`;
  return String(item.actual);
}

function displayGateTarget(item) {
  if (item.target === null) return "ไม่ระบุ";
  const prefix = item.direction === "gte" ? "≥ " : item.direction === "lte" ? "≤ " : "= ";
  if (item.unit === "ratio") return `${prefix}${formatPercent(item.target, 0)}`;
  if (item.unit === "days") return `${prefix}${decimal.format(item.target)} วัน`;
  return `${prefix}${item.target}`;
}

function renderTrust(data) {
  const q = data.quality;
  document.getElementById("trust-score").innerHTML = `<strong>${q.pass_count}/${q.gates.length}</strong><span>gates passed</span>`;
  document.getElementById("gate-list").innerHTML = q.gates.map((item) => {
    let meter = 0;
    if (item.actual !== null) {
      meter = item.unit === "ratio" ? item.actual * 100 : Math.min(100, (item.actual / Math.max(item.actual, item.target || 1)) * 100);
    }
    const stateLabel = item.status === "pass" ? "PASS" : item.status === "fail" ? "FAIL" : "BLOCKED";
    return `<div class="gate-row" data-status="${item.status}">
      <div class="gate-name"><b>${escapeHtml(item.label)}</b><small>${displayGateActual(item)} · Target ${displayGateTarget(item)}</small></div>
      <div class="gate-meter" aria-label="${escapeHtml(item.label)} ${displayGateActual(item)}"><span style="width:${Math.max(0, Math.min(100, meter))}%"></span></div>
      <span class="gate-state">${stateLabel}</span>
    </div>`;
  }).join("");

  const h = data.headline;
  const baselines = [
    { label: "Working PM/CM baseline เดิม", value: h.documented_pm_cm_baseline, note: "ต้องยืนยัน scope/inclusion" },
    { label: "Service baseline ในเอกสารเดิม", value: h.documented_2025_baseline, note: `ต่าง Rev.1 ${formatBaht(h.baseline_difference)}` },
    { label: "Excel Rev.1 · ปี 2025", value: h.annual_2025_cost, note: "Observed from 1,123 records" },
  ];
  document.getElementById("baseline-stack").innerHTML = baselines.map((item) => `
    <div class="baseline-row"><span>${escapeHtml(item.label)}</span><b>${formatMillions(item.value)}</b><small>${escapeHtml(item.note)}</small></div>`).join("");

  document.getElementById("unknown-cost-share").textContent = formatPercent(data.operations.unknown_symptom_cost_share, 2);
  document.getElementById("asset-coverage").textContent = formatPercent(data.operations.asset_coverage, 2);
  const freshness = q.gates.find((item) => item.key === "source_freshness_days");
  document.getElementById("freshness-days").textContent = freshness ? `${money.format(freshness.actual)} วัน` : "N/A";
}

function renderSourceMeta(data) {
  document.getElementById("source-coverage").textContent = `${money.format(data.meta.rows)} rows · ${data.meta.columns} fields`;
  document.getElementById("latest-close").textContent = shortDate(data.meta.latest_close_date);
  document.getElementById("topbar-as-of").textContent = `Review ${shortDate(data.meta.review_date)}`;
}

function renderAll(data) {
  renderSourceMeta(data);
  renderMetrics(data);
  renderMonthlyChart(data);
  renderWaterfall(data);
  renderProblemChart(data);
  renderWorkTypeChart(data);
  renderPareto(data);
  renderTrust(data);
}

function showLoadError(error) {
  const grid = document.getElementById("metric-grid");
  grid.innerHTML = `<article class="metric-card metric-blocked" style="grid-column:1/-1"><div class="metric-label"><span>ไม่สามารถอ่าน aggregate data</span><span class="metric-chip chip-blocked">ERROR</span></div><div class="metric-value text-value">เปิดผ่าน local server หรือ Vercel</div><div class="metric-context">${escapeHtml(error.message)}</div></article>`;
}

async function loadDashboard() {
  const response = await fetch("data/dashboard-data.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status} while loading dashboard-data.json`);
  const data = await response.json();
  state.data = data;
  renderAll(data);
}

document.querySelectorAll("[data-view-button]").forEach((button) => {
  button.addEventListener("click", () => setActiveView(button.dataset.viewButton));
});

document.querySelectorAll("[data-view-jump]").forEach((button) => {
  button.addEventListener("click", () => setActiveView(button.dataset.viewJump));
});

document.querySelectorAll("[data-open-dialog]").forEach((button) => {
  button.addEventListener("click", () => {
    const dialog = document.getElementById(button.dataset.openDialog);
    if (dialog?.showModal) dialog.showModal();
  });
});

loadDashboard().catch((error) => {
  console.error(error);
  showLoadError(error);
});
