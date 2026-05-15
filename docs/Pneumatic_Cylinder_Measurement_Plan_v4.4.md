# Pneumatic Cylinder Stroke Measurement — Consolidated Project Plan
**Version:** 4.4
**Date:** 2026-05-12
**Status:** Active Development — POC Complete, Awaiting Cylinder Hardware
**Supersedes:** Pneumatic_Cylinder_Measurement_Plan_v4.3.md
**Sources:** Claude conversations (May 10–12, 2026) + Gemini conversation (May 10, 2026) + Empirical tap tests (May 11, 2026) + PWA live mic tests (May 12, 2026) + Session 9 PWA tuning (May 12, 2026) + Session 10 code review and deploy workflow (May 12, 2026)

---

## 1. Project Summary

A smartphone-based predictive maintenance tool for measuring and logging the stroke speed of pneumatic cylinders. The system uses contact vibration sensors (phone microphone or external wireless sensors) mounted directly on the cylinder body to detect mechanical events and calculate stroke time and speed.

**Primary Goal:** Detect degradation (seal wear, increased friction) across a set of 4 cylinders over time.
**Accuracy Target:** < 1–2%
**Platform:** PWA — Windows laptop, Android, iPhone (via Chrome / Safari)
**POC Status:** Complete as of May 12, 2026. Full pipeline validated on laptop mic. Cylinder hardware validation pending.

---

## 2. The Problem

| Parameter | Value |
|---|---|
| Number of cylinders | 4 (performing same function over an area) |
| Stroke length | 1 inch |
| Approximate speed | ~30 in/sec |
| Total stroke time | ~33.3 ms |
| Required time resolution | ≤ 0.67 ms (for 2% accuracy) |
| Normal operation | All 4 fire simultaneously |
| Measurement mode | Isolate one cylinder at a time |

**Key constraint:** The 4 cylinders share a metal frame. During measurement mode, the other 3 are silent — isolation IS the filter. No software filtering of simultaneous multi-cylinder events is required during measurement.

---

## 3. Why Camera-Based Measurement Was Rejected

Camera-based measurement was evaluated and rejected. The math:

- Stroke time at 30 in/sec = **33.3 ms**
- For 2% accuracy: max frame interval = 0.67 ms → requires **1,500 fps**
- Best consumer phone (Samsung Galaxy S24): **480 fps** → frame interval = 2.08 ms → **~6% accuracy per frame selection**
- Averaging 10 video recordings reduces this to ~4–5% — still short of the 1–2% target
- The error is systematic quantization error, not random — averaging helps but cannot fully close the gap

**Verdict:** Camera rejected. Contact microphone / acoustic emission method adopted.

---

## 4. The Solution — Contact Microphone / Acoustic Emission Method

### 4.1 Physical Principle

When a pneumatic cylinder fires, two distinct mechanical events propagate as vibration through the metal body:

| Event | Description | Signal Characteristic |
|---|---|---|
| **T_start** (Breakaway) | Air pressure overcomes static friction; shaft breaks free | Burst of stick-slip micro-spikes |
| **T_end** (Impact) | Shaft/weight slams into mechanical end stop | Large, sharp, unambiguous spike |

A microphone pressed against the metal cylinder body acts as a **contact vibration sensor**, bypassing air entirely and reading structure-borne acoustic waves directly. This technique is used industrially in:
- Bearing failure detection
- Pipeline crack detection
- Weld quality inspection
- Seismic monitoring

### 4.2 Why This Setup Is Favorable

The test cylinder is:
- **Metal body** — excellent vibration conductor, minimal dampening
- **Weight loaded** — higher breakaway energy, larger stick-slip events at T_start; more momentum = larger T_end impact
- **Valve several feet away** — valve click is not a reliable T_start indicator; breakaway burst is the primary T_start signal

**Assessment:** Both T_start and T_end are expected to be clearly detectable on this cylinder. The weight-loaded metal body is close to the ideal case for this measurement method.

### 4.3 Accuracy Analysis

| Sensor | Sample Rate | Time Resolution | Accuracy on 33.3 ms stroke |
|---|---|---|---|
| Phone microphone (wired) | 44,100 Hz | 0.023 ms | **0.07%** |
| External USB-C wireless mic (2.4 GHz) | 48,000 Hz | 0.021 ms | **0.06%** |
| Phone accelerometer | ~500 Hz | 2.0 ms | ~6% |
| Camera (480 fps) | 480 fps | 2.08 ms | ~6% |

