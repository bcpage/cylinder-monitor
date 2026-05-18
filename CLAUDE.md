# CLAUDE.md — Cylinder Monitor PWA

## What This Project Is

A Progressive Web App (PWA) for measuring pneumatic cylinder stroke speed on the Inovoject
in-ovo vaccination machine (Zoetis). Uses contact vibration sensing via microphone to detect
mechanical events (T_start breakaway, T_end impact) and calculate stroke time and speed.

**Primary goal:** Detect which cylinders are out of sync and guide flow control valve adjustments.
**Secondary goal:** Detect long-term degradation (seal wear, increased friction) over time.
**Accuracy target:** < 1-2%
**Deployed at:** https://bcpage.github.io/cylinder-monitor/
**Platform:** GitHub Pages (static files, HTTPS)

---

## Key Files

| File | Purpose |
|---|---|
| `index.html` | Full app UI + Pyodide bootstrap |
| `processor.js` | AudioWorklet — RMS + FFT gate in JS, spike-only posting |
| `detector.py` | CycleTracker — adaptive threshold, lookback cycle logic, runs in Pyodide |
| `manifest.json` | PWA installability |
| `service_worker.js` | Offline caching — bump cache version on every update |
| `analysis/cylinder_analysis.ipynb` | Signal analysis workbench — load/record/log/trend |
| `docs/Pneumatic_Cylinder_Measurement_Plan.md` | Full project reference |

---

## Architecture

```
Microphone
    |
Web Audio API (JavaScript)
    |
AudioWorkletProcessor — runs off main thread
  - Computes RMS in JS
  - Maintains ring buffer of last 250ms
  - Runs FFT gate in JS
  - Posts spike event + ring buffer snapshot when threshold + FFT gate both pass
    |
postMessage -> main thread
    |
Pyodide -> ring buffer injected -> CycleTracker.process_chunk(spike)
  - Searches ring buffer for T_start in lookback window
  - Matches T_start to T_end spike -> confirmed cycle
    |
Result back to UI
```

---

## Critical Constraints

- **NR must be OFF** on wireless mics — check indicator per hardware model.
  AGC/DSP will suppress T_start and make it undetectable.
- **CM28 Base is current primary hardware** — BY-V30 confirmed hardware mono (L/R identical),
  retained for interim use only. Run acceptance test on all new hardware before use.
- **Additive method** (`|Ch0| + |Ch1|`) for laptop/phone mic at ambient distance.
  **Multiplicative method** (`|Ch0| x |Ch1|`) for wireless mics mounted on cylinder.
- **Threshold multiplier:** 10x validated on laptop mic. Retune from real cylinder data.
- **Ring buffer injection:** Use `pyodide.globals.set()` — never string interpolation
  (NaN/Infinity risk).
- **Ring buffer must be cleared** between spikes — `tracker.ring_buffer.clear()` before
  each injection.
- **Service worker cache version must be bumped** on every update or browsers serve
  stale files.
- **Corporate Chrome:** Symantec/SysTrack extensions crash Pyodide on first load.
  Workaround: hard refresh (Ctrl+Shift+R). Not a blocker.

---

## Current Status

- POC complete and validated on laptop mic (May 12, 2026)
- CM28 Base ordered (May 18, 2026) — acceptance test required on arrival
- Cylinder hardware validation pending
- HF Floor (0.01) not yet empirically tuned — tune from real cylinder hfEnergy data
- MIN/MAX lookback window needs tightening once real stroke time confirmed

## What Is Not Done Yet

- CM28 Base acceptance test
- Cylinder hardware validation (7-phase roving mic protocol)
- PSI entry field in UI (single field, gates Start button)
- HF Floor tuning
- Data logging and export
- Trend view across sessions
- Cylinder selection (1-6) in UI
- Android Chrome test
- iPhone Safari test (T_start detectability unconfirmed on iOS)

---

## What NOT To Do

- Do not change the ring buffer injection method away from `pyodide.globals.set()`
- Do not hardcode debounce in the worklet — read from `processorOptions`
- Do not remove the FFT gate — it is a noise rejection layer, not optional
- Do not cache-bust by renaming files — bump the cache version string in `service_worker.js`
- Do not assume iOS Safari supports T_start detection — unconfirmed, needs empirical test
