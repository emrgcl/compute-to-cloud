---
name: cloud-training-walkthrough
description: HTML layout, styling, and conventions for Emre's beat-by-beat training walkthroughs. Use this skill whenever creating or revising a self-contained HTML training module — modules that open by double-click, present 8-9 beats one at a time, with shared session timer across files, speaker notes panel, session log, and dark theme. Triggers include any request to build a training layer, lesson walkthrough, beat-based presentation, screen-recordable lecture HTML, or extension of the cloud training project. Also use when modifying any of the existing 0_intro through 7_azure HTML files.
---

# Cloud Training Walkthrough — HTML/CSS/JS Spec

This is the reference for the beat-by-beat training walkthrough layout. Each file is **self-contained**, opens by **double-click**, and presents one of N modules in a multi-module training. State (timer, session log) is shared across all module files via `localStorage`.

## Design contract (locked)

These properties are non-negotiable. Don't deviate without explicit instruction.

### Visual
- **Dark theme only.** No light-mode toggle.
- **Background:** page `#0e0e10`, surface `#1a1a1d`, muted `#2a2a2e`.
- **Text:** primary `#f3f1ea`, secondary `#b0aea4`, tertiary `#7a7872`.
- **Borders:** subtle `rgba(255, 255, 255, 0.10)`; strong `rgba(255, 255, 255, 0.25)`.
- **Accent:** amber `#fde68a` for keepers/emphasis, never red.
- **Font stack:** `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`; mono `ui-monospace, "SF Mono", Menlo, Consolas, monospace`.
- **Base size:** 14px body, 18px h1.
- **Border radius:** 8px for buttons, 14px for the stage block, 10-12px for content cards inside beats.

### Color families per module

When this template is used for a series, color-code modules so the audience subliminally recognizes related families.

| Modules | Color family | Hex (border) |
|---|---|---|
| Foundation | gray | `#5F5E5A` |
| Network/Server | green | `#3B6D11` / `#7fcfa0` |
| Virtualization | purple | `#534AB7` / `#a89df5` |
| Cloud | blue | `#185FA5` / `#7fc7f5` |

Each module's stage block, primary borders, and section accents pull from its assigned family. Yellow/amber (`#fde68a`) is the universal keeper-sentence color across all modules.

### Layout
- **Container:** `max-width: 1280px`, centered.
- **Stage block:** `min-height: 560px`, holds all beats, only one visible at a time.
- **Padding:** 20-24px page, 32px inside beats.
- **No CDN. No build step. No frameworks.** Vanilla HTML/CSS/JS.
- **Offline-first.** Must open from disk via `file://`.

### Beats
- 8-9 beats per module. More than 10 = pedagogical overload.
- Each beat has: a visual (SVG/PNG asset), a caption (the keeper sentence), and a speaker note (the delivery script).
- Only one beat visible at a time (`display: none` on inactive, `display: flex` on active).
- Beats animate in with a subtle fade — no flashy transitions.

### Asset naming (locked)
- Pattern: `{module_number}_{beat_counter}_{slug}.{ext}`
- `beat_counter` is the **1-indexed** number the audience sees on screen ("Beat 7 of 9"), NOT the `data-beat` attribute (0-indexed). They are deliberately off by one.
- Example: A beat displayed as "Beat 7 of 9" with `data-beat="6"` has its asset at `6_beat7_three_questions.svg`.
- Slug is descriptive, lowercase, underscores: `the_problem`, `policy_machine_revealed`, `gui_vs_cli`.

## File structure (single module)

```
{N}_{module_slug}.html              ← double-click to open
{N}_{module_slug}_assets/           ← all SVG and PNG assets
  ├── {N}_beat{M}_{slug}.svg
  └── {N}_beat{M}_{slug}.png
```

A delivered zip contains the HTML file and the assets folder side-by-side.

