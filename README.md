# Cylinder Monitor

A Progressive Web App for measuring and comparing the stroke speed of pneumatic cylinders using contact vibration sensing via microphone.

**Live app:** https://bcpage.github.io/cylinder-monitor/

---

## What It Does

Mounts a wireless microphone directly on a cylinder body and detects two mechanical events as structure-borne vibration:

- **T_start** — breakaway burst as the shaft overcomes static friction
- **T_end** — impact spike as the shaft hits the end stop

The time delta between them is the stroke time. Comparing stroke times across cylinders identifies which ones are out of sync, guiding flow control valve adjustments until all cylinders move in unison.

---

## Hardware

- **Sensor:** NEEWER CM28 Base dual wireless microphone (USB-C, 48kHz, true stereo)
- **Mounting:** Neodymium magnets on cylinder body, steel plates on transmitters
- **Protocol:** One fixed reference mic + one roving mic across cylinders

NR must be OFF on transmitters. Run the acceptance test on any new hardware before use: block one transmitter, tap the other, verify channels are independent in Audacity.

---

## How It Works

```
Microphone (on cylinder body)
    ↓
Web Audio API → AudioWorkletProcessor
  RMS computation + FFT gate (JavaScript, off main thread)
    ↓
Spike events → Pyodide (Python via WebAssembly)
  CycleTracker: adaptive threshold, T_start lookback, T_end matching
    ↓
Stroke time + speed displayed in UI
```

The detection pipeline runs entirely in the browser — no server, no install. Python logic (numpy, scipy) runs via Pyodide/WebAssembly, preserving the JupyterLab → production analysis path.

---

## Accuracy

| Method | Sample Rate | Time Resolution | Accuracy on 33ms stroke |
|---|---|---|---|
| CM28 wireless (NR off) | 48,000 Hz | 0.021 ms | **0.06%** |
| Phone mic (wired) | 44,100 Hz | 0.023 ms | 0.07% |
| Camera (480 fps) | — | 2.08 ms | ~6% — rejected |

---

## Repository Structure

```
index.html          PWA app — UI and Pyodide bootstrap
processor.js        AudioWorklet — RMS and FFT gate
detector.py         CycleTracker — adaptive threshold and cycle logic
service_worker.js   Offline caching
manifest.json       PWA installability
analysis/
  cylinder_analysis.ipynb   Signal analysis workbench (JupyterLab)
docs/
  Pneumatic_Cylinder_Measurement_Plan.md   Full project reference
  appendix/                                Supporting appendices
session_logs/
  cylinder_sessions.csv     Measurement history (committed after each session)
```

---

## Analysis Notebook

`analysis/cylinder_analysis.ipynb` runs in JupyterLab (GitHub Codespaces). It loads WAV or M4A recordings, runs the same detection pipeline as the app, and provides:

- Raw waveform and combined signal visualization
- Rolling RMS with threshold overlay
- Spike detection and T_start/T_end pairing
- Coincidence quality score (inter-channel delay per spike)
- Power spectral density — T_start vs T_end frequency signatures
- Suggested app settings derived from the recording
- Session CSV logging
- Cross-session trend plot with linear fit
- CUSUM sustained-shift alert
- Inter-cylinder ratio (each cylinder vs fleet mean)

---

## Status

- POC validated on laptop mic (May 2026)
- NEEWER CM28 Base ordered — acceptance test and cylinder hardware validation pending
- Data logging, trend analysis, and calibration report generation planned post-validation

---

## Project Reference

Full technical detail — measurement method, hardware evaluation, detection parameters, measurement protocol, open items — is in [`docs/Pneumatic_Cylinder_Measurement_Plan.md`](docs/Pneumatic_Cylinder_Measurement_Plan.md).
