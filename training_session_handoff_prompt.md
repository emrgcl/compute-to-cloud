# Cloud Training Roadmap — Session Handoff Prompt

> Copy everything below the line into a new Claude session to resume this work. If you have the `cloud-training-walkthrough` skill installed, that's the preferred path — reference it explicitly.

---

I'm preparing a 90-minute cloud infrastructure training. I want to continue work we started in previous sessions. Use the `cloud-training-walkthrough` skill if it's installed. Here's the full context:

## Audience

- **High school students** on a CS track — their school prepares them for industry.
- Floor: competent computer users. They've seen variables/loops, basic OS use, maybe touched Linux in a lab, know what RAM is.
- They have **not** seen: a rack server in person, a hypervisor, anything cloud, anything enterprise.
- Treat them as "competent computer users who've never seen a datacenter."
- They will **watch only** — no laptops, no hands-on. I do all demos.

## Format

- **90 minutes, single session.**
- Language: **English first**, I'll translate to Turkish later.
- Final deliverable: **single-file HTML walkthrough per layer** — standalone, opens by double-click, step-through controls, screen-recordable for class. Dark theme. Inherits a shared session timer + event log via `localStorage` across all modules. Use **Excalidraw** for the heavier visual moments where a hand-drawn diagram earns its place. Not every layer needs Excalidraw — only where it carries the lesson.

## The 7-layer roadmap (locked)

A roadmap SVG already exists with these 7 layers (each a separate module):

1. **Computer** — CPU, RAM, storage, motherboard, PSU. Physical hardware that executes instructions.
2. **Operating System** — kernel, system calls, scheduling, memory mgmt, file system. The kernel-as-heart framing.
3. **Networking** — IP, subnet, port, public vs. private, firewall. How computers find and talk to each other. Terminates at a VNet/subnet/NSG preview that sets up Layer 7.
4. **Server Computer** — what makes a server physically different from a laptop (rack form, redundant PSU, ECC RAM, multi-socket CPU, more disks/NICs, BMC/iLO/iDRAC).
5. **Server OS** — *requirements-driven framing*: what does a server NEED from its OS that a desktop doesn't? Headless boot, services/daemons, remote management (SSH/RDP), uptime, no-human-present. Windows Server + Linux Server as anchors.
6. **Virtualization** — Type 1/2 hypervisor, VMs, Hyper-V/VMware, containers. One physical server → many isolated VMs. Exploits the privilege boundary planted in Layer 2.
7. **Azure** — IaaS, Azure VM, regions & AZs, VNet, NSG, storage, portal. Virtualization at hyperscale as a managed service. **Live demo here** (instructor deploys a VM in front of students). **Includes a required mapping-table beat** showing Layer 3 networking concepts → Azure terminology.

## Time budget (locked)

| Layer | Min | Notes |
|---|---|---|
| 0 — Intro/hook | 5 | Why this matters, what they'll explain at the end |
| 1 — Computer | 8 | Fast review, anchor terminology (CPU/RAM/disk/network as roles) |
| 2 — OS | 10 | Built at ~10:20. Kernel-as-heart + system calls + policy machine |
| 3 — Networking | 8 | **Next to build.** IP/subnet/port/firewall; plants Azure vocabulary as asides |
| 4 — Server computer | 12 | What makes a server different from a laptop |
| 5 — Server OS | 10 | The mental shift — requirements-driven framing |
| 6 — Virtualization | 16 | **Conceptual heavy lift.** The hinge of the whole talk |
| 7 — Azure | 16 | Payoff: hyperscale virtualization + Layer 3→Azure mapping table + live demo |
| Wrap / Q&A | 5 | Recap the through-line |

## The through-line (anchor for the whole talk)

> *"Azure isn't magic. It's the same computer you have at home, plus five ideas stacked on top: a stronger version of it, an OS that runs without a screen, a way to talk to other computers, a way to slice one into many, and someone else owning the building."*

If students leave with that sentence, the talk worked.

## Two cross-module patterns to preserve