## HTML skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cloud Training — {Module Name}</title>
<style>/* all CSS inline — no external stylesheets */</style>
</head>
<body>
<div class="container">

  <header>
    <h1>Cloud Training Roadmap — {Module Name}</h1>
    <span class="module-tag">Layer {N} · ~{X} minutes</span>
  </header>

  <div class="controls">
    <button id="back-btn">← Back</button>
    <button id="next-btn" class="primary">Next →</button>
    <button id="notes-btn">Speaker notes</button>
    <button id="log-btn">📋 Log <span id="log-count">0</span></button>
    <button id="reset-btn">Reset</button>
    <span id="step-counter" class="step-counter">Beat 1 of {N}</span>
    <div class="timer-display">
      <span id="elapsed-time">00:00</span> elapsed
      <span class="separator">·</span>
      target <span id="target-time">00:00</span>
      <span id="time-diff"></span>
    </div>
  </div>

  <div class="stage" id="stage">
    <!-- One beat per div, only first has class="active" -->
    <div class="beat beat-title active" data-beat="0">
      <h2 class="big-title">{Title}</h2>
      <p class="big-sub">{Subtitle}</p>
      <p class="timer">Layer {N} · {Module Name} · ~{X} min</p>
    </div>

    <div class="beat beat-netframe" data-beat="1">
      <div class="net-wrap">
        <object data="{N}_{slug}_assets/{N}_beat2_{slug}.svg"
                type="image/svg+xml"
                aria-label="{Accessible description of the visual}"></object>
      </div>
      <p class="net-caption">
        {Caption HTML with <strong>emphasis</strong> and <em>keepers</em>.}
      </p>
    </div>
    <!-- ... more beats ... -->
  </div>

  <div id="notes" class="notes" hidden>
    <span class="notes-label">SPEAKER NOTES</span>
    <div id="notes-content"></div>
  </div>

  <div id="log-panel" class="log-panel" hidden>
    <!-- Session log markup -->
  </div>

</div>

<script>/* all JS inline */</script>
</body>
</html>
```

## CSS conventions

### Beat types (CSS class on the `<div class="beat ...">` wrapper)
- `beat-title` — the title slide. Big centered text, no asset.
- `beat-netframe` — standard beat with one asset and a caption below it. **Most common.**
- `beat-throughline` — promise/sentence/footnote stack for handoff beats.
- `beat-spectable` — for animated spec-comparison tables (use sparingly, only when comparing 4+ rows of paired data).

### Beat anatomy (`beat-netframe`)
```html
<div class="beat beat-netframe" data-beat="N">
  <div class="net-wrap">
    <object data="..." type="image/svg+xml" aria-label="..."></object>
  </div>
  <p class="net-caption">
    Caption with the keeper sentence. Use <strong> for emphasis and <em> for the punchline.
  </p>
  <p class="azure-plant">
    Optional plant for next layer. Used sparingly — only when planting a pin for a future payoff.
  </p>
</div>
```

### Image sizing rule (LOCKED — common mistake)

Inside `.net-wrap object` (or any image element):

```css
.net-wrap object {
  max-width: 100%;
  max-height: 440px;
  width: auto;       /* ← critical */
  height: auto;      /* ← critical */
  display: block;
}
```

**NEVER use `width: 100%`** — it stretches the image and breaks aspect ratios. Always use `max-width: 100%` with `width: auto`.

### SVG asset rule (LOCKED)

Every SVG used as an asset must include an explicit dark-background rect as the first element after `</defs>`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 500" ...>
  <defs>...</defs>
  <rect x="0" y="0" width="920" height="500" fill="#1a1a1d"/>
  <!-- visual content here -->
</svg>
```

This is because some browsers don't inherit the container's background through `<object>` embedding.

### Animation
- Beat transitions: 200ms fade-in only. No slide, no zoom.
- Within-beat reveals (e.g. animated table rows): 360ms ease, staggered by 320ms per row.

## JavaScript conventions

### MODULE config block

Each HTML file declares a single `MODULE` object near the top of the script:

```javascript
const MODULE = {
  layer: 4,                              // module number
  name: "Server Computer",               // display name
  targetSeconds: 44 * 60,                // CUMULATIVE seconds from start of training
  beatLabels: [                          // human-readable labels per beat (for log)
    "Title",
    "The question (designed for the network)",
    "What a server looks like (real photo)",
    // ... one per beat
  ]
};
```

