#!/usr/bin/env python3
"""
build_release.py — Combine the 8 standalone lesson HTML files into ONE
self-contained walkthrough at release/cloud_training.html, with all assets
flattened into release/assets/.

Why a script (not a hand-merge):
  * Each lesson reuses class names (.beat-heart, .beat-jobs ...) with DIFFERENT
    rules, so the 8 <style> blocks would collide if concatenated. We scope every
    lesson's CSS under [data-layer="N"] with a small deterministic prefixer.
  * The 8 per-lesson IIFE engines each grab querySelectorAll(".beat") globally
    and would fight over the DOM. We replace them with ONE engine that walks a
    flat list of all beats and runs a generic [data-delay] staggered reveal
    (faithful to every lesson's original animation).
  * Re-runnable: edit any lesson, re-run this, release/ regenerates.

Run:  python build_release.py
"""

import os, re, json, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ROOT, "lessons")
RELEASE_DIR = os.path.join(ROOT, "release")
ASSETS_OUT = os.path.join(RELEASE_DIR, "assets")

# (layer, folder, html file, asset folder, color family accent)
LESSON_DEFS = [
    (0, "0_Intro",            "0_intro.html",            "0_intro_assets",            "#f59e0b"),  # amber (hook)
    (1, "1_computer",         "1_computer.html",         "1_computer_assets",         "#b0aea4"),  # gray (foundation)
    (2, "2_operating_system", "2_operating_system.html", "2_operating_system_assets", "#b0aea4"),  # gray
    (3, "3_networking",       "3_networking.html",       "3_networking_assets",       "#22c55e"),  # green
    (4, "4_server_computer",  "4_server_computer.html",  "4_server_computer_assets",  "#22c55e"),  # green
    (5, "5_server_os",        "5_server_os.html",        "5_server_os_assets",        "#22c55e"),  # green
    (6, "6_virtualization",   "6_virtualization.html",   "6_virtualization_assets",   "#8b5cf6"),  # purple
    (7, "7_azure",            "7_azure.html",            "7_azure_assets",            "#4a9eed"),  # blue
]

# Intro has no MODULE block: synthesize labels + cumulative target (minute 5).
INTRO_LABELS = ["Title", "The hook", "Phone → datacenter", "Datacenter scale",
                "Punchline", "Roadmap", "Through-line"]
INTRO_TARGET = 5 * 60


# ───────────────────────── balanced / comment-aware scanners ─────────────────

def capture_balanced(text, start, open_ch, close_ch):
    """Return the substring text[start:end] covering a balanced open/close pair.
    start must point at open_ch. Respects ' " ` strings and // and /* */ comments."""
    depth = 0
    i = start
    n = len(text)
    in_str = None
    esc = False
    while i < n:
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == in_str:
                in_str = None
        else:
            if c == "/" and i + 1 < n and text[i + 1] == "/":
                j = text.find("\n", i)
                i = n if j == -1 else j
                continue
            if c == "/" and i + 1 < n and text[i + 1] == "*":
                j = text.find("*/", i + 2)
                i = n if j == -1 else j + 2
                continue
            if c in "\"'`":
                in_str = c
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced block starting at %d" % start)


# ───────────────────────── per-lesson extraction ────────────────────────────

def extract_style(html):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    return m.group(1) if m else ""


