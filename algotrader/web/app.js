// AlgoTrader web app. Vanilla JS, no build step. One state object per view.
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) k.startsWith("on") ? el.addEventListener(k.slice(2), v) : v != null && el.setAttribute(k, v);
  el.append(...kids.flat().filter((k) => k != null));
  return el;
};
const inr = (n, d = 0) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: d });
const pct = (n) => (n > 0 ? "+" : "") + Number(n).toFixed(2) + "%";
const cls = (n) => (n > 0 ? "up" : n < 0 ? "down" : "");
const when = (iso) => (iso.endsWith("00:00:00") ? iso.slice(0, 10) : iso.slice(0, 16));
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

async function api(path, opts = {}) {
  const res = await fetch(path, opts.body && !(opts.body instanceof FormData)
    ? { ...opts, headers: { "content-type": "application/json" }, body: JSON.stringify(opts.body) } : opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg || `Request failed (${res.status})`);
  return data;
}
function toast(msg, err = false) {
  const t = $("#toast");
  t.textContent = msg; t.className = "toast show" + (err ? " err" : "");
  clearTimeout(toast.t); toast.t = setTimeout(() => (t.className = "toast"), err ? 6000 : 2800);
}

/* ---------- router ---------- */
function route() {
  const v = (location.hash || "#lab").slice(1);
  $$(".view").forEach((s) => (s.hidden = s.id !== "view-" + v));
  $$(".rail nav a").forEach((a) => a.classList.toggle("on", a.dataset.view === v));
  ({ portfolio: loadPortfolio, data: loadData, replay: loadAccounts })[v]?.()?.catch?.((e) => toast(e.message, true));
}
addEventListener("hashchange", route);

/* ---------- charts ---------- */
function chart(el, opts = {}) {
  el.replaceChildren();
  return LightweightCharts.createChart(el, {
    autoSize: true,
    layout: { background: { color: "transparent" }, textColor: css("--ink3"), fontFamily: "Geist Mono" },
    grid: { vertLines: { color: css("--line") }, horzLines: { color: css("--line") } },
    rightPriceScale: { borderColor: css("--line2") },
    timeScale: { borderColor: css("--line2"), timeVisible: opts.intraday, secondsVisible: false },
    crosshair: { mode: 0 },
  });
}
const candleStyle = () => ({ upColor: css("--up"), downColor: css("--down"), borderVisible: false, wickUpColor: css("--up"), wickDownColor: css("--down") });

/* ---------- LAB ---------- */
const OPS = [["<", "below"], [">", "above"], ["<=", "≤"], [">=", "≥"], ["crosses_above", "crosses above"], ["crosses_below", "crosses below"]];
const TERMS = ["close", "open", "high", "low", "sma(50)", "sma(200)", "ema(20)", "rsi(14)", "bb_upper(20,2)", "bb_lower(20,2)", "bb_mid(20,2)",
  "macd(12,26,9)", "macd_signal(12,26,9)", "atr(14)", "highest(20)", "lowest(10)", "pct_change(1)", "gap_pct", "supertrend(10,3)"];
const lab = { s: null, datasets: [], chat: [], result: null };

const blank = () => ({ name: "My strategy", symbol: "NIFTY", timeframe: "1D", start: "2016-01-01", end: null, direction: "long",
  entry: [{ left: "rsi(14)", op: "<", right: 30 }], entry_logic: "all", exit: [{ left: "rsi(14)", op: ">", right: 60 }], exit_logic: "any",
  stop_loss_pct: null, take_profit_pct: null, max_bars: null, intraday_exit: null, capital: 100000, position_pct: 100,
  segment: "equity_delivery", slippage_pct: 0.05, kind: "rules" });