**`targetSeconds` is cumulative** — end of Layer 4 = 44 min from the start of the training, not from the start of Layer 4. This is how the shared timer warns the speaker when they're running long.

### Shared localStorage keys (LOCKED — DO NOT RENAME)

All HTML files in this training share these keys so the timer and log persist across files:

```javascript
const LS_LOG          = "cloud_training_log";          // session events
const LS_START        = "cloud_training_start";        // ms epoch when training started
const LS_PAUSED_AT    = "cloud_training_paused_at";    // ms epoch when paused (if paused)
const LS_PAUSE_OFFSET = "cloud_training_pause_offset"; // total ms paused so far
```

The prefix `cloud_training_` is the training's namespace. If forking this template for a different training, change the prefix everywhere (one find/replace).

### Beat navigation

```javascript
// State
let idx = 0;                                       // current beat index (0-based)
const beats = document.querySelectorAll(".beat");

// Show beat by index
function showBeat(i) {
  beats.forEach((b, n) => b.classList.toggle("active", n === i));
  document.getElementById("step-counter").textContent =
    `Beat ${i + 1} of ${beats.length}`;
  // Update next-button label on last beat
  const nextBtn = document.getElementById("next-btn");
  nextBtn.textContent = i === beats.length - 1
    ? `End of Layer ${MODULE.layer}`   // or "End of training 🎓" for final module
    : "Next →";
  // Update speaker notes panel
  renderNotes(i);
}

// Navigation handlers (Back / Next)
document.getElementById("next-btn").addEventListener("click", () => {
  if (idx < beats.length - 1) {
    idx++;
    showBeat(idx);
    const label = MODULE.beatLabels[idx] || `Beat ${idx + 1}`;
    logEvent("→", `L${MODULE.layer} · ${label}`);
  }
});
```

### Speaker notes

Notes are declared as an array parallel to the beats:

```javascript
const NOTES = [
  {
    title: "Beat 1 — Title (~15 sec)",
    body: "Quick landing. Read the subtitle aloud. Click Next."
  },
  {
    title: "Beat 2 — The setup (~75 sec)",
    body: "<strong>Open with the callback (~20 sec):</strong> '...'..."
  },
  // ... one entry per beat
];
```

The note for beat `idx` is rendered into `#notes-content` whenever the beat changes. HTML allowed inside `body` for emphasis, lists, and pre-formatted instructional structure.

### Timer

The timer fires every second:

```javascript
function tickTimer() {
  const start = getStart();
  if (!start) return;
  const offset = getPauseOffset();
  const elapsedMs = Date.now() - start - offset;
  const elapsed = Math.floor(elapsedMs / 1000);

  document.getElementById("elapsed-time").textContent = fmtMinSec(elapsed);
  document.getElementById("target-time").textContent = fmtMinSec(MODULE.targetSeconds);

  const diff = MODULE.targetSeconds - elapsed;  // positive = ahead, negative = behind
  const diffEl = document.getElementById("time-diff");
  if (diff > 0) {
    diffEl.textContent = `${fmtMinSec(diff)} ahead`;
    diffEl.className = "ahead";
  } else if (diff < 0) {
    diffEl.textContent = `${fmtMinSec(-diff)} behind`;
    diffEl.className = "behind";
  } else {
    diffEl.textContent = "on time";
    diffEl.className = "on-time";
  }
}

setInterval(tickTimer, 1000);
```

### Session log

Every navigation event is logged with a timestamp. The log persists in `localStorage` across modules:

```javascript
function logEvent(symbol, text) {
  const arr = loadLog();
  arr.push({
    t: Date.now(),
    sym: symbol,
    text: text,
    layer: MODULE.layer
  });
  saveLog(arr);
  refreshLogPanel();
}
```

Use these symbols consistently:
- `→` forward navigation
- `←` back navigation
- `⏵` session start
- `⏸` paused
- `⏹` reset
- `📝` notes opened

