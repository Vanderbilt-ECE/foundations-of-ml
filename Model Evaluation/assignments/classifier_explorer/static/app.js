// Classifier Explorer front end.
//
// The server sends, once per fit, the test-set TP/FP/TN/FN counts at every
// threshold on a fixed grid. Everything the slider and cost boxes control is
// recomputed here from those counts, so moving the threshold is instant.

const $ = (id) => document.getElementById(id);

const state = {
  config: null,
  result: null,    // latest /api/fit response
  history: {},     // k -> { degree -> complexity metrics }
  index: 0,        // current position in result.grid.thresholds
  scale: "linear", // slider scale: "linear" or "log"
};

// ---------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function binom(n, r) {
  let out = 1;
  for (let i = 1; i <= r; i++) out = (out * (n - r + i)) / i;
  return Math.round(out);
}

function expandedCount(k, degree) {
  return binom(k + degree, degree) - 1;
}

const fmtInt = (x) => Math.round(x).toLocaleString();
const fmtPct = (x) => (Number.isFinite(x) ? (100 * x).toFixed(1) + "%" : "–");
const fmtNum = (x, d = 3) => (Number.isFinite(x) ? x.toFixed(d) : "–");
const fmtMoney = (x) =>
  Number.isFinite(x) ? (x < 0 ? "−" : "") + Math.abs(x).toLocaleString(undefined, { maximumFractionDigits: 0 }) : "–";

function fmtThreshold(t) {
  if (t === 0) return "0";
  if (t >= 0.001) return t.toFixed(3);
  return t.toExponential(1);
}

/** Index of the grid threshold nearest to t (thresholds are sorted). */
function nearestIndex(thresholds, t) {
  let lo = 0, hi = thresholds.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (thresholds[mid] < t) lo = mid + 1; else hi = mid;
  }
  if (lo > 0 && Math.abs(thresholds[lo - 1] - t) <= Math.abs(thresholds[lo] - t)) return lo - 1;
  return lo;
}

function setStatus(text, kind = "") {
  const el = $("status");
  el.textContent = text;
  el.className = "status" + (kind ? " " + kind : "");
}

// ---------------------------------------------------------------------
// Costs and per-threshold metrics
// ---------------------------------------------------------------------

function readCosts() {
  const value = (id) => {
    const v = parseFloat($(id).value);
    return Number.isFinite(v) ? v : 0;
  };
  return { tp: value("cost-tp"), fp: value("cost-fp"), tn: value("cost-tn"), fn: value("cost-fn") };
}

/** Total cost on the test set at every grid threshold. */
function costCurve(grid, c) {
  return grid.thresholds.map((_, i) =>
    c.tp * grid.tp[i] + c.fp * grid.fp[i] + c.tn * grid.tn[i] + c.fn * grid.fn[i]);
}

function argmin(values) {
  let best = 0;
  for (let i = 1; i < values.length; i++) if (values[i] < values[best]) best = i;
  return best;
}

function metricsAt(grid, i) {
  const tp = grid.tp[i], fp = grid.fp[i], tn = grid.tn[i], fn = grid.fn[i];
  const precision = tp + fp > 0 ? tp / (tp + fp) : NaN;
  const recall = tp / (tp + fn);
  return {
    tp, fp, tn, fn,
    precision,
    recall,
    fpr: fp / (fp + tn),
    specificity: tn / (fp + tn),
    accuracy: (tp + tn) / (tp + fp + tn + fn),
    f1: precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : NaN,
    flagged: tp + fp,
  };
}

// ---------------------------------------------------------------------
// Slider: linear 0..1 in steps of 0.001, or log10 from -6 to 0 in steps of 0.01.
// Both land exactly on thresholds in the server's grid.
// ---------------------------------------------------------------------

function configureSlider() {
  const s = $("threshold");
  if (state.scale === "linear") { s.min = 0; s.max = 1000; s.step = 1; }
  else { s.min = -600; s.max = 0; s.step = 1; }
}

function sliderToThreshold(v) {
  return state.scale === "linear" ? v / 1000 : Math.pow(10, v / 100);
}

function thresholdToSlider(t) {
  if (state.scale === "linear") return Math.round(t * 1000);
  return t <= 0 ? -600 : Math.max(-600, Math.min(0, Math.round(100 * Math.log10(t))));
}