async function initLab() {
  $("#terms").append(...TERMS.map((t) => h("option", { value: t })));
  const [presets, datasets] = await Promise.all([api("/api/presets"), api("/api/datasets")]);
  lab.datasets = datasets;
  $("#presets").append(...presets.map((p, i) => h("button", { class: "preset", type: "button", style: `animation-delay:${i * 40}ms`, onclick: () => usePreset(p) },
    h("span", { class: "t" }, p.name), h("span", { class: "d" }, p.description),
    h("span", { class: "tags" }, h("span", { class: "tag" }, p.symbol), h("span", { class: "tag" }, p.timeframe), h("span", { class: "tag" }, p.direction)))));
  fillSymbols($("#f-symbol")); fillSymbols($("#r-symbol"));
  setStrategy(blank());
}
function fillSymbols(sel) {
  sel.replaceChildren(...lab.datasets.map((d) => h("option", { value: d.symbol }, d.symbol)));
}
function usePreset(p) {
  setStrategy(structuredClone(p));
  toast(`Loaded “${p.name}”. Running…`);
  runBacktest();
}
function setStrategy(s) {
  lab.s = { ...blank(), ...s };
  const S = lab.s;
  $("#f-name").value = S.name;
  if (!lab.datasets.some((d) => d.symbol === S.symbol)) $("#f-symbol").append(h("option", { value: S.symbol }, S.symbol));
  $("#f-symbol").value = S.symbol;
  syncTimeframes();
  $("#f-timeframe").value = S.timeframe;
  $("#f-start").value = S.start || ""; $("#f-end").value = S.end || "";
  $("#f-direction").value = S.direction; $("#f-segment").value = S.segment;
  $("#f-entry-logic").value = S.entry_logic; $("#f-exit-logic").value = S.exit_logic;
  $("#f-sl").value = S.stop_loss_pct ?? ""; $("#f-tp").value = S.take_profit_pct ?? ""; $("#f-maxbars").value = S.max_bars ?? "";
  $("#f-capital").value = S.capital; $("#f-pct").value = S.position_pct; $("#f-slip").value = S.slippage_pct;
  $("#f-sq").value = S.intraday_exit || "";
  renderConds("entry"); renderConds("exit"); toggleSq();
}
function syncTimeframes() {
  const ds = lab.datasets.find((d) => d.symbol === $("#f-symbol").value);
  const tfs = ds?.timeframes || ["1D", "1W"];
  const cur = lab.s?.timeframe || $("#f-timeframe").value;
  $("#f-timeframe").replaceChildren(...tfs.map((t) => h("option", { value: t }, t)));
  $("#f-timeframe").value = tfs.includes(cur) ? cur : tfs.includes("1D") ? "1D" : tfs[0];
}
const toggleSq = () => ($("#sq-wrap").hidden = ["1D", "1W"].includes($("#f-timeframe").value));
function renderConds(which) {
  $(`#${which}-rows`).replaceChildren(...lab.s[which].map((c, i) => {
    const op = h("select", { "aria-label": "operator", onchange: (e) => (c.op = e.target.value) }, OPS.map(([v, t]) => h("option", { value: v }, t)));
    op.value = c.op;
    return h("div", { class: "cond" },
      h("input", { list: "terms", value: c.left, "aria-label": "left term", oninput: (e) => (c.left = e.target.value) }), op,
      h("input", { list: "terms", value: c.right, "aria-label": "right term", oninput: (e) => (c.right = e.target.value) }),
      h("button", { class: "x", type: "button", title: "Remove", onclick: () => { lab.s[which].splice(i, 1); renderConds(which); } }, "×"));
  }));
}
function readForm() {
  const num = (id) => ($(id).value === "" ? null : Number($(id).value));
  Object.assign(lab.s, {
    name: $("#f-name").value || "My strategy", symbol: $("#f-symbol").value, timeframe: $("#f-timeframe").value,
    start: $("#f-start").value || null, end: $("#f-end").value || null, direction: $("#f-direction").value, segment: $("#f-segment").value,
    entry_logic: $("#f-entry-logic").value, exit_logic: $("#f-exit-logic").value, stop_loss_pct: num("#f-sl"), take_profit_pct: num("#f-tp"),
    max_bars: num("#f-maxbars"), capital: num("#f-capital") || 100000, position_pct: num("#f-pct") || 100, slippage_pct: num("#f-slip") ?? 0.05,
    intraday_exit: $("#sq-wrap").hidden ? null : $("#f-sq").value || null,
  });
  for (const k of ["entry", "exit"]) lab.s[k] = lab.s[k].filter((c) => String(c.left).trim() && String(c.right).trim())
    .map((c) => ({ ...c, right: isNaN(Number(c.right)) ? c.right : Number(c.right) }));
  return lab.s;
}