**The contact microphone method provides ~100× better time resolution than camera or accelerometer approaches.**

### 4.4 Empirical Validation (Finger Tap Test)

A test audio recording of two finger taps on the side of a phone produced:
- Two clean spikes at **110× baseline amplitude**
- Background noise events at **5–13× baseline**
- Signal-to-noise ratio: **~8.5× above background noise ceiling**
- Safe detection threshold: **~30× baseline**

A metal cylinder end-stop impact (structure-borne, weight-loaded) will produce a significantly stronger signal than an airborne finger tap. Detection is expected to be straightforward.

---

## 5. Hardware Options

### 5.1 Sensor Tiers

| Tier | Hardware | Cost | Pros | Cons |
|---|---|---|---|---|
| **Free** | Phone microphone pressed on cylinder | $0 | No hardware needed | Wired to phone, single channel |
| **Budget wired** | Murata 7BB-35-3L0 piezo disc + TRRS plug | ~$3.50 | Zero latency, zero processing, highest fidelity | Requires TRRS jack (many modern phones lack this) |
| **Budget wireless** | Boya BY-V20 (dual, USB-C) | ~$30–40 | Wireless, dual channel, NR toggle, USB-C | 2.4 GHz packet drop risk |
| **Industrial wireless** | Boya BY-V30 (dual, USB-C) | ~$40–60 | 100m range, charging case, better RF stability | Higher cost |

### 5.2 Wired Piezo Option (Highest Fidelity)

**Murata 7BB-35-3L0** piezo disc:
- 35mm bender disc, wires pre-attached
- Available from Mouser Electronics (~$1.50)
- Resonant type: high sensitivity to transient impact spikes
- No preamp needed for impact detection
- Stereo TRRS configuration: Left channel = T_start location, Right channel = T_end location

**Note:** Most modern phones lack a 3.5mm TRRS jack. A USB-C audio adapter (~$8–15) is required.

### 5.3 Wireless Mic Options — Boya BY-V Series

> **⚠️ Critical requirement for all wireless mics:** Noise Reduction (NR) **must be disabled** during measurement. AGC and DSP processing will suppress or distort the breakaway burst (T_start), making it undetectable.

#### Boya BY-V20
- **Connection:** USB-C receiver (plug-and-play, no pairing required)
- **Transmission:** 2.4 GHz proprietary (NOT standard Bluetooth)
- **Sample rate:** 48 kHz / 16-bit
- **Range:** 50 m (164 ft)
- **NR control:** One-click toggle on transmitter; **Blue light = NR OFF** (raw signal mode)
- **Channels:** 2 transmitters → stereo output (Left = Mic A, Right = Mic B)
- **Battery:** 9 hours per transmitter

#### Boya BY-V30
- **Connection:** USB-C receiver
- **Transmission:** 2.4 GHz proprietary
- **Sample rate:** 48 kHz / 16-bit
- **Range:** 100 m (328 ft) — double the V20
- **NR control:** Same one-click toggle; Blue light = NR OFF
- **Channels:** 2 transmitters → stereo output
- **Battery:** 9 hours + 36 hours via charging case
- **Charging case:** Hard case — better for toolbox/shop storage
- **Best for:** Factory environments with RF interference; recommended over V20

**Recommendation:** BY-V30 for industrial use.

### 5.4 Why NOT Standard Bluetooth

1. **Packet drops:** A dropped Bluetooth packet = ~10 ms gap in audio data. Entire stroke is 33 ms. One drop can swallow T_start entirely.
2. **Packet loss concealment:** The codec silently interpolates over gaps — you cannot detect that a drop occurred.

The 2.4 GHz proprietary protocol used by Boya BY-V series does NOT use the standard Bluetooth stack.

### 5.5 Hardware Evaluated and Rejected

**FULAIM X6** (4 transmitters, ~$83–99): Receiver outputs only 2 channels simultaneously regardless of transmitter count. Costs more than BY-V30 with no advantage for this application. **Rejected.**

---

## 6. Mounting Strategy

### 6.1 Single Sensor

- Mount sensor on the **end cap** (closest to impact point) for strongest T_end signal
- Orient mic port/hole **facing the metal surface**
- Align device body **parallel to cylinder rod axis**
- Avoid taut cables pulling the sensor off the surface