function syncSliderToIndex() {
  const t = state.result.grid.thresholds[state.index];
  $("threshold").value = thresholdToSlider(t);
}

// ---------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------

function baseLayout(extra = {}) {
  const ink = css("--text-secondary");
  const axis = (title, more = {}) => ({
    title: { text: title, font: { size: 12, color: ink } },
    gridcolor: css("--grid"),
    linecolor: css("--axis"),
    zerolinecolor: css("--axis"),
    tickfont: { size: 11, color: css("--text-muted") },
    ...more,
  });
  return {
    paper_bgcolor: css("--surface"),
    plot_bgcolor: css("--surface"),
    font: { family: "system-ui, -apple-system, Segoe UI, sans-serif", color: css("--text-primary") },
    margin: { l: 58, r: 16, t: 12, b: 48 },
    showlegend: false,
    hoverlabel: { bgcolor: css("--surface"), bordercolor: css("--axis"), font: { color: css("--text-primary") } },
    legend: { orientation: "h", y: 1.12, x: 0, font: { size: 12, color: ink } },
    ...extra,
    xaxis: axis(extra.xTitle || "", extra.xaxis || {}),
    yaxis: axis(extra.yTitle || "", extra.yaxis || {}),
  };
}

const plotConfig = { displayModeBar: false, responsive: true };

/** A marker for the current operating point, with a surface-colored ring. */
function pointMarker(color) {
  return { size: 12, color, line: { color: css("--surface"), width: 2 } };
}

function renderConfusionMatrix(m) {
  const cell = (id, tag, count, rowTotal, costPer) => {
    const share = rowTotal > 0 ? count / rowTotal : 0;
    const el = $(id);
    el.style.background = `color-mix(in oklab, var(--seq-1) ${Math.round(share * 100)}%, var(--seq-0))`;
    el.style.color = share > 0.7 ? "#ffffff" : "var(--text-primary)";
    el.innerHTML =
      `<span class="tag">${tag}</span>` +
      `<span class="count">${fmtInt(count)}</span>` +
      `<span class="pct">${fmtPct(share)} of row · cost ${fmtMoney(count * costPer)}</span>`;
  };
  const c = readCosts();
  cell("cm-tn", "TN", m.tn, m.tn + m.fp, c.tn);
  cell("cm-fp", "FP", m.fp, m.tn + m.fp, c.fp);
  cell("cm-fn", "FN", m.fn, m.fn + m.tp, c.fn);
  cell("cm-tp", "TP", m.tp, m.fn + m.tp, c.tp);

  const rows = [
    ["Precision", fmtNum(m.precision)],
    ["Recall (TPR)", fmtNum(m.recall)],
    ["F1", fmtNum(m.f1)],
    ["FPR", fmtNum(m.fpr, 4)],
    ["Specificity", fmtNum(m.specificity, 4)],
    ["Accuracy", fmtNum(m.accuracy, 4)],
    ["Flagged", fmtInt(m.flagged)],
  ];
  $("metrics").innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
}

function renderCost(grid, cost, best, flagNothing) {
  const log = state.scale === "log";
  const keep = grid.thresholds.map((t) => !log || t > 0);
  const xs = grid.thresholds.filter((_, i) => keep[i]);
  const ys = cost.filter((_, i) => keep[i]);
  const i = state.index;
  const tNow = grid.thresholds[i];

  const traces = [
    {
      x: xs, y: ys, mode: "lines", name: "Total cost",
      line: { color: css("--series-1"), width: 2 },
      hovertemplate: "threshold %{x:.4g}<br>cost %{y:,.0f}<extra></extra>",
    },
    {
      x: [grid.thresholds[best]], y: [cost[best]], mode: "markers+text", name: "Minimum",
      marker: { ...pointMarker(css("--min-mark")), symbol: "diamond" },
      text: ["min"], textposition: "top center", textfont: { color: css("--text-secondary"), size: 12 },
      hovertemplate: "minimum cost %{y:,.0f}<br>at threshold %{x:.4g}<extra></extra>",
    },
  ];
  if (!log || tNow > 0) {
    traces.push({
      x: [tNow], y: [cost[i]], mode: "markers", name: "Current",
      marker: pointMarker(css("--text-primary")),
      hovertemplate: "current threshold %{x:.4g}<br>cost %{y:,.0f}<extra></extra>",
    });
  }
  // Flagging (almost) everything is so expensive that it would flatten the
  // rest of the curve, so the y-axis stops a little above "flag nothing".
  const top = Math.max(flagNothing, cost[i], cost[best]);
  const bottom = Math.min(0, cost[best]);
  const pad = 0.15 * (top - bottom || 1);
  Plotly.react("cost-chart", traces, baseLayout({
    xTitle: "Threshold (flag as fraud when P ≥ threshold)",
    yTitle: "Total cost on test set",
    xaxis: log ? { type: "log", exponentformat: "power" } : { range: [0, 1] },
    yaxis: { range: [bottom - pad, top + pad] },
    hovermode: "closest",
  }), plotConfig);
}