1. **Layer 3 plants Azure vocabulary casually.** When introducing each networking concept, drop the Azure name as an aside ("This is a subnet. In Azure they call it... a subnet."). Light touch — one sentence per concept. Sets up triple-exposure for retention.
2. **Layer 7 has a required mapping-table beat** right before the live demo. Side-by-side: Layer 3 concept → Azure name. Makes the demo feel like recognition instead of vocabulary.

## Pin inventory (what's planted, where it pays off)

| Plant | Module | Paid off in |
|---|---|---|
| "Four roles" (CPU/RAM/storage/network) | Layer 1 beat 3 | Layer 2 beat 5 (four jobs table reuses them) |
| "Virtual machine has the four roles too — but isn't a machine" | Layer 1 beat 3 PIN | Layer 6 |
| "Eight milestones — we'll come back at the end" | Layer 1 beat 4 | Layer 7 closer |
| "System call" vocabulary | Layer 2 beat 3 | Layer 6 (hypervisors intercept syscalls) |
| "CPU enforces privilege boundary" | Layer 2 beat 3 | Layer 6 (virtualization exploits this) |
| "Programs never touch hardware directly" | Layer 2 beat 3 | Layer 6 ("hardware" can be faked) |
| "Same heart, different bodies" / "policy machine" | Layer 2 beat 7 PIN | Layer 5 (server OS persona) |
| "And one more thing — the network" | Layer 2 beat 8 handoff | Layer 3 opens with this |

## Workflow

1. **Discuss each layer first.** Propose: learning objectives, 3–5 concepts that earn their place in the time budget, the one visual that carries the lesson, what we deliberately drop. I react, push back, we iterate, lock.
2. **Then build.** Single-file HTML walkthrough per module using the `cloud-training-walkthrough` skill conventions. Use Excalidraw inside where a hand-drawn diagram earns its place.
3. PPTX deck and Turkish translation come *after* all the HTML walkthroughs are right.

## Output style I want

- Produce artifacts over explanations. Skip preamble.
- Be dense and actionable.
- **Push back on pedagogically questionable ideas before building.** I value the honest critique.
- Don't anchor general infra answers to my work projects (zerlog, Koczer, Enerjisa, Domino's) unless I explicitly ask.
- Follow the `cloud-training-walkthrough` skill conventions (single file per module, per-module assets folder, dark theme matched to existing modules, asset filenames prefixed with module number).

## Engineering conventions (locked)

- **Asset folder per module:** `{N}_{name}_assets/` next to `{N}_{name}.html`
- **Asset filename convention:** `{N}_beat{M}_{name}.{ext}` — module-number prefix, beat-number to identify where it belongs. Example: `2_beat1_programs_to_cpu.svg`, `2_beat3_kernel_heart.svg`, `2_beat5_activity_monitor.png`.
- **Shared session timer + event log** across all modules via `localStorage` (keys prefixed `cloud_training_`). Each module's `MODULE.targetSeconds` is *cumulative* (Layer 0 = 5*60, Layer 1 = 13*60, Layer 2 = 23*60, Layer 3 = 31*60, etc).
- **Color family per layer:** 1–2 gray (personal computing), 3–5 green (networking/enterprise), 6 purple (virtualization), 7 blue (Azure).
- **Hard-reload reminder** (Cmd+Shift+R) after any SVG/HTML change. Safari caches aggressively.
- **No CDN, no build step.** Hand-coded HTML/CSS/JS. Syntax-coloring done with inline spans.
- **Beat patterns reused:** animated row-fade tables (data-delay attribute, ~320ms stagger), PIN boxes (purple), amber emphasis on key terms, plain-stage handoff beats.
- **Image sizing pattern:** for raster screenshots use `max-width: 100%; max-height: {H}px; width: auto; height: auto; display: block;` — NOT `width: 100%`, which forces stretching.

## Where we are right now

**Status as of this checkpoint:**