### 6.2 Dual Sensor — 180° Opposite Mounting (Recommended)

- Mount **Transmitter A** on one side of the cylinder barrel (via neodymium magnet)
- Mount **Transmitter B** on the **opposite side, 180° offset** (via neodymium magnet)

Both sensors couple to the same metal body. Internal vibration hits both simultaneously. External factory noise hits one sensor harder or with a phase delay.

### 6.3 Magnet Mounting

- Glue a **thin steel adhesive plate** (~1 mm) to the back of each transmitter
- Keep the **neodymium magnet on the cylinder** (permanent installation)
- Transmitter snaps onto magnet for measurement, removes cleanly for storage
- Steel plate is thin enough to fit back in the BY-V30 charging case

**Do NOT glue the magnet directly to the transmitter** — it will not fit in the charging case.

---

## 7. SNR Improvement — Coincidence Detection (Cross-Check Algorithm)

### 7.1 Physical Basis

| Source | Behavior at Both Sensors |
|---|---|
| Cylinder firing (signal) | Hits both sensors **simultaneously** (same metal body) |
| External factory noise (noise) | Hits one sensor harder, or with a **phase delay** |

### 7.2 Algorithm

#### Multiplicative Cross-Check (High Amplitude)

$$Result(t) = |Ch_1(t)| \times |Ch_2(t)|$$

- External noise spike in Ch1 only: Ch1 = 0.8, Ch2 = 0.01 → Product ≈ **0.008** (suppressed)
- Cylinder impact in both channels: Ch1 = 0.5, Ch2 = 0.5 → Product = **0.25** (amplified)

> **⚠️ Limitation:** When both channel amplitudes are small (laptop mic, low-amplitude events), multiplying two small numbers drives the cross-check signal toward zero. Use additive method in this case.

#### Additive Combined Method (Robust — Low or High Amplitude)

$$Result(t) = |Ch_0(t)| + |Ch_1(t)|$$

- Baseline remains proportional to actual signal amplitude
- Validated on laptop mic at 0.018–0.078 amplitude

**Rule of thumb:** Use multiplicative for wireless mics on cylinder. Use additive for laptop/phone mic at ambient distance.

### 7.3 Tuned Detection Parameters (PWA — Laptop Mic Validated)

| Parameter | Value | Notes |
|---|---|---|
| Combined signal | Additive: `|Ch0| + |Ch1|` | Validated on laptop mic |
| Calibration window | 1.5s (150 chunks) | 80th percentile used as baseline |
| Adaptive window | 5s rolling (500 chunks) | Continuous baseline update |
| Threshold multiplier | **10×** | Validated on laptop mic — rejects ambient noise |
| Debounce | 50ms | Prevents double-counting single impact |
| MIN_CYCLE_MS | 3ms | Rejects noise spikes |
| MAX_CYCLE_MS | 3000ms | Rejects timeouts |
| HF Floor | 0.01 | FFT gate — tune empirically on cylinder |

> **Note on multiplier:** Initial testing used 5×. Ambient noise triggered false cycles. Raised to 10× — clean detection with no false positives. On the actual cylinder, retune from real data.

### 7.4 Detection Steps (PWA Pipeline)

1. Calibrate: collect 1.5s of ambient audio, compute 80th percentile RMS as baseline
2. Push threshold (`baseline × multiplier`) to AudioWorklet
3. AudioWorklet computes RMS on every 10ms chunk in JS
4. If RMS ≥ threshold: run FFT gate — sum energy in bins 10–100 (~1kHz–10kHz)
5. If HF energy ≥ HF Floor: fire spike event to main thread with ring buffer snapshot
6. Main thread injects ring buffer into Pyodide CycleTracker, then calls process_chunk
7. CycleTracker searches ring buffer for T_start in lookback window, matches to T_end spike
8. Delta = T_end − T_start. Speed = stroke_length / delta
9. Adaptive baseline updates continuously from 5s rolling window

### 7.5 Python Reference Implementation (JupyterLab / Batch)