function renderRoc(result, m) {
  $("roc-title").textContent = `ROC curve · AUC = ${result.roc_auc.toFixed(4)}`;
  const logX = $("roc-log").checked;
  const diag = logX ? [1e-5, 1] : [0, 1];
  Plotly.react("roc-chart", [
    {
      x: diag, y: diag, mode: "lines", name: "Random guessing",
      line: { color: css("--text-muted"), width: 1.5, dash: "dot" }, hoverinfo: "skip",
    },
    {
      x: result.roc.fpr, y: result.roc.tpr, mode: "lines", name: "Model",
      line: { color: css("--series-1"), width: 2 },
      hovertemplate: "FPR %{x:.4f}<br>TPR %{y:.3f}<extra></extra>",
    },
    {
      x: [m.fpr], y: [m.recall], mode: "markers", name: "Current threshold",
      marker: pointMarker(css("--text-primary")),
      hovertemplate: "current threshold<br>FPR %{x:.4f}<br>TPR %{y:.3f}<extra></extra>",
    },
  ], baseLayout({
    xTitle: "False positive rate" + (logX ? " (log scale)" : ""), yTitle: "True positive rate (recall)",
    xaxis: logX ? { type: "log", range: [-5, 0], exponentformat: "power" } : { range: [0, 1] }, yaxis: { range: [0, 1.02] }, hovermode: "closest",
  }), plotConfig);
}

function renderPr(result, m) {
  $("pr-title").textContent =
    `Precision–recall curve · AP = ${result.average_precision.toFixed(4)}`;
  const base = result.prevalence_test;
  const traces = [
    {
      x: [0, 1], y: [base, base], mode: "lines", name: "Random guessing",
      line: { color: css("--text-muted"), width: 1.5, dash: "dot" }, hoverinfo: "skip",
    },
    {
      x: result.pr.recall, y: result.pr.precision, mode: "lines", name: "Model",
      line: { color: css("--series-1"), width: 2 },
      hovertemplate: "recall %{x:.3f}<br>precision %{y:.3f}<extra></extra>",
    },
  ];
  if (Number.isFinite(m.precision)) {
    traces.push({
      x: [m.recall], y: [m.precision], mode: "markers", name: "Current threshold",
      marker: pointMarker(css("--text-primary")),
      hovertemplate: "current threshold<br>recall %{x:.3f}<br>precision %{y:.3f}<extra></extra>",
    });
  }
  Plotly.react("pr-chart", traces, baseLayout({
    xTitle: "Recall", yTitle: "Precision",
    xaxis: { range: [0, 1.02] }, yaxis: { range: [0, 1.05] }, hovermode: "closest",
    annotations: [{
      x: 0.01, y: base, xanchor: "left", yanchor: "bottom", showarrow: false,
      text: `baseline = fraud rate ${(100 * base).toFixed(2)}%`,
      font: { size: 11, color: css("--text-muted") },
    }],
  }), plotConfig);
}