def extract_h1(html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def extract_tag(html):
    m = re.search(r'<span class="module-tag">(.*?)</span>', html, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def extract_stage_inner(html):
    m = re.search(r'<div class="stage"[^>]*>', html)
    if not m:
        raise ValueError("no stage div")
    start = m.end()
    notes_idx = html.index('<div id="notes"', start)
    close_idx = html.rindex("</div>", start, notes_idx)
    return html[start:close_idx]


def extract_notes_literal(html):
    m = re.search(r"const NOTES\s*=\s*", html)
    if not m:
        raise ValueError("no NOTES")
    bracket = html.index("[", m.end())
    return capture_balanced(html, bracket, "[", "]")


def extract_module(html):
    m = re.search(r"const MODULE\s*=\s*", html)
    if not m:
        return None
    brace = html.index("{", m.end())
    return capture_balanced(html, brace, "{", "}")


def module_field(module_text, field):
    """Pull a string field like name: "OS"."""
    m = re.search(field + r"\s*:\s*\"([^\"]*)\"", module_text)
    return m.group(1) if m else None


def module_target_seconds(module_text):
    m = re.search(r"targetSeconds\s*:\s*([0-9*\s]+?)\s*,", module_text)
    if not m:
        return None
    return int(eval(m.group(1).strip()))  # only digits/*/space


def module_beatlabels_literal(module_text):
    m = re.search(r"beatLabels\s*:\s*", module_text)
    if not m:
        return None
    bracket = module_text.index("[", m.end())
    return capture_balanced(module_text, bracket, "[", "]")


# ───────────────────────── CSS scoping (prefix under [data-layer]) ───────────

def split_selectors(sel):
    parts, depth, buf = [], 0, ""
    for c in sel:
        if c in "([":
            depth += 1; buf += c
        elif c in ")]":
            depth -= 1; buf += c
        elif c == "," and depth == 0:
            parts.append(buf); buf = ""
        else:
            buf += c
    if buf.strip():
        parts.append(buf)
    return parts


def prefix_selectors(sel, layer):
    scope = '[data-layer="%d"]' % layer
    out = []
    for part in split_selectors(sel):
        p = part.strip()
        if not p:
            continue
        if p == ":root":
            out.append(scope)            # palette vars apply to the section
        else:
            out.append("%s %s" % (scope, p))
    return ", ".join(out)


def scope_css(css, layer, keyframes):
    """Prefix every style rule with [data-layer="N"]. Pull @keyframes out to a
    shared dict (dedup by prelude). Recurse into @media/@supports/@container.
    Drops comments."""
    out = []
    i, n = 0, len(css)
    prelude = ""
    while i < n:
        c = css[i]
        # comments
        if c == "/" and i + 1 < n and css[i + 1] == "*":
            j = css.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c == "{":
            block = capture_balanced(css, i, "{", "}")
            inner = block[1:-1]
            pre = prelude.strip()
            low = pre.lower()
            if low.startswith("@keyframes") or low.startswith("@-webkit-keyframes"):
                keyframes[pre] = pre + " {" + inner + "}"
            elif low.startswith("@media") or low.startswith("@supports") or low.startswith("@container"):
                out.append(pre + " {\n" + scope_css(inner, layer, keyframes) + "\n}")
            elif low.startswith("@"):
                out.append(pre + " {" + inner + "}")
            else:
                psel = prefix_selectors(pre, layer)
                if psel:
                    out.append(psel + " {" + inner + "}")
            prelude = ""
            i += len(block)
            continue
        if c == ";" and prelude.strip().startswith("@"):
            out.append(prelude.strip() + ";")
            prelude = ""
            i += 1
            continue
        prelude += c
        i += 1
    return "\n".join(out)


# ───────────────────────── global chrome CSS (from canonical Layer 2) ────────

GLOBAL_CHROME = r"""
  :root {
    --bg-page: #0e0e10;
    --bg-surface: #1a1a1d;
    --bg-muted: #2a2a2e;
    --text-primary: #f3f1ea;
    --text-secondary: #b0aea4;
    --text-tertiary: #7a7872;
    --border: rgba(255, 255, 255, 0.10);
    --border-strong: rgba(255, 255, 255, 0.25);
    --blue-50:  #E6F1FB;
    --blue-600: #4a9eed;
    --blue-800: #185FA5;
    --amber-50:  #FAEEDA;
    --amber-600: #f59e0b;
    --amber-800: #BA7517;
    --green-600: #22c55e;
    --purple-600: #8b5cf6;
    --accent: #4a9eed;
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; }
  body {
    font-family: var(--font-sans);
    background: var(--bg-page);
    color: var(--text-primary);
    margin: 0; padding: 0;
    font-size: 14px; line-height: 1.5;
    min-height: 100vh;
  }

  /* ===== App shell: sidebar + main ===== */
  .app { display: flex; min-height: 100vh; }
  .sidebar {
    width: 256px; flex-shrink: 0;
    background: var(--bg-surface);
    border-right: 1px solid var(--border);
    overflow-y: auto; max-height: 100vh;
    position: sticky; top: 0;
    padding: 16px 10px 24px;
  }
  .sidebar.collapsed { display: none; }
  .sidebar-title {
    font-size: 12px; font-family: var(--font-mono);
    color: var(--text-tertiary); letter-spacing: 0.5px;
    text-transform: uppercase; padding: 0 8px 12px;
  }
  .lesson-list { list-style: none; margin: 0; padding: 0; }
  .lesson-row {
    display: flex; align-items: center; gap: 8px; width: 100%;
    text-align: left; background: transparent; border: 1px solid transparent;
    border-radius: 8px; padding: 8px 10px; margin: 1px 0;
    color: var(--text-secondary); font-size: 13px; cursor: pointer;
  }
  .lesson-row:hover { background: var(--bg-muted); }
  .lesson-row.active { color: var(--text-primary); background: var(--bg-muted); border-color: var(--accent); }
  .lesson-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
  .lesson-num { font-family: var(--font-mono); font-size: 11px; color: var(--text-tertiary); width: 12px; }
  .lesson-name { flex: 1; }
  .lesson-caret { font-size: 10px; color: var(--text-tertiary); transition: transform 120ms; }
  .lesson-item.expanded .lesson-caret { transform: rotate(90deg); }
  .beat-list { list-style: none; margin: 0 0 4px; padding: 0; display: none; }
  .lesson-item.expanded .beat-list { display: block; }
  .beat-row {
    display: block; width: 100%; text-align: left;
    background: transparent; border: none; cursor: pointer;
    color: var(--text-tertiary); font-size: 12px; line-height: 1.4;
    padding: 5px 10px 5px 32px; border-radius: 6px;
  }
  .beat-row:hover { background: var(--bg-muted); color: var(--text-secondary); }
  .beat-row.active { color: var(--text-primary); background: rgba(255,255,255,0.04); box-shadow: inset 2px 0 0 var(--accent); }

  .main { flex: 1; min-width: 0; padding: 20px 24px; }
  .container { max-width: 1280px; margin: 0 auto; }

  header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; gap: 12px; }
  .header-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
  h1 { font-size: 18px; font-weight: 500; margin: 0; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .module-tag { font-size: 12px; color: var(--text-tertiary); font-family: var(--font-mono); white-space: nowrap; }
  .icon-btn {
    font-size: 16px; line-height: 1; padding: 6px 10px;
    background: var(--bg-surface); color: var(--text-secondary);
    border: 1px solid var(--border-strong); border-radius: 8px; cursor: pointer;
  }
  .icon-btn:hover { background: var(--bg-muted); }

  .controls { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
  button {
    font-family: inherit; font-size: 13px; padding: 8px 16px;
    background: var(--bg-surface); color: var(--text-primary);
    border: 1px solid var(--border-strong); border-radius: 8px;
    cursor: pointer; transition: background 120ms, transform 80ms;
  }
  button:hover:not(:disabled) { background: var(--bg-muted); }
  button:active:not(:disabled) { transform: scale(0.98); }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  button.primary { font-weight: 500; background: var(--accent); color: #fff; border-color: var(--accent); }
  button.primary:hover:not(:disabled) { filter: brightness(1.12); }
  .step-counter { margin-left: 8px; font-size: 12px; color: var(--text-tertiary); font-family: var(--font-mono); }

  .stage {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden; min-height: 560px;
    display: flex; align-items: center; justify-content: center; position: relative;
  }
  .lesson { display: contents; }
  .beat { display: none; width: 100%; height: 100%; padding: 32px; animation: fadein 480ms ease; }
  .beat.active { display: flex; }
  @keyframes fadein { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

  .notes {
    margin-top: 14px; padding: 14px 18px; background: var(--bg-surface);
    border: 1px solid var(--border); border-left: 3px solid var(--amber-600);
    border-radius: 10px; font-size: 13px; color: var(--text-secondary);
    line-height: 1.6; display: none;
  }
  .notes.show { display: block; }
  .notes strong { color: var(--text-primary); font-weight: 500; }
  .notes-label { color: var(--amber-600); font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.5px; display: block; margin-bottom: 6px; }

  .footer-hint { margin-top: 14px; color: var(--text-tertiary); font-size: 12px; text-align: center; }
  .footer-hint code { font-family: var(--font-mono); background: var(--bg-muted); padding: 2px 6px; border-radius: 4px; }

  .timer-block {
    margin-left: auto; display: flex; align-items: center; gap: 14px;
    font-family: var(--font-mono); font-size: 13px; color: var(--text-secondary);
    padding: 6px 14px; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px;
  }
  .timer-block.paused { opacity: 0.5; }
  .timer-elapsed { color: var(--text-primary); font-weight: 500; }
  .timer-target { color: var(--text-tertiary); }
  .timer-delta { font-weight: 500; }
  .timer-delta.ahead { color: var(--green-600); }
  .timer-delta.behind { color: var(--amber-600); }
  .timer-delta.on { color: var(--text-tertiary); }

  .log-badge { margin-left: 4px; color: var(--text-tertiary); font-family: var(--font-mono); font-size: 11px; }
  .log-panel { margin-top: 14px; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; display: none; }
  .log-panel.show { display: block; }
  .log-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; gap: 10px; flex-wrap: wrap; }
  .log-panel-title { color: var(--text-primary); font-size: 13px; font-weight: 500; }
  .log-panel-meta { color: var(--text-tertiary); font-size: 12px; font-family: var(--font-mono); }
  .log-panel-actions { display: flex; gap: 8px; }
  .log-panel-actions button { font-size: 12px; padding: 5px 12px; }
  .log-content { font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary); line-height: 1.6; max-height: 240px; overflow-y: auto; background: var(--bg-page); border-radius: 6px; padding: 10px 12px; white-space: pre; }

  @media (max-width: 720px) { .sidebar { position: fixed; z-index: 50; height: 100vh; box-shadow: 0 0 40px rgba(0,0,0,0.6); } }
"""


# ───────────────────────── unified engine JS ────────────────────────────────

ENGINE_JS = r"""
(function () {
  const LESSONS = __LESSONS__;

  // Build flat beat list from the DOM (sections are rendered in order).
  const FLAT = [];
  const LESSON_START = [];
  let acc = 0;
  LESSONS.forEach((L, li) => {
    const section = document.querySelector('.lesson[data-layer="' + L.layer + '"]');
    const beats = section.querySelectorAll(".beat");
    L.beatCount = beats.length;
    LESSON_START[li] = acc;
    beats.forEach((b, bi) => { b.classList.remove("active"); FLAT.push({ li, bi, el: b, L }); });
    acc += beats.length;
  });
  const TOTAL = FLAT.length;

  const app = document.getElementById("app");
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const titleEl = document.getElementById("lesson-title");
  const tagEl = document.getElementById("module-tag");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const notesBtn = document.getElementById("notes-btn");
  const resetBtn = document.getElementById("reset-btn");
  const counter = document.getElementById("step-counter");
  const notesEl = document.getElementById("notes");
  const notesContent = document.getElementById("notes-content");

  const timerBlock = document.getElementById("timer-block");
  const elapsedEl = document.getElementById("timer-elapsed");
  const targetEl = document.getElementById("timer-target");
  const deltaEl = document.getElementById("timer-delta");
  const logBtn = document.getElementById("log-btn");
  const logBadge = document.getElementById("log-badge");
  const logPanel = document.getElementById("log-panel");
  const logContent = document.getElementById("log-content");
  const logMeta = document.getElementById("log-meta");
  const logPauseBtn = document.getElementById("log-pause-btn");
  const logDownloadBtn = document.getElementById("log-download-btn");
  const logCopyBtn = document.getElementById("log-copy-btn");
  const logClearBtn = document.getElementById("log-clear-btn");

  // localStorage keys — same names the standalone lessons used, so a session
  // started in an old file continues here.
  const LS_LOG = "cloud_training_log";
  const LS_START = "cloud_training_start";
  const LS_PAUSED_AT = "cloud_training_paused_at";
  const LS_PAUSE_OFFSET = "cloud_training_pause_offset";
  const LS_POS = "cloud_training_pos";

  let g = 0;
  let notesOpen = false;
  let logOpen = false;

  const cur = () => FLAT[g];

  // ───────── sidebar ─────────
  function buildSidebar() {
    const ul = document.createElement("ul");
    ul.className = "lesson-list";
    LESSONS.forEach((L, li) => {
      const item = document.createElement("li");
      item.className = "lesson-item";
      item.dataset.lesson = li;

      const row = document.createElement("button");
      row.className = "lesson-row";
      row.dataset.lesson = li;
      row.innerHTML =
        '<span class="lesson-dot" style="background:' + L.accent + '"></span>' +
        '<span class="lesson-num">' + L.layer + '</span>' +
        '<span class="lesson-name">' + L.name + '</span>' +
        '<span class="lesson-caret">▸</span>';
      row.addEventListener("click", () => go(LESSON_START[li], "⇲"));
      item.appendChild(row);

      const blist = document.createElement("ul");
      blist.className = "beat-list";
      L.labels.forEach((lab, bi) => {
        const bli = document.createElement("li");
        const brow = document.createElement("button");
        brow.className = "beat-row";
        brow.dataset.lesson = li;
        brow.dataset.beat = bi;
        brow.textContent = (bi + 1) + ". " + lab;
        brow.addEventListener("click", () => go(LESSON_START[li] + bi, "⇲"));
        bli.appendChild(brow);
        blist.appendChild(bli);
      });
      item.appendChild(blist);
      ul.appendChild(item);
    });
    const title = document.createElement("div");
    title.className = "sidebar-title";
    title.textContent = "Cloud Training";
    sidebar.appendChild(title);
    sidebar.appendChild(ul);
  }

  function updateSidebar() {
    const f = cur();
    sidebar.querySelectorAll(".lesson-item").forEach((item, li) => {
      item.classList.toggle("expanded", li === f.li);
      item.querySelector(".lesson-row").classList.toggle("active", li === f.li);
    });
    sidebar.querySelectorAll(".beat-row").forEach((br) => {
      const on = (+br.dataset.lesson === f.li && +br.dataset.beat === f.bi);
      br.classList.toggle("active", on);
      if (on) br.scrollIntoView({ block: "nearest" });
    });
  }

  // ───────── log ─────────
  function getLog() { try { return JSON.parse(localStorage.getItem(LS_LOG) || "[]"); } catch (e) { return []; } }
  function saveLog(a) { localStorage.setItem(LS_LOG, JSON.stringify(a)); }
  function fmtDuration(t) {
    const h = Math.floor(t / 3600), m = Math.floor((t % 3600) / 60), s = Math.floor(t % 60);
    return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }
  function fmtMinSec(t) {
    const m = Math.floor(t / 60), s = Math.floor(t % 60);
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }
  function logEvent(arrow, label) {
    const e = getLog(); e.push({ t: getElapsedSeconds(), arrow, label }); saveLog(e); renderLog();
  }
  function renderLog() {
    const e = getLog();
    logBadge.textContent = e.length;
    logMeta.textContent = e.length + " event" + (e.length === 1 ? "" : "s");
    logContent.textContent = e.length === 0
      ? "No events yet. Click Next to begin."
      : e.map(x => "[" + fmtDuration(x.t) + "]  " + x.arrow + "  " + x.label).join("\n");
    if (e.length) logContent.scrollTop = logContent.scrollHeight;
  }

  // ───────── timer ─────────
  function getStart() { const s = localStorage.getItem(LS_START); return s ? parseInt(s, 10) : null; }
  function getPauseOffset() { return parseInt(localStorage.getItem(LS_PAUSE_OFFSET) || "0", 10); }
  function getPausedAt() { const v = localStorage.getItem(LS_PAUSED_AT); return v ? parseInt(v, 10) : null; }
  function isPaused() { return getPausedAt() !== null; }
  function getElapsedSeconds() {
    const start = getStart(); if (!start) return 0;
    const offset = getPauseOffset(), pausedAt = getPausedAt();
    return Math.floor(((pausedAt || Date.now()) - start - offset) / 1000);
  }
  function ensureStarted() {
    if (!getStart()) { localStorage.setItem(LS_START, String(Date.now())); logEvent("⏵", "Session started — Layer " + cur().L.layer + " " + cur().L.name); }
  }
  function pauseTimer() { if (isPaused()) return; localStorage.setItem(LS_PAUSED_AT, String(Date.now())); logEvent("⏸", "PAUSED"); updateTimerDisplay(); }
  function resumeTimer() {
    const p = getPausedAt(); if (!p) return;
    localStorage.setItem(LS_PAUSE_OFFSET, String(getPauseOffset() + (Date.now() - p)));
    localStorage.removeItem(LS_PAUSED_AT); logEvent("▶", "resumed"); updateTimerDisplay();
  }
  function togglePause() { isPaused() ? resumeTimer() : pauseTimer(); }
  function updateTimerDisplay() {
    const elapsed = getElapsedSeconds(), target = cur().L.target;
    elapsedEl.textContent = fmtMinSec(elapsed);
    targetEl.textContent = fmtMinSec(target);
    const diff = target - elapsed;
    deltaEl.classList.remove("ahead", "behind", "on");
    if (Math.abs(diff) <= 30) { deltaEl.classList.add("on"); deltaEl.textContent = "on time"; }
    else if (diff > 0) { deltaEl.classList.add("ahead"); deltaEl.textContent = fmtMinSec(diff) + " ahead"; }
    else { deltaEl.classList.add("behind"); deltaEl.textContent = fmtMinSec(-diff) + " behind"; }
    timerBlock.classList.toggle("paused", isPaused());
    logPauseBtn.textContent = isPaused() ? "▶ Resume" : "⏸ Pause";
  }
  setInterval(updateTimerDisplay, 1000);

  // ───────── engine ─────────
  function render() {
    const f = cur(), L = f.L;
    FLAT.forEach((x, i) => x.el.classList.toggle("active", i === g));
    titleEl.textContent = L.title;
    tagEl.textContent = L.tag;
    counter.textContent = "Beat " + (f.bi + 1) + " of " + L.beatCount;
    app.style.setProperty("--accent", L.accent);

    prevBtn.disabled = g === 0;
    if (g === TOTAL - 1) { nextBtn.disabled = true; nextBtn.textContent = "End of training 🎓"; }
    else {
      nextBtn.disabled = false;
      nextBtn.textContent = (f.bi === L.beatCount - 1) ? ("Next: " + FLAT[g + 1].L.name + " →") : "Next →";
    }

    const n = L.notes[f.bi];
    notesContent.innerHTML = n ? ("<strong>" + n.title + "</strong><br>" + n.body) : "";

    // generic staggered reveal — faithful to every lesson's [data-delay] anim
    const reveal = f.el.querySelectorAll("[data-delay]");
    reveal.forEach(e => e.classList.remove("show"));
    reveal.forEach(e => { const d = parseInt(e.dataset.delay || "0", 10); setTimeout(() => e.classList.add("show"), d + 60); });

    updateSidebar();
    localStorage.setItem(LS_POS, String(g));
  }

  function go(target, arrow) {
    if (target < 0 || target >= TOTAL || target === g) { if (target === g) { render(); } return; }
    const forward = target > g;
    if (forward) ensureStarted();
    g = target;
    render();
    const f = cur();
    const label = "L" + f.L.layer + " · " + (f.L.labels[f.bi] || ("Beat " + (f.bi + 1)));
    logEvent(arrow || (forward ? "→" : "←"), label);
  }
  function next() { if (g < TOTAL - 1) go(g + 1, "→"); }
  function prev() { if (g > 0) go(g - 1, "←"); }

  function reset() {
    const e = getLog();
    if (e.length > 0 && !confirm("Reset session? You've recorded " + e.length + " events across " + fmtMinSec(getElapsedSeconds()) + ".")) return;
    [LS_LOG, LS_START, LS_PAUSED_AT, LS_PAUSE_OFFSET, LS_POS].forEach(k => localStorage.removeItem(k));
    g = 0; render(); renderLog(); updateTimerDisplay();
  }

  function toggleNotes() { notesOpen = !notesOpen; notesEl.classList.toggle("show", notesOpen); notesBtn.classList.toggle("primary", notesOpen); }
  function toggleLog() { logOpen = !logOpen; logPanel.classList.toggle("show", logOpen); logBtn.classList.toggle("primary", logOpen); if (logOpen) renderLog(); }
  function toggleSidebar() { sidebar.classList.toggle("collapsed"); }

  function downloadLog() {
    const e = getLog(); if (!e.length) { alert("Log is empty — nothing to download."); return; }
    const header = "# Cloud Training Session Log\n# Generated: " + new Date().toISOString() + "\n# Events: " + e.length + "\n\n";
    const body = e.map(x => "[" + fmtDuration(x.t) + "]\t" + x.arrow + "\t" + x.label).join("\n");
    const blob = new Blob([header + body], { type: "text/plain" });
    const url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = "cloud_training_session_" + new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19) + ".log";
    a.click(); URL.revokeObjectURL(url);
  }
  async function copyLog() {
    const e = getLog(); if (!e.length) { alert("Log is empty."); return; }
    const text = e.map(x => "[" + fmtDuration(x.t) + "]\t" + x.arrow + "\t" + x.label).join("\n");
    try { await navigator.clipboard.writeText(text); logCopyBtn.textContent = "✓ Copied"; setTimeout(() => logCopyBtn.textContent = "📋 Copy", 1500); }
    catch (e2) { alert("Couldn't copy automatically — select the text in the log panel manually."); }
  }
  function clearLogOnly() { if (!confirm("Clear the log? Timer keeps running. This is separate from Reset.")) return; localStorage.removeItem(LS_LOG); renderLog(); }

  // ───────── wiring ─────────
  nextBtn.addEventListener("click", next);
  prevBtn.addEventListener("click", prev);
  resetBtn.addEventListener("click", reset);
  notesBtn.addEventListener("click", toggleNotes);
  logBtn.addEventListener("click", toggleLog);
  sidebarToggle.addEventListener("click", toggleSidebar);
  logPauseBtn.addEventListener("click", togglePause);
  logDownloadBtn.addEventListener("click", downloadLog);
  logCopyBtn.addEventListener("click", copyLog);
  logClearBtn.addEventListener("click", clearLogOnly);

  document.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.code === "ArrowRight" || e.code === "Enter" || e.code === "Space") { e.preventDefault(); next(); }
    else if (e.code === "ArrowLeft") { e.preventDefault(); prev(); }
    else if (e.key === "n" || e.key === "N") toggleNotes();
    else if (e.key === "l" || e.key === "L") toggleLog();
    else if (e.key === "s" || e.key === "S") toggleSidebar();
    else if (e.key === "p" || e.key === "P") { ensureStarted(); togglePause(); }
    else if (e.key === "r" || e.key === "R") reset();
    else if (/^[0-7]$/.test(e.key)) { const li = +e.key; if (li < LESSONS.length) go(LESSON_START[li], "⇲"); }
  });

  // ───────── init ─────────
  buildSidebar();
  const saved = parseInt(localStorage.getItem(LS_POS) || "0", 10);
  if (saved > 0 && saved < TOTAL) g = saved;
  render(); renderLog(); updateTimerDisplay();
})();
"""


PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cloud Training — Full Walkthrough (Layers 0–7)</title>
<style>
__CSS__
</style>
</head>
<body>
<div class="app" id="app">
  <nav class="sidebar" id="sidebar"></nav>
  <div class="main">
    <div class="container">
      <header>
        <div class="header-left">
          <button id="sidebar-toggle" class="icon-btn" title="Toggle sidebar (S)">&#9776;</button>
          <h1 id="lesson-title">Cloud Training</h1>
        </div>
        <span class="module-tag" id="module-tag"></span>
      </header>

      <div class="controls">
        <button id="prev-btn">&larr; Back</button>
        <button id="next-btn" class="primary">Next &rarr;</button>
        <button id="notes-btn">Speaker notes</button>
        <button id="log-btn">&#128203; Log <span class="log-badge" id="log-badge">0</span></button>
        <button id="reset-btn">Reset</button>
        <span id="step-counter" class="step-counter">Beat 1 of 7</span>
        <div class="timer-block" id="timer-block">
          <span><span class="timer-elapsed" id="timer-elapsed">00:00</span> elapsed</span>
          <span>target <span class="timer-target" id="timer-target">05:00</span></span>
          <span class="timer-delta on" id="timer-delta">on time</span>
        </div>
      </div>

      <div class="stage" id="stage">
__SECTIONS__
      </div>

      <div id="notes" class="notes">
        <span class="notes-label">SPEAKER NOTES</span>
        <div id="notes-content"></div>
      </div>

      <div id="log-panel" class="log-panel">
        <div class="log-panel-header">
          <span class="log-panel-title">Session log</span>
          <span class="log-panel-meta" id="log-meta">0 events</span>
          <div class="log-panel-actions">
            <button id="log-pause-btn">&#9208; Pause</button>
            <button id="log-download-btn">&#11015; Download</button>
            <button id="log-copy-btn">&#128203; Copy</button>
            <button id="log-clear-btn">&#128465; Clear</button>
          </div>
        </div>
        <div class="log-content" id="log-content">No events yet. Click Next to begin.</div>
      </div>

      <p class="footer-hint">
        <code>&larr;</code> / <code>&rarr;</code> navigate &middot; <code>0</code>&ndash;<code>7</code> jump to lesson &middot;
        <code>N</code> notes &middot; <code>L</code> log &middot; <code>S</code> sidebar &middot; <code>P</code> pause &middot; <code>R</code> reset
      </p>
    </div>
  </div>
</div>
<script>
__JS__
</script>
</body>
</html>
"""


def main():
    keyframes = {}
    scoped_css_parts = []
    sections = []
    lessons_js = []

    for layer, folder, htmlfile, assetfolder, accent in LESSON_DEFS:
        path = os.path.join(LESSONS_DIR, folder, htmlfile)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()

        style = extract_style(html)
        h1 = extract_h1(html)
        tag = extract_tag(html)
        stage = extract_stage_inner(html)
        notes_lit = extract_notes_literal(html)
        module = extract_module(html)

        # asset paths -> flat assets/
        stage = stage.replace(assetfolder + "/", "assets/")
        # let JS own the active state
        stage = re.sub(r'class="beat([^"]*?)\s+active"', r'class="beat\1"', stage)

        if module:
            name = module_field(module, "name") or folder
            target = module_target_seconds(module)
            labels_lit = module_beatlabels_literal(module)
        else:
            name = "Intro"
            target = INTRO_TARGET
            labels_lit = json.dumps(INTRO_LABELS, ensure_ascii=False)

        scoped_css_parts.append("/* ===== Layer %d (%s) ===== */\n%s"
                                % (layer, name, scope_css(style, layer, keyframes)))

        sections.append('<section class="lesson" data-layer="%d">\n%s\n</section>'
                        % (layer, stage.strip()))

        lessons_js.append(
            "{layer:%d, name:%s, title:%s, tag:%s, target:%d, accent:%s, labels:%s, notes:%s}"
            % (layer, json.dumps(name, ensure_ascii=False), json.dumps(h1, ensure_ascii=False),
               json.dumps(tag, ensure_ascii=False), target, json.dumps(accent),
               labels_lit, notes_lit)
        )
        print("  layer %d  %-16s beats-html ok  notes ok  target=%ds" % (layer, name, target))

    full_css = (GLOBAL_CHROME
                + "\n\n  /* ===== keyframes (deduped) ===== */\n  "
                + "\n  ".join(keyframes.values())
                + "\n\n  /* ===== per-lesson scoped beat CSS ===== */\n"
                + "\n\n".join(scoped_css_parts))

    lessons_array = "[\n" + ",\n".join(lessons_js) + "\n]"
    engine = ENGINE_JS.replace("__LESSONS__", lessons_array)

    page = (PAGE_TEMPLATE
            .replace("__CSS__", full_css)
            .replace("__SECTIONS__", "\n".join(sections))
            .replace("__JS__", engine))

    # write release/
    os.makedirs(ASSETS_OUT, exist_ok=True)
    out_html = os.path.join(RELEASE_DIR, "cloud_training.html")
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(page)

    # flatten assets
    copied = 0
    for layer, folder, htmlfile, assetfolder, accent in LESSON_DEFS:
        src = os.path.join(LESSONS_DIR, folder, assetfolder)
        if not os.path.isdir(src):
            continue
        for fn in os.listdir(src):
            sp = os.path.join(src, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(ASSETS_OUT, fn))
                copied += 1

    print("\n  wrote %s (%d KB)" % (out_html, os.path.getsize(out_html) // 1024))
    print("  copied %d assets -> %s" % (copied, ASSETS_OUT))


if __name__ == "__main__":
    main()