```python
import numpy as np

def rolling_rms(signal, window):
    sq = signal ** 2
    kernel = np.ones(window) / window
    return np.sqrt(np.convolve(sq, kernel, mode='same'))

def detect_taps(recording, sr=48000, method='additive',
                threshold_multiplier=20, merge_ms=150,
                min_delta_ms=200, max_delta_ms=2000):

    ch0 = recording[:, 0]
    ch1 = recording[:, 1]

    if method == 'multiplicative':
        combined = np.abs(ch0) * np.abs(ch1)
    else:
        combined = np.abs(ch0) + np.abs(ch1)

    window_samples = int(0.005 * sr)
    rms = rolling_rms(combined, window_samples)

    baseline = np.percentile(rms, 20)
    threshold = baseline * threshold_multiplier

    above = rms > threshold
    transitions = np.diff(above.astype(int))
    starts = np.where(transitions == 1)[0]

    if len(starts) == 0:
        return None, None

    merge_samples = int(merge_ms / 1000 * sr)
    merged = [starts[0]]
    for s in starts[1:]:
        if s - merged[-1] > merge_samples:
            merged.append(s)

    times_ms = [s / sr * 1000 for s in merged]
    deltas = np.diff(times_ms)
    clean = [d for d in deltas if min_delta_ms < d < max_delta_ms]

    return times_ms, clean


def process_cylinder_stroke(recording, stroke_length_inches=1.0, sr=48000):
    times_ms, deltas = detect_taps(recording, sr=sr)
    if not deltas or len(deltas) < 1:
        return "Insufficient detections — check mounting and amplitude"
    stroke_time_ms = deltas[0]
    stroke_time_sec = stroke_time_ms / 1000
    speed_ips = stroke_length_inches / stroke_time_sec
    print(f"Stroke Time: {stroke_time_ms:.2f} ms")
    print(f"Speed: {speed_ips:.2f} in/sec")
    return stroke_time_sec, speed_ips
```

---

## 8. Accuracy Summary

| Configuration | Theoretical Accuracy | Notes |
|---|---|---|
| Single wired piezo (TRRS) | **0.07%** | Best case, zero processing |
| Dual wired piezo (stereo TRRS) | **0.07%** | Adds coincidence detection benefit |
| Single wireless (BY-V20/V30, NR OFF) | **0.06%** | 48 kHz sample rate |
| Dual wireless (BY-V20/V30, NR OFF) | **0.06% + SNR benefit** | Recommended configuration |
| 10-measurement average (any method) | Reduces random error by ~68% | Systematic errors unaffected |
| Camera (480 fps) | ~6% | Rejected |

---

## 9. Measurement Workflow

### 9.1 Per-Session Procedure

1. Isolate target cylinder (disable other 3)
2. Mount dual sensors 180° apart on cylinder barrel (snap to permanent magnets)
3. Plug BY-V30 USB-C receiver into phone or laptop
4. Verify **Blue light** on both transmitters (NR OFF)
5. Open app → select cylinder number → set stroke length in settings
6. Press Start → wait for calibration bar to turn green
7. Fire cylinder → app records and auto-detects spikes
8. Review result — accept or flag as outlier
9. Repeat 3–5 times per cylinder, app averages and logs
10. Re-enable other cylinders

### 9.2 Validation Test (Before First Use on Cylinder)

1. Mount dual transmitters on opposite sides of cylinder
2. Confirm NR OFF (Blue light) on both
3. Record a single firing event in Audacity or similar waveform editor
4. Verify both T_start and T_end spikes are visible on **both channels simultaneously**
5. If T_start is absent: check mounting orientation, check NR status
6. If only one channel shows spikes: check second transmitter pairing

---

## 10. App Design — PWA + Pyodide

### 10.1 Platform Decision

**Selected:** Progressive Web App (PWA) + Pyodide (Python via WebAssembly)

**Rationale:**
This project is not just a timing tool. The long-term direction is trend analysis, anomaly detection, frequency signature analysis, and potentially ML-based wear prediction. Keeping Python throughout preserves the JupyterLab → production pipeline. numpy/scipy are available for future FFT, ML, and frequency analysis. Rewriting to JavaScript would create two diverging codebases.

**Deployment:** GitHub Pages (static files, HTTPS, free)
- No app store required
- Single URL works on all platforms
- Works offline after first load via service worker

**iOS caveat:** Safari on iPhone applies audio processing that may suppress T_start. T_end expected to survive. Needs empirical test before iOS is a confirmed supported platform.

**Flutter** remains the fallback if iOS T_start detection fails on PWA.

**Corporate Chrome caveat:** Symantec and SysTrack extensions (corporate laptop) inject into page context and crash Pyodide CDN loading on first attempt. Workaround: hard refresh (Ctrl+Shift+R) after initial load. Does not affect functionality once loaded.