function renderComplexity() {
  const k = parseInt($("k").value, 10);
  const byDegree = state.history[k] || {};
  const degrees = Object.keys(byDegree).map(Number).sort((a, b) => a - b);
  $("complexity-k").textContent = `(k = ${k} features; ${degrees.length} degree${degrees.length === 1 ? "" : "s"} fitted)`;

  const current = state.result && state.result.k === k ? state.result.degree : null;
  const chart = (el, trainKey, testKey, yTitle) => {
    const series = (key, name, color) => ({
      x: degrees, y: degrees.map((d) => byDegree[d][key]), name,
      mode: "lines+markers+text",
      line: { color, width: 2 },
      marker: { size: 9, color, line: { color: css("--surface"), width: 2 } },
      // Direct label on the last point only.
      text: degrees.map((_, j) => (j === degrees.length - 1 ? name : "")),
      textposition: "middle right",
      textfont: { color: css("--text-secondary"), size: 12 },
      hovertemplate: `${name}: %{y:.4f}<extra></extra>`,
    });
    const shapes = current ? [{
      type: "line", x0: current, x1: current, y0: 0, y1: 1, yref: "paper",
      line: { color: css("--axis"), width: 1.5, dash: "dot" },
    }] : [];
    Plotly.react(el, [
      series(trainKey, "Train", css("--series-2")),
      series(testKey, "Test", css("--series-1")),
    ], baseLayout({
      xTitle: "Polynomial degree", yTitle,
      xaxis: { dtick: 1, range: [0.6, state.config.max_degree + 0.9] },
      showlegend: true, hovermode: "x unified", shapes,
      margin: { l: 64, r: 16, t: 36, b: 48 },
    }), plotConfig);
  };
  chart("ap-chart", "train_ap", "test_ap", "PR-AUC (average precision) ↑");
  chart("logloss-chart", "train_logloss", "test_logloss", "Log-loss ↓");
}

/** Redraw everything that depends on the threshold or costs. */
function renderThresholdViews() {
  const r = state.result;
  if (!r) return;
  const grid = r.grid;
  const c = readCosts();
  const cost = costCurve(grid, c);
  const best = argmin(cost);
  const m = metricsAt(grid, state.index);

  $("threshold-value").textContent = fmtThreshold(grid.thresholds[state.index]);
  $("min-threshold").textContent = fmtThreshold(grid.thresholds[best]);

  const P = r.n_test_fraud, N = r.n_test - r.n_test_fraud;
  const flagNothing = c.fn * P + c.tn * N;
  const flagAll = c.tp * P + c.fp * N;
  $("min-cost-detail").innerHTML =
    `Minimum cost <strong>${fmtMoney(cost[best])}</strong> vs current ${fmtMoney(cost[state.index])}.<br>` +
    `Flag nothing: ${fmtMoney(flagNothing)} · flag everything: ${fmtMoney(flagAll)}`;

  renderConfusionMatrix(m);
  renderCost(grid, cost, best, flagNothing);
  renderRoc(r, m);
  renderPr(r, m);
}

let frame = null;
function scheduleRender() {
  if (frame) return;
  frame = requestAnimationFrame(() => { frame = null; renderThresholdViews(); });
}

// ---------------------------------------------------------------------
// Server calls
// ---------------------------------------------------------------------