- ✅ **Layer 0 (Intro)** — built, locked. `0_intro.html` + `0_intro_assets/`. 7 beats, ~5 min.
- ✅ **Layer 1 (Computer)** — built, locked. `1_computer.html` + `1_computer_assets/`. 6 beats, ~8 min. Real specs locked: Apple II (1 MHz/4 KB/cassette/$1,298), IBM PC (4.77 MHz/16 KB/160 KB floppy/$1,565), 2026 monster (~5 GHz·8 cores/32 GB/2 TB NVMe with ~8,000×/~2M×/~12.5M× multipliers).
- ✅ **Layer 2 (OS)** — built, locked. `2_operating_system.html` + `2_operating_system_assets/`. 9 beats, ~10:20. Slight over-budget acknowledged by Emre, who said he'd manage the time.
- 🔨 **Layer 3 (Networking)** — **NEXT.** Draft spec from earlier session: 6 beats, ~8 min, covering IP/subnet/port/private-vs-public/firewall. Plants Azure vocabulary as asides. Terminates at VNet/subnet preview setting up Layer 7. **Discuss before building.**
- ⏳ Layers 4, 5, 6, 7 — pending.

## Layer 2 design summary (so it doesn't drift)

The 9 beats:

| # | Beat | Time | Visual |
|---|---|---|---|
| 0 | Title — "The coordinator you've never met" | 15 sec | Plain |
| 1 | The problem — who decides which program runs? | 75 sec | SVG: programs → 8-core CPU |
| 2 | CPU vocabulary — "1,500 instructions" + C↔asm addition example | 90 sec | Side-by-side code, syntax-colored |
| 3 | The heart — sandbox, system call, CPU enforces privilege | 105 sec | Excalidraw-style flow: code → syscall → kernel → hardware |
| 4 | The wall — hello world explodes; `printf → write` system call reveal | 70 sec | C↔asm side-by-side with `...` ellipsis + `write(1, ..., 14)` callout |
| 5 | Four jobs — animated table (scheduling/memory/file/network) | 120 sec | Animated 4-row table, Layer 1 callback |
| 6 | EKG — real Windows Task Manager screenshot from Emre's laptop | 75 sec | Real Task Manager (16% CPU, 54% memory, 21 apps including Claude with 13 processes) |
| 7 | Policy machine — same heart, different bodies; plants Layer 5 | 50 sec | 2-column table + PIN box |
| 8 | Handoff — "...and one more thing: the network" | 30 sec | Empty stage |