### 10.2 Architecture

```
Microphone
    ↓
Web Audio API (JavaScript)
    ↓
AudioWorkletProcessor — runs off main thread
  - Computes RMS in JS (no Pyodide call)
  - Maintains ring buffer of last 250ms of chunks
  - Runs FFT gate in JS (no Pyodide call)
  - Posts spike event + ring buffer snapshot when threshold + FFT gate both pass
    ↓
postMessage → main thread (spike events only, ~95% reduction vs per-chunk)
    ↓
Pyodide → ring buffer injected → CycleTracker.process_chunk(spike)
  - Searches ring buffer for T_start in lookback window
  - Matches T_start to T_end spike → confirmed cycle
    ↓
Result back to UI
    ↓
Threshold updated → pushed back to AudioWorklet
```

### 10.3 Repository

**GitHub repo:** bcpage/cylinder-monitor
**Live URL:** https://bcpage.github.io/cylinder-monitor/
**Development environment:** GitHub Codespaces (browser-based VS Code)

### 10.4 File Structure

| File | Purpose | Status |
|---|---|---|
| index.html | Full app UI + Pyodide bootstrap | Working ✅ |
| processor.js | AudioWorklet — RMS + FFT gate in JS, spike-only Pyodide calls | Working ✅ |
| detector.py | CycleTracker — adaptive threshold, lookback cycle logic, runs in Pyodide | Working ✅ |
| manifest.json | PWA installability | Working ✅ |
| service_worker.js | Offline caching, cache v5 | Working ✅ |
| deploy.sh | Unpack AI-delivered zip and push to GitHub | Working ✅ |
| icon.png | 192×192 app icon | Placeholder |

### 10.5 Build Order

1. ✅ PWA hello world — Pyodide running in browser
2. ✅ Live mic via Web Audio API + AudioWorklet
3. ✅ CycleTracker running in Pyodide, detecting events
4. ✅ Adaptive threshold — continuous baseline recalculation
5. ✅ RMS moved to JS AudioWorklet — Pyodide called on spikes only
6. ✅ FFT pre-filter in AudioWorklet — gate on high-frequency energy
7. ✅ Full UI — status bar, cal progress, metric display, cycle log, settings
8. ✅ POC validated on laptop mic — 5 sets of taps, clean detection, SD ~14ms
9. ✅ Ring buffer lookback — T_start/T_end architecture (replaces sequential spike pairing)
10. ✅ Code review — ring buffer injection bug fixed, debounce sync fixed, cal timestamp fixed
11. ✅ Deploy workflow — deploy.sh script, zip delivery pattern documented
12. [ ] Cylinder hardware validation — T_start and T_end on real cylinder
13. [ ] HF Floor tuning from real cylinder data
14. [ ] MIN/MAX cycle window tightening (target: 10–100ms for cylinder)
15. [ ] Data logging and export
16. [ ] Comparison across 4 cylinders
17. [ ] Trend graphing and pass/fail alerts
18. [ ] Test on Android Chrome
19. [ ] Test on iPhone Safari — T_start detectability unconfirmed on iOS

---

## 11. Known Issues and Tuning Notes

### 11.1 Threshold Sensitivity — Single Channel

**Status:** Managed. Multiplier of 10× validated on laptop mic.

**Behavior observed:**
- Multiplier 5×: ambient noise triggers false cycles
- Multiplier 10×: clean detection, no false positives on laptop mic
- Multiplier 10×: taps still detected cleanly (tap RMS ~10–20× baseline)

**On the cylinder:** Retune from real data. Structure-borne impacts will be much louder than desk taps — multiplier may be raisable further, giving more noise rejection.

**Long-term fix:** BY-V30 dual-channel + multiplicative coincidence detection. Noise that hits only one sensor is suppressed mathematically.

### 11.2 FFT Gate — HF Floor Not Yet Tuned

**Status:** Active but not yet empirically tuned. Default 0.01 passes most events through.

**On the cylinder:** Record real T_start and T_end events. Note hfEnergy values in console (SPIKE log lines). Note hfEnergy on ambient noise (GATED log lines). Set HF Floor between noise ceiling and lowest real event.

**Adjust live without reload:**
```javascript
processor.port.postMessage({ type: 'set_hf_floor', value: 0.05 });
```

### 11.3 Cycle Window Too Wide