async function runBacktest() {
  const s = readForm();
  const box = $("#results");
  box.classList.add("loading");
  try {
    const r = await api("/api/backtest", { method: "POST", body: s });
    lab.result = r;
    renderResult(r);
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) { toast(e.message, true); } finally { box.classList.remove("loading"); }
}

function renderResult(r) {
  const m = r.metrics, s = r.strategy;
  const metric = (k, v, sub, c = "", i = 0) => h("div", { class: "metric", style: `animation-delay:${i * 50}ms` }, h("div", { class: "k" }, k), h("div", { class: "v " + c }, v), sub && h("div", { class: "s" }, sub));
  const box = $("#results");
  box.replaceChildren(
    h("div", { class: "res-head" }, h("h3", {}, s.name), h("span", { class: "muted" }, `${s.symbol} · ${s.timeframe} · ${m.start} → ${m.end} · charges as of ${m.rates_as_of}`)),
    h("div", { class: "metrics" },
      metric("CAGR after costs", pct(m.cagr_pct), `before costs ${pct(m.cagr_before_costs_pct)}`, cls(m.cagr_pct), 0),
      metric(`vs holding ${s.symbol}`, pct(m.cagr_pct - m.benchmark_cagr_pct), `${s.symbol} did ${pct(m.benchmark_cagr_pct)}/yr`, cls(m.cagr_pct - m.benchmark_cagr_pct), 1),
      metric("Max drawdown", pct(m.max_drawdown_pct), `${m.drawdown_from} → ${m.drawdown_to}`, "down", 2),
      metric("Win rate", m.win_rate_pct + "%", `${m.trades} trades · PF ${m.profit_factor ?? "–"}`, "", 3),
      metric("Final equity", inr(m.final_equity), `from ${inr(s.capital)} · Sharpe ${m.sharpe}`, cls(m.total_return_pct), 4),
      metric("Charges + slippage", inr(m.costs), `in market ${m.exposure_pct}% of time`, "", 5)),
    h("div", { class: "tabs" }, ["Price & trades", "Equity", "Drawdown"].map((t, i) => h("button", { type: "button", class: i ? "" : "on", onclick: (e) => { $$(".tabs button", box).forEach((b) => b.classList.toggle("on", b === e.target)); drawTab(i); } }, t))),
    h("div", { id: "res-chart", class: "chart" }),
    h("div", { class: "coach" }, h("h4", {}, "What this is telling you"), h("ul", {}, r.insights.map((t) => h("li", {}, t)))),
    h("div", { class: "res-actions" },
      h("button", { class: "btn primary", type: "button", onclick: () => { location.hash = "#replay"; $("#r-symbol").value = s.symbol; toast("Pick a date and practise this strategy by hand."); } }, "Practise it in Replay →"),
      h("button", { class: "btn", type: "button", onclick: () => askBot(`My backtest result: CAGR ${m.cagr_pct}% vs ${s.symbol} ${m.benchmark_cagr_pct}%, max drawdown ${m.max_drawdown_pct}%, ${m.trades} trades, win rate ${m.win_rate_pct}%. Suggest one change to test next and update the strategy.`) }, "Ask the assistant how to improve it"),
      h("button", { class: "btn", type: "button", onclick: () => download(r) }, "Download trades CSV")),
    h("h2", {}, `Trades (${r.trades.length})`),
    h("div", { class: "table-wrap" }, h("table", { class: "table" },
      h("thead", {}, h("tr", {}, ["Entry", "Exit", "Side", "Qty", "Entry ₹", "Exit ₹", "P&L", "Return", "Charges", "Why exit"].map((t) => h("th", {}, t)))),
      h("tbody", {}, r.trades.slice().reverse().map((t) => h("tr", {},
        h("td", {}, when(t.entry_time)), h("td", {}, when(t.exit_time || "")), h("td", {}, t.side), h("td", {}, t.qty),
        h("td", {}, t.entry_price), h("td", {}, t.exit_price), h("td", { class: cls(t.pnl) }, inr(t.pnl)), h("td", { class: cls(t.return_pct) }, pct(t.return_pct)),
        h("td", {}, inr(t.charges)), h("td", {}, t.reason)))))));
  drawTab(0);
}

