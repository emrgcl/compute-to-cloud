# Cloud Training Walkthrough — Project Context

This is a 90-minute cloud computing training for Turkish high-school CS-track students. The deliverable is **eight self-contained HTML files**, one per layer, each opening with a double-click in a browser and presenting a beat-by-beat walkthrough Emre delivers as a screen-recorded lecture.

## Audience

- **Turkish high-school CS-track students** at an industry-prep school.
- **Sharp but tired** — the talk runs ~90 minutes; attention is finite.
- **Watching only** — no laptops in front of them, no exercises during.
- **English first**, Turkish translation later.

## Through-line

The whole training is anchored by one sentence:

> *Azure isn't magic. It's the same computer you have at home, plus five ideas stacked on top: a stronger version of it, an OS that runs without a screen, a way to talk to other computers, a way to slice one into many, and someone else owning the building.*

This sentence is **introduced in Layer 0 verbatim** and **restated in Layer 7 beat 8 verbatim**. Layers 1-6 fill in each of the five "plus" clauses. Layer 7 synthesizes.

## The seven layers

| # | Module | Status | Time | Cumulative |
|---|---|---|---|---|
| 0 | Intro / hook | ✅ Built | ~5 min | 5 |
| 1 | Computer (five physical things) | ✅ Built | ~8 min | 13 |
| 2 | Operating System (the coordinator) | ✅ Built | ~10 min | 23 |
| 3 | Networking (how computers find each other) | ✅ Built | ~11 min | 34 |
| 4 | Server Computer (a stronger version) | ✅ Built | ~10 min | 44 |
| 5 | Server OS (an OS without a screen) | ✅ Built | ~10 min | 54 |
| 6 | Virtualization (slice one into many) | ✅ Built | ~11 min | 65 |
| 7 | Azure (someone else owning the building) | ✅ Built | ~17 min | 82 |

**Total budget: 90 min. Built: ~80 min. Headroom: ~10 min for Q&A.**

## File structure

```
/mnt/user-data/outputs/
├── 0_intro.html                        ← double-click to open
├── 0_intro_assets/                     ← SVG and PNG assets per layer
│   ├── 0_beat2_*.svg
│   └── ...
├── 1_computer.html
├── 1_computer_assets/
├── ... (through layer 7)
├── 7_azure.html
├── 7_azure_assets/
└── cloud_training_layer{0..7}.zip      ← one zip per delivered layer
```

**Asset naming convention (locked):**
- `{layer}_{beat-counter}_{slug}.{ext}`
- `beat-counter` is what the student sees on screen (1-indexed), NOT the `data-beat` attribute (0-indexed). The counter and the data-beat are deliberately off by one.
- Example: `6_beat7_three_questions.svg` is the SVG for the beat showing as "Beat 7 of 9" on screen, but its HTML element has `data-beat="6"`.

## Layout pattern (locked)

See `cloud-training-html-styling.md` for the full spec. Summary:

- **Dark theme**, no light-mode toggle.
- **Stage block** holds 8-9 beats per layer, only one visible at a time.
- **Beat navigation:** Back / Next buttons, optional Speaker Notes panel, Log panel for session recording.
- **Shared session timer** across all 8 HTML files via `localStorage` (so Emre can navigate between layers and the timer keeps running cumulative time).
- **Color families per layer:**
  - Layers 1-2: gray (foundation)
  - Layers 3-5: green (server/network)
  - Layer 6: purple (virtualization)
  - Layer 7: blue (Azure / cloud)
- **No CDN, no build step.** Pure hand-coded HTML/CSS/JS, opens by double-click.
- **No frameworks.** Vanilla JS only.

## Working style Emre wants

These are the conventions that emerged through 7 layers of iteration. They are durable preferences, not arbitrary.

1. **Push back on questionable pedagogical moves *before* building, not silently comply.** If a beat structure feels off, say so first. If a metaphor is doing too much (or too little), flag it.

2. **Confirm before building** when something seems off. Don't assume.

3. **Match the counter number when Emre references a beat.** He says "Beat 4" meaning what the student sees on screen, not `data-beat="3"`.

4. **Don't anchor general infra answers to his customer projects** unless explicitly asked. He works with many clients; the training is generic high-school content.

5. **Emre is a Microsoft employee.** Avoid quoting Linux-vs-Windows market share, vendor comparisons that could land wrong, or "Azure beats AWS" framing. Stay neutral on competitive positioning. Honest pluralism is fine when relevant.

6. **He cares about pedagogical density.** Every beat must earn its time. Every pin planted must pay off later. Every callback must be intentional.

7. **Plants and payoffs are load-bearing.** The training works because pins planted in Layers 1-2 pay off in Layers 5-7. A beat is "good" if it pays off a pin or plants one for later.

8. **Read SKILL.md files before working.** When code-execution tools are available, check the available_skills block first and view relevant SKILL.md files before writing anything.

## Pin inventory (planted and paid off)