**Status:** MIN_LOOKBACK_MS = 15ms, MAX_LOOKBACK_MS = 100ms. May need tuning on real cylinder.

**On the cylinder:** Once real stroke time is known (~33ms at 30 in/sec), verify the lookback window brackets T_start reliably. Adjust min/max lookback in Settings UI without restarting.

### 11.4 Corporate Chrome Extension Interference

**Status:** Known, workaround documented.

Symantec and SysTrack extensions (corporate laptop) inject `LsiHookContent.js` which crashes Pyodide's promise chain on first page load. Error appears in console but does not prevent operation after hard refresh.

**Workaround:** Hard refresh (Ctrl+Shift+R) after initial load. Pyodide initializes correctly on reload.

**Not a blocker.** Does not affect measurement accuracy or reliability once loaded.

### 11.5 PWA Offline Mode — Pyodide CDN Not Cached

**Status:** Known limitation. The service worker caches local app files but Pyodide (~30MB) and numpy load from CDN on first use. The app requires an internet connection on first load per device. Subsequent loads may use browser cache but this is not guaranteed.

**Workaround options (not yet implemented):**
- Accept online-only and remove offline claim from manifest
- Self-host Pyodide assets in the repo (adds ~30MB to repo size)

---

## 12. AI-Assisted Development Workflow

This project uses a structured pattern for AI-assisted code review and delivery. This section documents the pattern so it can be repeated consistently.

### 12.1 The Pattern

Code review and updates are done in conversation with an AI assistant (Claude, via ZenAI/LangDock). The AI reviews the full source, identifies issues, proposes fixes, and delivers corrected files as a zip. The developer unpacks and deploys using a shell script.

**Why this works:**
- The AI sees the full codebase in one context — cross-file issues are visible (e.g., debounce defined in two places that can diverge)
- Fixes are delivered as complete, ready-to-deploy files — no manual patching
- The deploy script eliminates copy-paste errors
- The service worker cache version is bumped automatically in each delivery so browsers pick up new files

### 12.2 Providing Code for Review

Paste all source files into a single message using this shell command from the repo root:

```bash
echo "===== detector.py =====" && cat detector.py && \
echo "===== index.html =====" && cat index.html && \
echo "===== processor.js =====" && cat processor.js && \
echo "===== service_worker.js =====" && cat service_worker.js && \
echo "===== manifest.json =====" && cat manifest.json
```

Then ask: `review it` or describe the specific issue.

### 12.3 Receiving Updated Files

The AI delivers a `cylinder-monitor.zip` containing all five app files. The zip always contains the full files — not patches or diffs.

**File list inside the zip:**
```
cylinder-monitor/
  detector.py
  index.html
  processor.js
  service_worker.js
  manifest.json
```

`icon.png`, `README.md`, and `deploy.sh` are never included in the zip — they are not touched by the AI delivery.

### 12.4 deploy.sh — The Deploy Script

`deploy.sh` lives in the repo root. It unpacks the zip, copies files into the repo, commits, and pushes in one command.

**First-time setup (once only):**
```bash
chmod +x deploy.sh
git add deploy.sh
git commit -m "add deploy script"
git push
```

**Every subsequent delivery:**
```bash
./deploy.sh cylinder-monitor.zip "describe what changed"
```

**What the script does:**
1. Validates the zip file exists
2. Unpacks to `/tmp/deploy_staging/`
3. Copies the five app files into the repo root
4. `git add` → `git commit` → `git push`
5. Cleans up the temp directory

**What it does NOT touch:** `README.md`, `icon.png`, `deploy.sh` itself.

**Script source:**
```bash
#!/bin/bash
# deploy.sh — unpack a cylinder-monitor zip and push to GitHub
# Usage: ./deploy.sh <zipfile> [commit message]

set -e

ZIP="${1}"
MSG="${2:-update from zip}"

if [ -z "$ZIP" ]; then
  echo "Usage: ./deploy.sh <zipfile> [commit message]"
  exit 1
fi

if [ ! -f "$ZIP" ]; then
  echo "Error: file not found: $ZIP"
  exit 1
fi

echo "Unpacking $ZIP..."
unzip -o "$ZIP" "cylinder-monitor/*" -d /tmp/deploy_staging

echo "Copying files into repo..."
cp /tmp/deploy_staging/cylinder-monitor/* .

echo "Cleaning up staging..."
rm -rf /tmp/deploy_staging

echo "Staging changes..."
git add detector.py index.html processor.js service_worker.js manifest.json

echo "Committing..."
git commit -m "$MSG"

echo "Pushing..."
git push

echo "Done."
```