async function drawTab(i) {
  const r = lab.result, s = r.strategy, el = $("#res-chart");
  const c = chart(el, { intraday: !["1D", "1W"].includes(s.timeframe) });
  if (i === 0) {
    const candles = await api(`/api/candles?symbol=${encodeURIComponent(s.symbol)}&timeframe=${s.timeframe}&start=${r.metrics.start}&end=${r.metrics.end}&limit=50000`);
    const cs = c.addCandlestickSeries(candleStyle());
    cs.setData(candles);
    const palette = ["#ff9a3c", "#7aa2ff", "#d58bff", "#5fd4d0"];
    Object.entries(r.overlays || {}).forEach(([k, pts], j) => c.addLineSeries({ color: palette[j % 4], lineWidth: 1.5, title: k, priceLineVisible: false, lastValueVisible: false }).setData(pts));
    const ts = (iso) => Math.floor(new Date(iso.replace(" ", "T") + "Z").getTime() / 1000);
    const long = s.direction === "long";
    cs.setMarkers(r.trades.flatMap((t) => [
      { time: ts(t.entry_time), position: long ? "belowBar" : "aboveBar", color: css("--saffron"), shape: long ? "arrowUp" : "arrowDown", text: long ? "B" : "S" },
      t.exit_time && { time: ts(t.exit_time), position: long ? "aboveBar" : "belowBar", color: t.pnl > 0 ? css("--up") : css("--down"), shape: "circle", text: t.pnl > 0 ? "✓" : "✗" },
    ]).filter(Boolean).sort((a, b) => a.time - b.time));
  } else if (i === 1) {
    c.addAreaSeries({ lineColor: css("--saffron"), topColor: "rgba(255,154,60,.28)", bottomColor: "rgba(255,154,60,0)", lineWidth: 2, title: "Strategy" }).setData(r.equity);
    c.addLineSeries({ color: css("--ink3"), lineWidth: 1, lineStyle: 2, title: `Hold ${s.symbol}` }).setData(r.benchmark);
  } else {
    c.addAreaSeries({ lineColor: css("--down"), topColor: "rgba(255,107,94,0)", bottomColor: "rgba(255,107,94,.3)", lineWidth: 1.5, invertFilledArea: true }).setData(r.drawdown);
  }
  c.timeScale().fitContent();
}
function download(r) {
  const cols = ["entry_time", "exit_time", "side", "qty", "entry_price", "exit_price", "pnl", "return_pct", "charges", "reason"];
  const csv = [cols.join(","), ...r.trades.map((t) => cols.map((k) => t[k]).join(","))].join("\n");
  const a = h("a", { href: URL.createObjectURL(new Blob([csv], { type: "text/csv" })), download: `${r.strategy.name.replace(/\W+/g, "_")}_trades.csv` });
  a.click(); URL.revokeObjectURL(a.href);
}