## When building a new module

The full workflow:

1. **Copy the canonical template** — Layer 2's HTML (`2_operating_system.html`) is the cleanest base. Copy it as `{N}_{slug}.html`.

2. **Create the assets folder** — `mkdir {N}_{slug}_assets/`.

3. **Update the page title** — `<title>Cloud Training — {Module Name}</title>`.

4. **Update the header** — `<h1>Cloud Training Roadmap — {Module Name}</h1>` and `<span class="module-tag">Layer {N} · ~{X} minutes</span>`.

5. **Update beat counter** — `<span id="step-counter">Beat 1 of {total beats}</span>`.

6. **Update end-of-module button** — `idx === beats.length - 1 ? "End of Layer {N}" : "Next →"`.

7. **Update MODULE config**:
   ```javascript
   const MODULE = {
     layer: N,
     name: "{Module Name}",
     targetSeconds: {cumulative_minutes} * 60,
     beatLabels: ["Title", "...", "Handoff to Layer {N+1}"]
   };
   ```

8. **Replace the stage block** — write each `<div class="beat" data-beat="K">` with its visual reference, caption, and (for handoff beats) plants.

9. **Replace the NOTES array** — write one entry per beat with `title` and `body` (HTML allowed in body).

10. **Build the SVG assets** — one per content beat. Use the dark `#1a1a1d` background rect, the module's color family, and `viewBox="0 0 920 H"` (typical heights 460-580).

11. **Sanity check** — verify every `data-beat` matches its position, every SVG ref resolves to a file, MODULE.beatLabels length matches the beat count.

12. **Zip the deliverable** — `zip -qr cloud_training_layer{N}.zip {N}_{slug}.html {N}_{slug}_assets/`.

## What NOT to do

- ❌ **No external dependencies.** No CDN, no `<link>` to stylesheets, no `<script src>`, no fonts beyond system stack.
- ❌ **No build step.** No bundlers, no transpilation, no preprocessors.
- ❌ **No frameworks.** No React, no Vue, no Alpine, no anything.
- ❌ **No `width: 100%`** on images — use `max-width: 100%; width: auto`.
- ❌ **No SVG without an explicit dark background rect** as the first drawn element.
- ❌ **No relying on container background** in embedded `<object>` SVGs.
- ❌ **No light-mode CSS** — dark only.
- ❌ **No animations** beyond the locked fade-in / stagger pattern.
- ❌ **No `localStorage` keys without the `cloud_training_` prefix** (or the equivalent per-training namespace).
- ❌ **No more than 9 beats** per module — pedagogical density caps here.
- ❌ **No mid-sentence bolding** in captions and notes outside `<strong>`/`<em>`.
- ❌ **No emoji except the few load-bearing ones** (🎓 for end-of-training, 📋 for log button, 📝 for notes log entry, →/←/⏵/⏸/⏹ for log symbols).

## Quick test before delivering

```bash
# 1. File opens by double-click (cd to outputs dir, open the .html in a browser)
# 2. Beat counter shows correct N
# 3. Every Next click advances the visual
# 4. Speaker notes panel shows the current beat's note
# 5. Timer increments
# 6. Reset clears localStorage and starts over
# 7. Open another module in a new tab — timer state persists
```

## Common pitfalls (each has cost time in this project)

1. **`data-beat` ≠ counter number.** `data-beat="3"` is shown as "Beat 4 of N". Plan for this offset when speaking and writing notes.
2. **MODULE.beatLabels length must match beat count.** Off-by-one is silent — log just shows "Beat N" instead of label.
3. **`targetSeconds` is cumulative.** If Layer 4 ends at minute 44 of training, its `targetSeconds` is `44 * 60`, not `10 * 60`.
4. **SVG `<object>` doesn't inherit container background.** Always include the inner background rect.
5. **Long captions overflow inside narrow beats.** Keep captions ≤ 2 lines (~140 characters), put richness in speaker notes.
6. **Adding new pin/payoff requires updating the inventory.** When extending, plant pins early, pay them off late, document both.