### 12.5 Service Worker Cache Versioning

Each AI delivery bumps the service worker cache version (e.g., `cyl-v4` → `cyl-v5`). This forces browsers to fetch updated files rather than serving stale cached versions. No manual action required — it is handled in the delivered files.

### 12.6 What to Tell the AI at the Start of a New Session

Upload these three files to give the AI full project context:
- `Memory_Update_Session_7.txt` (or current version)
- `Pneumatic_Cylinder_Measurement_Plan_v4.4.md` (this file)
- `The_Updated_Seed - Version_4.txt`

Then paste the current source files using the command in Section 12.2.

---

## 13. Predictive Maintenance Value

| Observation | Interpretation |
|---|---|
| Gradual increase in ΔT over weeks | Seal wear, increased friction |
| Sudden step change in ΔT | Damage, contamination, pressure change |
| One cylinder slower than other 3 | Investigate that specific unit |
| All 4 consistent and within spec | System healthy |
| High standard deviation across 10 runs | Inconsistent pressure supply or mounting issue |

---

## 14. Hardware Shopping List

| Item | Specification | Estimated Cost | Source |
|---|---|---|---|
| Boya BY-V30 | Dual USB-C wireless mic, 2.4 GHz, NR toggle | ~$40–60 | Amazon |
| Neodymium disc magnets | 10–15 mm diameter, N52 grade | ~$8–12 (pack) | Amazon |
| Thin steel adhesive plates | "Phone magnet plates," <1 mm thick | ~$5–8 (pack) | Amazon |
| USB-C audio adapter (optional) | If using wired piezo fallback | ~$8–15 | Amazon |
| Murata 7BB-35-3L0 (optional) | Piezo disc for wired fallback | ~$1.50 each | Mouser Electronics |

**Total estimated cost (wireless path):** ~$55–80
**Total estimated cost (wired piezo fallback only):** ~$15–25

---

## 15. Open Items

**Hardware:**
- [ ] BY-V30 purchase decision
- [ ] Source neodymium disc magnets (10–15mm, N52) and thin steel adhesive plates
- [ ] Validation test on actual cylinder hardware
- [ ] Confirm T_start (breakaway burst) detectable on this specific cylinder

**Software — post-cylinder-validation:**
- [ ] Tune HF Floor from real cylinder hfEnergy data
- [ ] Tighten MIN/MAX lookback window from real stroke time data
- [ ] Data logging / export
- [ ] Trend view across multiple sessions
- [ ] Cylinder selection (1–4) in UI
- [ ] Test on Android Chrome
- [ ] Test on iPhone Safari

**Infrastructure:**
- [ ] Resolve PWA offline limitation (Pyodide CDN dependency)
- [ ] Explore LangDock Agent for more durable session continuity
- [ ] Consider Workflow for automating memory updates

---

## 16. Empirical Validation Log

### 16.1 S22U Smartphone Tap Test (May 11, 2026)

| Parameter | Value |
|---|---|
| Device | Samsung Galaxy S22 Ultra |
| Recording format | Stereo M4A → WAV → CSV |
| Simulated events | Two finger taps on phone body |
| Channel correlation | ~0.36 |
| Tap amplitude | ~110× baseline RMS |
| Background noise | 5–13× baseline |
| SNR above noise ceiling | ~8.5× |

| Event | Single-Channel (ms) | Stereo Cross-Check (ms) |
|---|---|---|
| Tap 1 (T_start analog) | ~914 | ~914 |
| Tap 2 (T_end analog) | ~2,236 | ~2,237 |
| Δt | ~1,322 | ~1,323 |

Agreement within 1 ms — algorithm consistency confirmed.

### 16.2 Laptop Mic Device Troubleshooting (May 11, 2026)

| Device | API | Outcome |
|---|---|---|
| 23 — Intel Smart Sound | WASAPI | Failed — exclusive mode conflict |
| 2 — Intel Smart Sound | MME | Failed — channel count mismatch |
| 0 — Microsoft Sound Mapper | MME | Worked — routed to Jabra (wrong device) |
| **27 — Realtek HD Audio Mic** | **WDM-KS** | **Working — correct device** |

