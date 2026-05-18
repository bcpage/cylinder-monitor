# Getting Started — Orientation Guide

> Read this first if you're picking this project up after time away.

---

## What Is This

A PWA that measures pneumatic cylinder stroke speed using a contact microphone mounted on the cylinder body. Detects two vibration events (breakaway + end-stop impact) and times the delta between them.

**Primary goal:** Compare stroke times across all cylinders and guide flow control valve adjustments until they're in sync.

Full detail: [`docs/Pneumatic_Cylinder_Measurement_Plan.md`](docs/Pneumatic_Cylinder_Measurement_Plan.md)

---

## Current Status

- POC validated on laptop mic (May 2026) ✅
- NEEWER CM28 Base ordered — **acceptance test required on arrival**
- Cylinder hardware validation is the next gate — nothing else matters until T_start is confirmed detectable on the real cylinder
- Data logging, PSI field, cylinder selector planned post-validation

**Next action:** CM28 arrives → run acceptance test → cylinder validation session.

---

## Quick Links

| | |
|---|---|
| **Repo** | https://github.com/bcpage/cylinder-monitor |
| **Live PWA** | https://bcpage.github.io/cylinder-monitor/ |
| **GitHub Actions** | https://github.com/bcpage/cylinder-monitor/actions |
| **Codespace (VS Code)** | https://bug-free-space-disco-95jpxwvvgjvcr56.github.dev/ |
| **JupyterLab** | https://bug-free-space-disco-95jpxwvvgjvcr56-8888.app.github.dev/lab/tree/analysis/cylinder_analysis.ipynb |

> Codespace URLs are instance-specific — update this file if GitHub assigns a new Codespace.

---

## Starting the Workspace

After opening the Codespace in a browser:

**Terminal 1 — Claude Code:**
```
claude
```

**Terminal 2 — JupyterLab:**
```
jupyter lab --no-browser --port=8888
```
Then click the port 8888 popup → JupyterLab opens in a new browser tab.

In JupyterLab: open `analysis/cylinder_analysis.ipynb` → Kernel → Restart Kernel and Run All Cells.

That's it. No reinstalling, no reconfiguring. These two commands are the only startup ritual every time.

**What survives a Codespace reload or restart:** everything — files, installed packages, all state. Packages live in `~/.local` and are not wiped.

**What requires a full rebuild:** only a manual devcontainer rebuild — rare, you'd have to trigger it deliberately.

---

## Repo Map

```
index.html          )
processor.js        )  PWA source — served by GitHub Pages
detector.py         )  (must stay at root)
service_worker.js   )
manifest.json       )
icon.png            )

CLAUDE.md               Instructions for Claude Code
README.md               Public project description

analysis/
  cylinder_analysis.ipynb   Signal analysis workbench — load recordings,
                            tune detection, log sessions, plot trends

docs/
  Pneumatic_Cylinder_Measurement_Plan.md   Full project reference
  pwa-wireframe.html                        UI design reference
  appendix/
    Appendix_Wireless_Mic_Hardware_Research.md
    Appendix_Science_Experiments.md

session_logs/
  cylinder_sessions.csv   Measurement history — commit after each session

test_data/              Local recordings — gitignored, stays local
```

---

## Workflow — Making Changes

Claude Code reads the repo directly. Start a session with:
```
claude
```

To review or edit app source files, just describe what you want. Claude Code handles reading, editing, committing, and pushing.

To deploy a change: edit files → Claude Code commits and pushes → GitHub Pages deploys automatically (takes ~1 minute).

**Always bump the service worker cache version** in `service_worker.js` when changing app files, or browsers will serve stale cached versions.

---

## Workflow — Measurement Session

1. Run acceptance test on CM28 Base if new hardware (see plan Section 5.2)
2. Mount sensors using 7-phase roving mic protocol (see plan Section 9.2)
3. Open PWA → enter PSI → Start → fire cylinder
4. Or: record in CM28 standalone mode → drop WAV into `test_data/` → open notebook
5. Run notebook analysis → Log Session cell
6. Commit the session log:
```
git add session_logs/cylinder_sessions.csv
git commit -m "data: cylinder session YYYY-MM-DD"
git push
```

---

## Key Constraints — Don't Break These

- **NR must be OFF** on CM28 transmitters — AGC/DSP suppresses T_start
- **Ring buffer injection** uses `pyodide.globals.set()` — never string interpolation
- **Ring buffer must be cleared** between spikes — `tracker.ring_buffer.clear()`
- **Service worker cache version** must be bumped on every app file change
- **BY-V30 is hardware mono** — retained for reference only, not for dual-channel use