/* chat */
function bubble(role, text, extra = "") {
  const t = $("#thread"); t.hidden = false;
  const b = h("div", { class: `msg ${role} ${extra}` }, text);
  t.append(b); b.scrollIntoView({ block: "nearest", behavior: "smooth" });
  return b;
}
async function askBot(text) {
  lab.chat.push({ role: "user", content: text });
  bubble("user", text);
  const wait = bubble("bot", "Thinking", "typing");
  try {
    const out = await api("/api/chat", { method: "POST", body: { messages: lab.chat, strategy: readForm() } });
    wait.remove();
    lab.chat.push({ role: "assistant", content: out.reply });
    bubble("bot", out.reply);
    setStrategy(out.strategy);
    if (out.ready_to_run) runBacktest();
  } catch (e) {
    wait.remove(); lab.chat.pop();
    bubble("bot", e.message + "\nYou can still pick a classic below or edit the rules by hand.", "err");
  }
}

$("#ask").addEventListener("submit", (e) => { e.preventDefault(); const v = $("#ask-input").value.trim(); if (v) { $("#ask-input").value = ""; askBot(v); } });
$("#builder").addEventListener("submit", (e) => { e.preventDefault(); runBacktest(); });
$$("[data-add]").forEach((b) => b.addEventListener("click", () => { lab.s[b.dataset.add].push({ left: "close", op: ">", right: "sma(20)" }); renderConds(b.dataset.add); }));
$("#f-symbol").addEventListener("change", () => { lab.s.symbol = $("#f-symbol").value; syncTimeframes(); toggleSq(); });
$("#f-timeframe").addEventListener("change", () => { lab.s.timeframe = $("#f-timeframe").value; toggleSq(); });
addEventListener("keydown", (e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && !$("#view-lab").hidden) runBacktest(); });

/* ---------- REPLAY ---------- */
const rp = { bars: [], i: 0, pos: null, timer: null, series: null, account: null, markers: [], sessions: {} };

async function loadAccounts(selectId) {
  const list = await api("/api/paper/accounts");
  if (!list.length) list.push(await api("/api/paper/accounts", { method: "POST", body: { name: "Starter account", capital: 100000, max_loss_pct: 20 } }));
  $("#r-account").replaceChildren(...list.map((a) => h("option", { value: a.id }, `${a.name}${a.status === "blown" ? " (blown)" : ""}`)));
  $("#r-account").value = selectId || rp.account?.id || list[0].id;
  return showAccount();
}
async function showAccount() {
  const a = (rp.account = await api(`/api/paper/accounts/${$("#r-account").value}`));
  const left = Math.max(0, Math.min(100, ((a.cash - a.loss_limit) / (a.capital - a.loss_limit)) * 100));
  $("#r-account-card").className = "acct" + (a.status === "blown" ? " blown" : "");
  $("#r-account-card").replaceChildren(
    h("span", { class: "muted small" }, a.status === "blown" ? "Account blown: loss limit hit" : "Balance"),
    h("span", { class: "bal " + cls(a.realised_pnl) }, inr(a.cash)),
    h("span", { class: "small " + cls(a.realised_pnl) }, `${inr(a.realised_pnl)} · ${a.trades.length} trades${a.win_rate_pct != null ? ` · ${a.win_rate_pct}% wins` : ""}`),
    h("div", { class: "bar", title: "Distance to loss limit" }, h("i", { style: `width:${left}%` })),
    h("span", { class: "muted small" }, `Dies below ${inr(a.loss_limit)}`));
}
$("#r-account").addEventListener("change", showAccount);
$("#new-account").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    const a = await api("/api/paper/accounts", { method: "POST", body: { name: f.get("name"), capital: +f.get("capital"), max_loss_pct: +f.get("max_loss_pct") } });
    e.target.closest("details").open = false; await loadAccounts(a.id); toast("Account opened. Trade like it’s real.");
  } catch (err) { toast(err.message, true); }
});

const sessionsFor = async (symbol) => (rp.sessions[symbol] ??= await api(`/api/sessions?symbol=${encodeURIComponent(symbol)}`));
$("#r-random").addEventListener("click", async () => {
  const days = await sessionsFor($("#r-symbol").value);
  $("#r-date").value = days[5 + Math.floor(Math.random() * (days.length - 5))];
  loadSession();
});
$("#r-load").addEventListener("click", loadSession);