async function post(url, body) {
  const res = await fetch(url, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function recordComplexity(k, degree, metrics) {
  (state.history[k] ||= {})[degree] = metrics;
}

function setBusy(busy) {
  $("fit-btn").disabled = busy;
  $("sweep-btn").disabled = busy;
  if (!busy) updateExpandedReadout();
}

async function fit() {
  const degree = parseInt($("degree").value, 10);
  const k = parseInt($("k").value, 10);
  const previousT = state.result ? state.result.grid.thresholds[state.index] : 0.5;
  setBusy(true);
  setStatus(`Fitting degree ${degree} with ${k} features…`);
  try {
    const r = await post("/api/fit", { degree, k });
    state.result = r;
    state.index = nearestIndex(r.grid.thresholds, previousT);
    syncSliderToIndex();
    recordComplexity(k, degree, r.complexity);
    const warn = r.warnings.length ? ` Warning: ${r.warnings.join(" ")}` : "";
    setStatus(
      `Fitted degree ${degree} on ${k} features → ${fmtInt(r.n_features_expanded)} model inputs ` +
      `in ${r.fit_seconds.toFixed(2)} s. Test AUC ${r.roc_auc.toFixed(4)}, AP ${r.average_precision.toFixed(4)}. ` +
      `Features: ${r.features_used.join(", ")}.${warn}`,
      warn ? "warn" : "");
    renderThresholdViews();
    renderComplexity();
  } catch (err) {
    setStatus(err.message, "error");
  } finally {
    setBusy(false);
  }
}

async function sweep() {
  const k = parseInt($("k").value, 10);
  setBusy(true);
  setStatus(`Fitting every degree for k = ${k} (this can take several seconds)…`);
  try {
    const r = await post("/api/sweep", { k });
    r.points.forEach((p) => recordComplexity(k, p.degree, p));
    const skipped = r.skipped.length
      ? ` Skipped degree ${r.skipped.join(", ")} (too many polynomial columns for k = ${k}).` : "";
    setStatus(`Sweep done for k = ${k}: fitted degree ${r.points.map((p) => p.degree).join(", ")}.${skipped}`);
    renderComplexity();
  } catch (err) {
    setStatus(err.message, "error");
  } finally {
    setBusy(false);
  }
}

function updateExpandedReadout() {
  const degree = parseInt($("degree").value, 10);
  const k = parseInt($("k").value, 10);
  const el = $("expanded-readout");
  if (!Number.isFinite(k) || k < state.config.min_k || k > state.config.max_k) {
    el.textContent = `k must be ${state.config.min_k}–${state.config.max_k}`;
    el.classList.add("over");
    $("fit-btn").disabled = true;
    return;
  }
  const n = expandedCount(k, degree);
  const over = n > state.config.max_expanded_features;
  el.textContent = `→ ${fmtInt(n)} polynomial columns` + (over ? ` (limit ${fmtInt(state.config.max_expanded_features)})` : "");
  el.classList.toggle("over", over);
  $("fit-btn").disabled = over;
}

// ---------------------------------------------------------------------
// Wiring
// ---------------------------------------------------------------------

async function init() {
  const cfg = await (await fetch("/api/config")).json();
  state.config = cfg;

  const degreeSelect = $("degree");
  for (let d = 1; d <= cfg.max_degree; d++) degreeSelect.add(new Option(String(d), String(d)));
  const k = $("k");
  k.min = cfg.min_k; k.max = cfg.max_k; k.value = cfg.default_k;
  k.title = "Features ranked by |correlation| with fraud (training data): " + cfg.ranked_features.join(", ");

  $("data-summary").textContent =
    `Training on ${fmtInt(cfg.n_fit)} rows: all ${fmtInt(cfg.n_train_fraud)} training frauds plus ` +
    `${(100 * cfg.sampling_rate).toFixed(1)}% of the ${fmtInt(cfg.n_train_legit_total)} training non-frauds. ` +
    `The intercept is corrected by log(${cfg.sampling_rate.toFixed(3)}) so probabilities match the real fraud rate.`;

  configureSlider();
  $("threshold").value = thresholdToSlider(0.5);

  degreeSelect.addEventListener("change", updateExpandedReadout);
  k.addEventListener("input", () => { updateExpandedReadout(); renderComplexityIfReady(); });
  $("fit-btn").addEventListener("click", fit);
  $("sweep-btn").addEventListener("click", sweep);

  $("threshold").addEventListener("input", (e) => {
    if (!state.result) return;
    const t = sliderToThreshold(parseFloat(e.target.value));
    state.index = nearestIndex(state.result.grid.thresholds, t);
    scheduleRender();
  });
  document.querySelectorAll('input[name="scale"]').forEach((radio) =>
    radio.addEventListener("change", (e) => {
      state.scale = e.target.value;
      configureSlider();
      if (state.result) {
        // Keep the current threshold, snapped to a point the new slider can reach.
        const t = sliderToThreshold(thresholdToSlider(state.result.grid.thresholds[state.index]));
        state.index = nearestIndex(state.result.grid.thresholds, t);
        syncSliderToIndex();
        renderThresholdViews();
      }
    }));
  $("roc-log").addEventListener("change", scheduleRender);
  ["cost-tp", "cost-fp", "cost-tn", "cost-fn"].forEach((id) => $(id).addEventListener("input", scheduleRender));
  $("jump-btn").addEventListener("click", () => {
    if (!state.result) return;
    state.index = argmin(costCurve(state.result.grid, readCosts()));
    syncSliderToIndex();
    renderThresholdViews();
  });

  // Redraw charts with the right colors when the OS theme changes.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    renderThresholdViews();
    renderComplexityIfReady();
  });

  updateExpandedReadout();
  await fit();
}

function renderComplexityIfReady() {
  if (state.config) renderComplexity();
}

init().catch((err) => setStatus("Could not reach the server: " + err.message, "error"));