### 16.3 Multi-Shot 10-Tap Test — JupyterLab (May 11, 2026)

| Parameter | Value |
|---|---|
| Taps recorded | 10 |
| Clean deltas | 9 |
| Mean | 816.5 ms |
| SD | 31.5 ms |
| CV | 3.86% |

SD of 31.5 ms represents human tapping variability, not measurement error. On an actual cylinder SD expected to be significantly tighter.

**Merge window tuning:**

| Merge Window | Detections | Clean Deltas | SD (ms) | CV |
|---|---|---|---|---|
| 50 ms | 13 | 9 | 49.3 ms | 6.15% |
| **150 ms** | **11** | **9** | **31.5 ms** | **3.86%** |

### 16.4 PWA Live Mic Test — Initial (May 12, 2026)

| Parameter | Value |
|---|---|
| Platform | Chrome browser, Windows laptop |
| Audio pipeline | Web Audio API → AudioWorklet → Pyodide |
| Sample rate | 48,000 Hz |
| Baseline RMS | 0.0189 |
| Working threshold | 5× baseline |

| Test | Result |
|---|---|
| 2 taps at threshold × 1 | 5+ cycles (over-sensitive) |
| 2 taps at threshold × 3 | 5 cycles (still over-sensitive) |
| 2 taps at threshold × 5 | **2 cycles — clean** |
| Deltas | 56ms, 58ms — SD 1ms |

### 16.5 PWA Multiplier Tuning — Ambient Noise Rejection (May 12, 2026)

**Problem:** At multiplier 5×, ambient background noise triggered false cycles with no taps.

| Multiplier | Ambient False Cycles | Tap Detection |
|---|---|---|
| 5× | Yes — frequent | Yes |
| 10× | None observed | Yes — clean |

**Validated settings for laptop mic:**

| Parameter | Value |
|---|---|
| Multiplier | 10× |
| HF Floor | 0.01 (not yet empirically tuned) |
| Baseline (typical) | ~0.028–0.038 |
| Threshold (typical) | ~0.28–0.38 |
| Tap peak RMS | ~0.40–0.56 |

### 16.6 PWA 5-Set Tap Test — POC Validation (May 12, 2026)

5 sets of two taps each. No false cycles between sets.

| Cycle | Delta (ms) | Speed (in/s) |
|---|---|---|
| 1 | 266 | 3.759 |
| 2 | 268 | 3.731 |
| 3 | 270 | 3.704 |
| 4 | 261 | 3.831 |
| 5 | 298 | 3.356 |

**Mean delta:** 272.6ms | **SD:** 14ms | **CV:** 5.1%

Cycles 1–4 extremely tight (261–270ms, SD 4ms). Cycle 5 outlier — slower tap. SD represents human tapping variability, not measurement error. On actual cylinder, SD expected to be significantly tighter (mechanically fixed events).

**POC conclusion:** Full pipeline validated end-to-end on laptop mic. Ready for cylinder hardware validation.

### 16.7 Code Review — Bug Fixes Applied (May 12, 2026)

Three bugs identified and fixed in Session 10:

| Bug | Severity | Fix |
|---|---|---|
| Ring buffer injected via string interpolation — NaN/Infinity risk | High | Replaced with `pyodide.globals.set()` — no JSON round-trip |
| Ring buffer not cleared between spikes — stale entries accumulate | High | Added `tracker.ring_buffer.clear()` before each injection |
| Calibration passed RMS value as timestamp | Medium | Fixed to use `audioCtx.currentTime` |
| Debounce not synced to worklet on settings change | Medium | `applyReset()` now sends `set_debounce` to worklet |
| Worklet debounce hardcoded at 50ms — ignored `processorOptions` | Medium | Fixed to read `debounceMs` from `processorOptions` at construction |

Service worker cache bumped to `cyl-v5`.

---

*Document compiled from Claude and Gemini conversations (May 10–12, 2026) plus empirical validation sessions. All claims vetted against manufacturer specifications and published technical sources where available. Accuracy figures are theoretical maximums under ideal conditions — empirical validation on the specific cylinder is required before relying on these numbers for production use.*

*Version 4.4 — 2026-05-12. Supersedes v4.3. Added Section 12 (AI-assisted development workflow, deploy.sh pattern). Added Section 16.7 (code review bug fixes). Updated architecture diagram, file table, and build order to reflect ring buffer lookback architecture.*