async function loadSession() {
  const symbol = $("#r-symbol").value, tf = $("#r-tf").value, date = $("#r-date").value;
  if (!date) return toast("Pick a date, or hit Surprise me.", true);
  const ds = lab.datasets.find((d) => d.symbol === symbol);
  if (!ds?.timeframes.includes(tf)) return toast(`${symbol} has no intraday data. Upload an intraday CSV to replay it.`, true);
  try {
    const days = await sessionsFor(symbol);
    const k = days.indexOf(date);
    if (k < 0) return toast("Market was closed that day (or it's outside the data). Try another date.", true);
    stop();
    if (rp.pos) await closePosition(true);
    rp.bars = await api(`/api/candles?symbol=${encodeURIComponent(symbol)}&timeframe=${tf}&start=${days[Math.max(0, k - 1)]}&end=${date}`);
    rp.i = rp.bars.findIndex((b) => b.iso.startsWith(date)); rp.symbol = symbol; rp.tf = tf; rp.markers = [];
    const c = chart($("#r-chart"), { intraday: true });
    rp.series = c.addCandlestickSeries(candleStyle());
    rp.series.setData(rp.bars.slice(0, rp.i + 1));
    c.timeScale().fitContent();
    tick(); toast("Previous day shown for context. Press → or Play.");
  } catch (e) { toast(e.message, true); }
}
function tick() {
  const b = rp.bars[rp.i];
  if (!b) return;
  $("#r-clock").textContent = b.iso.slice(0, 16);
  $("#r-last").textContent = b.close.toFixed(2);
  const pos = $("#r-pos");
  if (rp.pos) {
    const u = (rp.pos.side === "long" ? 1 : -1) * (b.close - rp.pos.price) * rp.pos.qty;
    pos.replaceChildren(`${rp.pos.side.toUpperCase()} ${rp.pos.qty} @ ${rp.pos.price.toFixed(2)} · `, h("span", { class: cls(u) }, inr(u)));
  } else pos.textContent = "Flat";
  $("#r-close").disabled = !rp.pos;
}
function step() {
  if (!rp.bars.length) return toast("Load a session first.", true);
  if (rp.i >= rp.bars.length - 1) { stop(); if (rp.pos) closePosition(); return toast("Session over. Positions are squared off at the close."); }
  rp.i++; rp.series.update(rp.bars[rp.i]); tick();
}
function play() { if (rp.timer) return stop(); if (!rp.bars.length) return toast("Load a session first.", true); rp.timer = setInterval(step, +$("#r-speed").value); $("#r-play").textContent = "❚❚ Pause"; }
function stop() { clearInterval(rp.timer); rp.timer = null; $("#r-play").textContent = "▶ Play"; }
function openPosition(side) {
  if (!rp.bars.length) return toast("Load a session first.", true);
  if (rp.account?.status === "blown") return toast("This account is blown. Open a new one and write down what went wrong.", true);
  if (rp.pos) return toast("Close your current position first.", true);
  const b = rp.bars[rp.i], qty = Math.max(1, +$("#r-qty").value || 1);
  if (b.close * qty > rp.account.cash) return toast(`That needs ${inr(b.close * qty)}; you have ${inr(rp.account.cash)}.`, true);
  rp.pos = { side, qty, price: b.close, iso: b.iso, note: $("#r-note").value };
  rp.markers.push({ time: b.time, position: side === "long" ? "belowBar" : "aboveBar", color: css("--saffron"), shape: side === "long" ? "arrowUp" : "arrowDown", text: side === "long" ? "B" : "S" });
  rp.series.setMarkers(rp.markers); tick();
}
async function closePosition(silent) {
  const p = rp.pos, b = rp.bars[rp.i];
  if (!p) return;
  rp.pos = null;
  try {
    const before = rp.account.cash;
    rp.account = await api(`/api/paper/accounts/${rp.account.id}/trades`, { method: "POST", body: { symbol: rp.symbol, timeframe: rp.tf, side: p.side, qty: p.qty, entry_time: p.iso, exit_time: b.iso, note: p.note } });
    const pnl = rp.account.cash - before;
    rp.markers.push({ time: b.time, position: p.side === "long" ? "aboveBar" : "belowBar", color: pnl > 0 ? css("--up") : css("--down"), shape: "circle", text: inr(pnl) });
    rp.series?.setMarkers(rp.markers);
    if (!silent) toast(rp.account.status === "blown" ? "Loss limit hit. This account is done." : `Closed: ${inr(pnl)} after charges.`, rp.account.status === "blown");
    $("#r-note").value = "";
    await loadAccounts(rp.account.id);
  } catch (e) { toast(e.message, true); }
  tick();
}
$("#r-step").addEventListener("click", step);
$("#r-play").addEventListener("click", play);
$("#r-speed").addEventListener("change", () => { if (rp.timer) { stop(); play(); } });
$("#r-buy").addEventListener("click", () => openPosition("long"));
$("#r-sell").addEventListener("click", () => openPosition("short"));
$("#r-close").addEventListener("click", () => closePosition());
addEventListener("keydown", (e) => {
  if ($("#view-replay").hidden || e.target.matches("input, select, textarea")) return;
  const k = e.key.toLowerCase();
  if (k === "arrowright") step(); else if (k === " ") { e.preventDefault(); play(); }
  else if (k === "b") openPosition("long"); else if (k === "s") openPosition("short"); else if (k === "c") closePosition();
});

