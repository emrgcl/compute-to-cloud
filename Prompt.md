# Cloud Training Roadmap — Session Handoff Prompt

> Copy everything below the line into a new Claude session to resume this work.

---

I'm preparing a 90-minute cloud infrastructure training. I want to continue work we started in a previous session. Here's the full context:

## Audience

- **High school students** on a CS track — their school prepares them for industry.
- Floor: competent computer users. They've seen variables/loops, basic OS use, maybe touched Linux in a lab, know what RAM is.
- They have **not** seen: a rack server in person, a hypervisor, anything cloud, anything enterprise.
- Treat them as "competent computer users who've never seen a datacenter."
- They will **watch only** — no laptops, no hands-on. I do all demos.
## Format

- **90 minutes, single session.**
- Language: **English first**, I'll translate to Turkish later.
- Final deliverable: **single-file HTML walkthrough** (using the `html-diagram` skill — standalone, opens by double-click, step-through controls, screen-recordable for class). Use **Excalidraw** for the heavier visual moments where a hand-drawn diagram earns its place (e.g., hypervisor splitting one server into VMs, Azure region/AZ topology). Not every layer needs Excalidraw — only where it carries the lesson.
## The 6-layer roadmap

A roadmap SVG already exists with these layers (each a separate module):

1. **Computer** — CPU, RAM, storage, motherboard, PSU. Physical hardware that executes instructions.
2. **Operating System** — kernel, processes, memory management, file system, CLI. Software layer that manages hardware resources.
3. **Server Computer** — what makes a server physically different from a laptop (rack form, redundant PSU, ECC RAM, multi-socket CPU, more disks/NICs, BMC/iLO/iDRAC).
4. **Server OS** — Windows Server / Linux Server: headless, services/daemons, remote management, no GUI by default.
5. **Virtualization** — Type 1/2 hypervisor, VMs, Hyper-V/VMware, containers. One physical server → many isolated VMs.
6. **Azure** — IaaS, Azure VM, regions & AZs, VNet, storage, portal. Virtualization at hyperscale as a managed service. **Live demo here** (instructor deploys a VM in front of students).
## Time budget (locked)

| Layer               | Min | Notes                                                       |
| ------------------- | --- | ----------------------------------------------------------- |
| 0 — Intro/hook      | 5   | Why this matters, what they'll explain at the end           |
| 1 — Computer        | 8   | Fast review, anchor terminology (CPU/RAM/disk as roles)     |
| 2 — OS              | 10  | Review + introduce "OS as resource manager" framing         |
| 3 — Server computer | 12  | **New ground**: what makes a server different from a laptop |
| 4 — Server OS       | 10  | Headless, services, remote management — the mental shift    |
| 5 — Virtualization  | 20  | **Conceptual heavy lift**. The hinge of the whole talk.     |
| 6 — Azure           | 20  | Payoff: hyperscale virtualization + live demo               |
| Wrap / Q&A          | 5   | Recap the through-line                                      |

## The through-line (anchor for the whole talk)

> _"Azure isn't magic. It's the same computer you have at home, plus four ideas stacked on top: a stronger version of it, an OS that runs without a screen, a way to slice one into many, and someone else owning the building."_

If students leave with that sentence, the talk worked.

## Workflow we agreed on

1. **Discuss each layer one at a time.** For each: learning objectives, 3–5 concepts that earn their place in the time budget, the one visual that carries the lesson, what we deliberately drop. I react, we lock it, move on.
2. **After all 6 layers are locked**, build the single-file HTML walkthrough using the `html-diagram` skill. Use Excalidraw inside it where a hand-drawn diagram earns its place.
3. PPTX deck and Turkish translation come _after_ the HTML walkthrough is right.

## Where we are right now

[ Update this section when you copy the prompt. Examples: ]

- _"We just locked the audience/format/timing. Start with Layer 1 — Computer. Propose the 3–4 learning objectives, the concepts that earn their place in 8 minutes, the one visual that carries the lesson, and what we deliberately drop."_
- _"Layers 1–3 are locked (notes attached). Start Layer 4 — Server OS."_
- _"All 6 layers locked. Build the HTML walkthrough now."_

## Output style I want

- Produce artifacts over explanations. Skip preamble.
- Be dense and actionable.
- Don't anchor general infra answers to my work projects (zerlog, Koczer, Enerjisa, Domino's) unless I explicitly ask.
- For the HTML walkthrough, follow the `html-diagram` skill conventions (single file, no build step, no CDN, double-click-to-run, UTF-8 declared, system fonts only).