| Pin | Origin | Paid off in |
|---|---|---|
| "A virtual machine has the four roles too, but isn't a machine" | Layer 1 beat 3 | Layer 6 beat 7 (explicit callback) |
| "Programs never touch hardware directly" | Layer 2 beat 3 | Layer 6 beat 3 ("now we do it to the OS") |
| "CPU enforces the privilege boundary" | Layer 2 beat 3 | Layer 6 beat 5 (CPU enforces VM isolation) |
| "Same kernel concept, different bodies" (policy machine) | Layer 2 beat 7 | Layer 5 beat 2 (right column filled in) |
| "Designed for failure — components fail, system runs" | Layer 4 beat 5 | Layer 6 beat 7 (portability/live migration) |
| "Kernel isolation, just stretched" | Layer 5 beat 6 | Layer 6 beat 5 (same mechanism, bigger boxes) |
| "What if hardware could be faked?" | Layer 5 beat 8 handoff | Layer 6 entire module |
| "Hypervisor at hyperscale" | Layer 6 beat 9 handoff | Layer 7 beat 2 opens with this |
| "Charged by the minute" | Layer 6 beat 9 | Layer 7 beat 5 economic model |
| "Anyone can rent with a credit card" | Layer 6 beat 9 | Layer 7 beat 5 |
| "~400 datacenters worldwide" | Layer 4 beat 7 | Layer 7 beat 2 (scale ladder reuse) |
| "SSH/RDP" remote access | Layer 4 beat 6 | Layer 7 demo + debrief |
| "Windows Server or Linux?" | Layer 5 beat 7 | Layer 7 demo image picker |
| **Layer 0 promise sentence (five ideas stacked)** | Layer 0 | **Layer 7 beat 8 — restated verbatim** |

## Locked design decisions

- **Color families per layer** as above. Do not deviate.
- **Asset naming `{layer}_{beat-counter}_{slug}.{ext}`** with beat-counter as the 1-indexed user-visible number.
- **MODULE.targetSeconds is cumulative**, not per-layer. End of Layer 4 = 44 min from training start.
- **Beat label `End of Layer N`** on the Next button at the last beat (except Layer 7 which says `End of training 🎓`).
- **Image sizing pattern:** `max-width: 100%; max-height: Hpx; width: auto; height: auto; display: block;` — **NEVER** `width: 100%` (breaks aspect ratio).
- **SVG dark background:** explicit `<rect fill="#1a1a1d">` as first element after `</defs>` (don't rely on container).
- **Layer 2 HTML is the canonical template** for new modules — it has the cleanest CSS and the most reusable structure.
- **No share-of-market numbers** for Linux vs Windows Server (Microsoft-employee constraint).
- **Live demo** (Layer 7 beat 6) is the riskiest beat. Speaker notes contain a full ~8-min script as fallback. Pre-recorded backup video recommended.

## Pedagogical principles (the rules that emerged)

1. **One beat = one job.** If a beat is doing two pedagogical jobs, split it.
2. **Visual + caption + speaker note do different jobs.** Visual = anchor. Caption = the keeper sentence. Notes = the delivery script.
3. **Concrete before abstract.** Always introduce a concrete example before the conceptual generalization.
4. **Repeat the pattern, not the explanation.** If a structure works for one row/example, repeat it. Students learn by recognizing patterns, not by being told the rule.
5. **Plants must pay off.** A pin without a payoff is wasted teaching budget.
6. **Cuts are an act of respect for the audience.** Every minute trimmed is a minute they don't have to endure something boring.

## How to resume / extend this project

If picking up where this left off:

1. **All 8 modules are built and zipped.** Files in `/mnt/user-data/outputs/`.
2. **Speaker notes are inside each HTML file** — open the "Speaker notes" panel button.
3. **Test by opening any `.html` file by double-clicking** — should work offline.
4. **To revise a layer:** edit the HTML directly (str_replace works fine for small edits), or regenerate beats. The Layer 2 HTML is the cleanest template to copy.
5. **To extend with new layers / variants:** copy Layer 2 as base, change MODULE config (layer number, name, targetSeconds, beatLabels array), replace stage block, replace NOTES array.
6. **To translate to Turkish:** captions and speaker notes are the translation targets. SVG text would need to be translated separately (most is English now). Headers, button labels, MODULE.beatLabels are also visible-to-student strings.

## What NOT to do

- ❌ Don't introduce new concepts without anchoring to a Layer 1-6 pin.
- ❌ Don't use share-of-market numbers, vendor-vs-vendor comparisons, or sales framing.
- ❌ Don't add features Emre didn't ask for (extra animations, sound, etc.).
- ❌ Don't quote song lyrics, copyrighted images, or character likenesses in any SVG.
- ❌ Don't add more than 8-9 beats per module — pedagogical density caps at ~10.
- ❌ Don't lean on metaphors that have to be set up before they pay off (the apartments metaphor in Layer 6 was deliberately removed for this reason).
- ❌ Don't reach for the Excalidraw tool, the visualize widget, or external services — the deliverable is offline-first HTML.

## See also

- `cloud-training-html-styling.md` — the full HTML/CSS/JS spec for the beat-walkthrough layout. Reference this when building or revising layers.
- Skills `timeline-svg`, `html-diagram`, `emre-profile` live at `/mnt/skills/user/` for related visual conventions.