**Pedagogical choices made (don't reverse without reason):**
- Kernel as *heart*, not translator or broker (Emre's framing, more visceral)
- System call shown as actual C code: `write(1, "Hello, world!\n", 14)` with `write` highlighted purple — not just spoken about
- Honest caveat: "printf is a library function, write IS the system call"
- "Stop your heart, you die. Stop the kernel, your computer freezes." — the keeper line
- "CPU itself enforces the rule" — explicit Layer 6 setup
- Syntax-colored code blocks via hand-rolled spans (no library): keywords amber, strings green, numbers purple, instructions white-bold, registers cyan, system calls purple-highlighted

**MODULE config in Layer 2 HTML:**
```js
{ layer: 2, name: "OS", targetSeconds: 23 * 60, beatLabels: [...9 labels...] }
```

## Layer 3 (Networking) — starting spec to refine, NOT to build yet

This is a starting point for discussion, not a locked design. Discuss and iterate before building.

**Time budget:** 8 minutes. **Cumulative target:** 31 min (`MODULE.targetSeconds: 31 * 60`).

**Core pedagogical move:** Layer 2 ended with "and one more thing — the network." Layer 3 opens by answering that. The lesson: **networking is just two computers talking, structured by a small number of rules.**

**Proposed 6 beats (~8 min):**

| # | Beat | Time | Idea |
|---|---|---|---|
| 0 | Title — "How computers find each other" | 15 sec | Settle |
| 1 | The problem — your laptop wants to talk to a server somewhere | 75 sec | Frame the question. There are billions of computers — how does yours find a specific one? |
| 2 | IP address as a phone number — every computer has one | 75 sec | IPv4 dotted notation. Public vs private (private = lives behind your router). Plant: "in Azure, this is just an IP address." |
| 3 | Subnet — neighborhoods | 90 sec | Group of computers that can reach each other directly. Plant: "in Azure they call it a Subnet" |
| 4 | Port + firewall — apartment numbers + the doorman | 90 sec | One IP can host many services; ports route to the right one. Firewall = allow/deny rules. Plant: "in Azure firewall rules are called NSG — Network Security Group" |
| 5 | Putting it together — the inside of a private network | 60 sec | Diagram: many computers in subnets, gateway out to internet, firewall guarding the door. Preview: "this exact shape is what we'll deploy in Azure" |
| 6 | Handoff — "Two computers can talk. But what does the OTHER computer look like?" | 30 sec | Bridge to Layer 4 (Server Computer) |

**Azure vocabulary planted (light touch, one mention each):**
- IP address → "in Azure: just IP address"
- Subnet → "in Azure: Subnet"
- Firewall → "in Azure: NSG (Network Security Group)"
- Private network → "in Azure: VNet (Virtual Network)"

Each plant is **one sentence**, said quickly, no fanfare. This is the *first* of three exposures (Layer 3, then Layer 7 mapping table, then Layer 7 demo).

**Visual centerpiece** (beat 5): a small private network diagram with 3-4 computers inside a subnet, a router/gateway box, an arrow to "the internet", and a firewall icon. The *exact same shape* will appear in Layer 7's mapping-table beat — same diagram with Azure labels overlaid. The recognition moment is the payoff.

**What deliberately drops:**
- ❌ IPv6 — mentioned as a one-liner if asked, not on slide
- ❌ DNS resolution mechanics — "names map to IPs" suffices, no NS records/recursion
- ❌ TCP vs UDP — irrelevant to the cloud story
- ❌ OSI 7-layer model — academic, no payoff for Azure
- ❌ MAC addresses, ARP, switching — wrong abstraction layer
- ❌ Routing protocols (BGP, OSPF) — way too deep
- ❌ NAT mechanics — handled implicitly via "private IPs live behind your router"

**Discussion questions to raise before building:**
1. Is "phone number" the right metaphor for IP, or want something else?
2. Is "neighborhoods" the right metaphor for subnet, or want a different framing?
3. The 4 Azure vocabulary plants (IP / Subnet / NSG / VNet) — too many, too few, or right?
4. Beat 5's diagram — Excalidraw, or hand-coded SVG?
5. Where in Layer 3 do we plant "two computers talking implies one is a server" — set up Layer 4 explicitly, or let it be implicit?

## How to resume

**If picking up at Layer 3:** Start by proposing/refining the Layer 3 spec above. Don't build until I sign off. Reference Layer 2's beat 8 handoff — that's the question Layer 3 opens with.

**If picking up at a Layer 2 polish task:** The file is `/mnt/user-data/outputs/2_operating_system.html`. Assets in `/mnt/user-data/outputs/2_operating_system_assets/`. The zip is `/mnt/user-data/outputs/cloud_training_layer2.zip`.

**If picking up to build a new module from spec:** Copy Layer 2's HTML as the base (it has the most recent template with the cumulative timer, 9-beat structure pattern, and asset-prefix convention). Rename, replace beats, update MODULE config, update NOTES array, update beat-row fade-in trigger if needed. Rename all assets with the new module-number prefix.

## File locations

- Working dir for outputs: `/mnt/user-data/outputs/`
- HTML files: `0_intro.html`, `1_computer.html`, `2_operating_system.html`
- Asset folders: `0_intro_assets/`, `1_computer_assets/`, `2_operating_system_assets/`
- Zips delivered to user: `cloud_training_layer0.zip`, `cloud_training_layer1.zip`, `cloud_training_layer2.zip`
- This handoff: `training_session_handoff_prompt.md`
- Skill package: `cloud-training-walkthrough.skill` and `/home/claude/cloud-training-walkthrough/`
