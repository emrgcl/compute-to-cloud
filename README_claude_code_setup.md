# Cloud Training — Claude Code Setup

Two files for your Claude Code project root:

## `CLAUDE.md`

Project context Claude Code reads on every session. Captures:
- The audience (Turkish high-school CS-track students)
- The 7-layer through-line and current build state
- Working conventions and pedagogical principles
- Pin inventory (plants and payoffs)
- Locked design decisions
- What NOT to do

Place at the repo root so Claude reads it automatically.

## `cloud-training-html-styling.md`

Standalone styling/conventions reference for the HTML layout. Two ways to use it:

**Option A — Inline reference:** keep alongside `CLAUDE.md` and reference it from there ("see `cloud-training-html-styling.md` for the full HTML/CSS/JS spec").

**Option B — Convert to a skill:** rename to `SKILL.md`, place at `.claude/skills/cloud-training-walkthrough/SKILL.md`, and Claude will load it on relevant triggers (creating/revising training layers). The YAML frontmatter at the top already declares it as a skill.

## Suggested repo layout

```
your-project/
├── CLAUDE.md                          ← project context
├── cloud-training-html-styling.md     ← layout reference
├── 0_intro.html
├── 0_intro_assets/
├── 1_computer.html
├── 1_computer_assets/
├── ...
├── 7_azure.html
└── 7_azure_assets/
```

Or, if you want the skill approach:

```
your-project/
├── CLAUDE.md
├── .claude/
│   └── skills/
│       └── cloud-training-walkthrough/
│           └── SKILL.md               ← (renamed from cloud-training-html-styling.md)
├── 0_intro.html
├── ...
```