/* ---------- PORTFOLIO ---------- */
async function loadPortfolio() {
  const [accts, brokers] = await Promise.all([api("/api/paper/accounts"), api("/api/portfolio/brokers")]);
  $("#p-accounts").replaceChildren(...(accts.length ? accts.map((a) => h("div", { class: "card" },
    h("span", { class: "t" }, a.name), h("span", { class: "v " + cls(a.cash - a.capital) }, inr(a.cash)),
    h("span", { class: "muted small" }, `started ${inr(a.capital)} · ${pct(((a.cash - a.capital) / a.capital) * 100)} · ${a.status}`))) : [h("p", { class: "muted" }, "No paper accounts yet. Open one in Replay.")]));
  $("#p-brokers").replaceChildren(...brokers.map((b) => h("div", { class: "card" }, h("span", { class: "t" }, b.name), h("button", { class: "btn", disabled: "" }, "Connect · soon"))));
}

/* ---------- DATA ---------- */
async function loadData() {
  lab.datasets = await api("/api/datasets");
  fillSymbols($("#f-symbol")); fillSymbols($("#r-symbol")); $("#f-symbol").value = lab.s.symbol; syncTimeframes();
  $("#d-table tbody").replaceChildren(...lab.datasets.map((d) => h("tr", {}, h("td", {}, d.symbol), h("td", {}, d.start), h("td", {}, d.end), h("td", {}, d.timeframes.join(" ")), h("td", {}, d.source))));
}
$("#upload").addEventListener("submit", async (e) => {
  e.preventDefault();
  try { const r = await api("/api/upload", { method: "POST", body: new FormData(e.target) }); toast(`${r.symbol} uploaded.`); e.target.reset(); loadData(); }
  catch (err) { toast(err.message, true); }
});
$("#yahoo").addEventListener("submit", async (e) => {
  e.preventDefault();
  const sym = new FormData(e.target).get("symbol").trim().toUpperCase();
  e.target.classList.add("loading");
  try { await api(`/api/candles?symbol=${encodeURIComponent(sym)}&limit=1`); toast(`${sym} fetched.`); e.target.reset(); loadData(); }
  catch (err) { toast(err.message, true); } finally { e.target.classList.remove("loading"); }
});

initLab().then(route).catch((e) => toast(e.message, true));
