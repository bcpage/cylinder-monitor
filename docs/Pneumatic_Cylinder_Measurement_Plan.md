# Pneumatic Cylinder Stroke Measurement — Consolidated Project Plan
**Version:** 6.0
**Date:** 2026-05-18
**Status:** Active Development — POC Complete, Hardware Ordered, Awaiting Cylinder Validation
**Supersedes:** Pneumatic_Cylinder_Measurement_Plan_v5.0.md
**Sources:** Claude conversations (May 10–18, 2026) + Gemini conversation (May 10, 2026) + Empirical tap tests (May 11, 2026) + PWA live mic tests (May 12, 2026) + Session 9 PWA tuning (May 12, 2026) + Session 10 code review and deploy workflow (May 12, 2026) + Research session May 15, 2026 (prior art, Python packages, project ideas, hardware evaluation) + Session May 18, 2026 (scope clarification, hardware decision, measurement protocol)

---

## 1. Project Summary

A smartphone-based tool for measuring and logging the stroke speed of pneumatic cylinders on the Inovoject in-ovo vaccination machine (Zoetis). The system uses contact vibration sensors (phone microphone or external wireless sensors) mounted directly on the cylinder body to detect mechanical events and calculate stroke time and speed.

**Primary Goal:** Detect which cylinders are out of sync and guide flow control valve adjustments until all cylinders move in tight unison.
**Secondary Goal (future):** Detect long-term degradation (seal wear, increased friction) across cylinders over time.
**Accuracy Target:** < 1–2%
**Platform:** PWA — Windows laptop, Android, iPhone (via Chrome / Safari)
**POC Status:** Complete as of May 12, 2026. Full pipeline validated on laptop mic. Cylinder hardware validation pending.
**Hardware Status:** NEEWER CM28 Base ordered (May 18, 2026). BY-V30 confirmed hardware mono — retained for interim validation use only.

---

## 2. The Problem

| Parameter | Value |
|---|---|
| Number of cylinders | 4 top + 1–2 bottom = **5–6 total** |
| Stroke length | 1 inch |
| Approximate speed | ~30 in/sec |
| Total stroke time | ~33.3 ms |
| Required time resolution | ≤ 0.67 ms (for 2% accuracy) |
| Normal operation | All cylinders fire simultaneously |
| Measurement mode | One fixed reference mic + one roving mic |

**Primary constraint:** All cylinders must start and end movement at the same time, in tight unison. Each cylinder has a flow control valve for speed adjustment. The measurement system identifies which cylinders are out of sync and guides valve adjustments.

**Key constraint:** The cylinders share a metal frame. Isolation is achieved via the fixed reference mic + roving mic protocol, not by disabling cylinders.

**Sync window tolerance:** Open — to be defined once baseline measurements are established.

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

### 4.5 Prior Art — Mechanical Watch Timegraphers

The closest open-source analogy to this project is not from industrial automation but from the **mechanical watch hobbyist community**. A timegrapher measures watch movement performance by placing a contact piezo microphone against the watch case, detecting tick and tock events as vibration spikes, and measuring the time delta between them — exactly the same physical principle as the cylinder project.

The open-source `tg` project (github.com/vacaboja/tg, GNU GPL v2) implements this in a native desktop application. A related Hackaday project, **Tick-Tach**, documents a DIY piezo microphone build including TRRS wiring notes and iPhone compatibility quirks directly applicable to the cylinder project hardware.

**Direct parallels:**

| Timegrapher | Cylinder PWA |
|---|---|
| Piezo disc on watch case | Phone mic / CM28 sensor on cylinder body |
| Tick event (T1) | T_start — breakaway burst |
| Tock event (T2) | T_end — end-stop impact |
| Delta between tick and tock | Stroke time (ms) |
| Rate drift over weeks | Increasing stroke time = seal wear |
| Beat error | Cycle-to-cycle SD across 10 measurements |
| Amplitude decrease | Could map to T_start signal energy decrease |

**Why this project is still novel:** No timegrapher software runs in a browser via Web Audio API. The combination of PWA + Web Audio API + AudioWorklet + Pyodide/WebAssembly + adaptive threshold + dual-channel coincidence detection + GitHub Pages deployment does not exist anywhere in the watch timing or industrial acoustic emission communities.

**Academic literature:** Research exists on acoustic emission (AE) for cylinder seal condition monitoring (Shanbhag et al., Springer 2020, PMC 2021) but uses dedicated lab-grade AE sensors and measures seal leakage frequency signatures — not stroke timing as a degradation proxy. The finding that AE signal energy correlates strongly and linearly with seal wear severity validates the physical basis of the cylinder project's approach.

---

## 5. Hardware Options

### 5.1 Sensor Tiers

| Tier | Hardware | Cost | Pros | Cons |
|---|---|---|---|---|
| **Free** | Phone microphone pressed on cylinder | $0 | No hardware needed | Wired to phone, single channel |
| **Budget wired** | Murata 7BB-35-3L0 piezo disc + TRRS plug | ~$3.50 | Zero latency, zero processing, highest fidelity | Requires TRRS jack (many modern phones lack this) |
| **Current primary** | NEEWER CM28 Base (dual, USB-C) | ~$60 | True stereo confirmed, NR off confirmed, no AGC, manual gain, TX standalone recording | Requires acceptance test on arrival |
| **Upgrade option** | NEEWER CM28 Max (dual, USB-C) | ~$110 | 24-bit float recording, 87dB SNR | Higher cost |

### 5.2 NEEWER CM28 Base — Current Primary Hardware

**Status:** Ordered May 18, 2026.

| Feature | Status |
|---|---|
| True stereo | ✅ Confirmed in manual and independent reviewer |
| NR off | ✅ One button toggle per TX — confirmed off state |
| AGC | ✅ Not mentioned in any spec or documentation |
| Manual gain | ✅ 5-level tap control |
| Low cut filter | ✅ 75Hz / 150Hz / OFF — independently switchable |
| TX standalone recording | ✅ 4GB / 9hrs uncompressed WAV per TX |
| USB-C output | ✅ |
| Sample rate | 48kHz / 16-bit |
| Range | 200m |
| Price | ~$60 |

**Mandatory acceptance test on arrival:**
1. Power on both TX units and RX
2. Physically block TX1 completely (hand over mic)
3. Tap TX2 sharply
4. Open Audacity — check both L and R channels
5. **Pass:** Left shows nothing, Right shows spike
6. **Fail:** Both channels identical — return unit

> See `docs/appendix/Appendix_Wireless_Mic_Hardware_Research.md` for full hardware evaluation including all products considered and rejected.

### 5.3 BY-V30 Status — Hardware Mono Confirmed

The Boya BY-V30 was the originally specified hardware. During the acceptance test, both L and R channels showed identical waveforms when one TX was blocked. **The BY-V30 RX hardware combines both TX inputs into a single mono signal and duplicates it to both L and R of the USB output.** This is a hardware architecture decision with no software or firmware workaround.

**What the BY-V30 can still do:**
- All timing domain measurements remain valid — stroke time, T_start, T_end, pneumatic lag
- The combined mono signal preserves timing relationships between events from both sensors
- Retained for the initial cylinder validation session in mono mode

**What is lost with BY-V30:**
- Amplitude ratio between channels
- True hardware coincidence detection (multiplicative method)
- Independent per-channel SNR measurement

### 5.4 Wired Piezo Option (Highest Fidelity)

**Murata 7BB-35-3L0** piezo disc:
- 35mm bender disc, wires pre-attached
- Available from Mouser Electronics (~$1.50)
- No preamp needed for impact detection
- Stereo TRRS configuration: Left channel = T_start location, Right channel = T_end location
- **iPhone TRRS note:** Some iPhones require a 10kΩ resistor between ground and mic output. Test before assuming connection is working.

### 5.5 Why NOT Standard Bluetooth

1. **Packet drops:** A dropped Bluetooth packet = ~10 ms gap in audio data. Entire stroke is 33 ms. One drop can swallow T_start entirely.
2. **Packet loss concealment:** The codec silently interpolates over gaps — you cannot detect that a drop occurred.

The 2.4 GHz proprietary protocol used by NEEWER CM28 does NOT use the standard Bluetooth stack.

### 5.6 Optional Hardware Cross-Check — Hall Effect Sensor

A small magnet on the cylinder rod and a hall effect sensor at each end cap provides a completely independent T_start/T_end measurement. Cheap to implement and provides a hardware cross-check to validate the acoustic method during initial cylinder validation.

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
- Steel plate is thin enough to fit back in the CM28 charging case

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

### 7.3 Cross-Correlation Delay Measurement (Future Enhancement)

Computing the actual **time delay between the two channels** per event produces a **continuous quality score per cycle** rather than a binary pass/fail. Structure-borne vibration from the same metal body arrives within microseconds on both sensors. External noise hitting one sensor from a different direction shows a measurable delay. Implemented in `analysis/cylinder_analysis.ipynb` (Coincidence Quality Score cell).

### 7.4 Tuned Detection Parameters (PWA — Laptop Mic Validated)

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

### 7.5 Detection Steps (PWA Pipeline)

1. Calibrate: collect 1.5s of ambient audio, compute 80th percentile RMS as baseline
2. Push threshold (`baseline × multiplier`) to AudioWorklet
3. AudioWorklet computes RMS on every 10ms chunk in JS
4. If RMS ≥ threshold: run FFT gate — sum energy in bins 10–100 (~1kHz–10kHz)
5. If HF energy ≥ HF Floor: fire spike event to main thread with ring buffer snapshot
6. Main thread injects ring buffer into Pyodide CycleTracker, then calls process_chunk
7. CycleTracker searches ring buffer for T_start in lookback window, matches to T_end spike
8. Delta = T_end − T_start. Speed = stroke_length / delta
9. Adaptive baseline updates continuously from 5s rolling window

### 7.6 Python Reference Implementation (JupyterLab / Batch)

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
```

---

## 8. Accuracy Summary

| Configuration | Theoretical Accuracy | Notes |
|---|---|---|
| Single wired piezo (TRRS) | **0.07%** | Best case, zero processing |
| Dual wired piezo (stereo TRRS) | **0.07%** | Adds coincidence detection benefit |
| Single wireless (CM28 Base, NR OFF) | **0.06%** | 48 kHz sample rate |
| Dual wireless (CM28 Base, NR OFF) | **0.06% + SNR benefit** | Recommended configuration |
| 10-measurement average (any method) | Reduces random error by ~68% | Systematic errors unaffected |
| Camera (480 fps) | ~6% | Rejected |

---

## 9. Measurement Workflow

### 9.1 Pre-Session Setup

1. Plug CM28 Base USB-C receiver into laptop
2. Verify **NR OFF** on both transmitters (per CM28 indicator)
3. Open app → select cylinder number
4. **Enter PSI reading** from supply pressure gauge — required before Start is enabled
5. Date and time are auto-stamped by the app when the session starts
6. Start button unlocks → calibration runs → ready to fire

### 9.2 Seven-Phase Measurement Protocol — Roving Mic

**Setup:** One mic = fixed reference (stays on primary cylinder all session). One mic = roving (moves between positions).

#### Phase 1 — Valve Baseline
- Both mics on valve body, 180° apart
- Fire 5 shots
- Establishes valve fire timing and shot-to-shot consistency
- **Output:** Valve fire SD, confirmed T_zero reference

#### Phase 2 — Primary Cylinder Characterization
- Both mics on primary cylinder, 180° apart
- Fire 5 shots
- Best possible T_start and T_end detection on reference cylinder
- **Output:** Primary cylinder stroke time, SD, speed — gold standard

#### Phase 3 — Valve vs Primary (Lag Measurement)
- Mic A on primary cylinder / Mic B on valve
- Fire 5 shots
- Measures pneumatic lag: time from valve fire to cylinder breakaway
- **Output:** Valve-to-cylinder lag for primary

#### Phase 4 — Primary vs Each Secondary (Roving)
- Mic A stays on primary cylinder permanently
- Mic B moves to each remaining cylinder in sequence
- Fire 5 shots at each position
- Cover all top cylinders, then bottom cylinders
- **Output:** Each cylinder's stroke time relative to primary

#### Phase 5 — Flag and Recheck
- Any cylinder outside tolerance: return Mic B to it
- Fire 5 more shots
- Confirms reading is not a mounting artifact
- **Output:** Confirmed outliers for valve adjustment

#### Phase 6 — Post-Adjustment Loop
- Adjust flow control valves on outlier cylinders
- Repeat Phase 4 roving pass
- Primary stays fixed — clean before/after comparison
- Repeat until all cylinders within sync window

#### Phase 7 — Final Validation
- Return both mics to primary cylinder, 180° apart
- Fire 5 shots
- Confirms primary has not drifted during the adjustment session
- Bookends the session with matched dual-mic readings

**Total passes:** ~25–35 fires for a full session on 6 cylinders.

### 9.3 Mic Placement Decision Table

| Situation | Mic Config | Reason |
|---|---|---|
| Establishing reference | Both on one cylinder | Maximum SNR and accuracy on baseline |
| Comparing cylinders | One fixed, one roving | Common reference across all comparisons |
| Checking lag | One on valve, one on cylinder | Direct causal measurement |
| Confirming outlier | Both on suspect cylinder | Eliminate mounting artifact before adjusting |

### 9.4 Validation Test (Before First Use on Cylinder)

1. Mount dual transmitters on opposite sides of cylinder
2. Confirm NR OFF on both
3. Record a single firing event in Audacity
4. Verify both T_start and T_end spikes are visible on **both channels simultaneously**
5. If T_start is absent: check mounting orientation, check NR status
6. If only one channel shows spikes: check second transmitter pairing / run CM28 acceptance test

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

**Corporate Chrome caveat:** Symantec and SysTrack extensions (corporate laptop) inject into page context and crash Pyodide CDN loading on first attempt. Workaround: hard refresh (Ctrl+Shift+R) after initial load.

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
| analysis/cylinder_analysis.ipynb | Signal analysis workbench — load/record/log/trend | Working ✅ |
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
11. ✅ Claude Code integration — replaces deploy.sh zip delivery pattern
12. [ ] CM28 Base acceptance test on arrival
13. [ ] Cylinder hardware validation — T_start and T_end on real cylinder
14. [ ] HF Floor tuning from real cylinder data
15. [ ] MIN/MAX cycle window tightening (target: 10–100ms for cylinder)
16. [ ] PSI entry field in UI — manual entry, stored per session, gates Start button
17. [ ] Cylinder selection (1–6) in UI
18. [ ] Data logging and export (CSV, include PSI per session)
19. [ ] Trend graphing and pass/fail alerts
20. [ ] Calibration report generation — format TBD
21. [ ] Test on Android Chrome
22. [ ] Test on iPhone Safari — T_start detectability unconfirmed on iOS

---

## 11. Known Issues and Tuning Notes

### 11.1 Threshold Sensitivity — Single Channel

**Status:** Managed. Multiplier of 10× validated on laptop mic.

**Behavior observed:**
- Multiplier 5×: ambient noise triggers false cycles
- Multiplier 10×: clean detection, no false positives on laptop mic
- Multiplier 10×: taps still detected cleanly (tap RMS ~10–20× baseline)

**On the cylinder:** Retune from real data. Structure-borne impacts will be much louder than desk taps — multiplier may be raisable further, giving more noise rejection.

**Long-term fix:** CM28 Base dual-channel + multiplicative coincidence detection.

### 11.2 FFT Gate — HF Floor Not Yet Tuned

**Status:** Active but not yet empirically tuned. Default 0.01 passes most events through.

**On the cylinder:** Record real T_start and T_end events. Note hfEnergy values in console (SPIKE log lines). Note hfEnergy on ambient noise (GATED log lines). Set HF Floor between noise ceiling and lowest real event.

**Adjust live without reload:**
```javascript
processor.port.postMessage({ type: 'set_hf_floor', value: 0.05 });
```

### 11.3 Cycle Window Too Wide

**Status:** MIN_LOOKBACK_MS = 15ms, MAX_LOOKBACK_MS = 100ms. May need tuning on real cylinder.

**On the cylinder:** Once real stroke time is known (~33ms at 30 in/sec), verify the lookback window brackets T_start reliably.

### 11.4 Corporate Chrome Extension Interference

**Status:** Known, workaround documented.

Symantec and SysTrack extensions inject `LsiHookContent.js` which crashes Pyodide's promise chain on first page load.

**Workaround:** Hard refresh (Ctrl+Shift+R) after initial load. Pyodide initializes correctly on reload. Not a blocker.

**Root cause:** Service worker is not yet active on the very first visit — it installs during that first load. On subsequent loads the service worker is in control and the loading sequence changes, which alters injection timing.

### 11.5 PWA Offline Mode — Pyodide CDN Not Cached

**Status:** Known limitation. Pyodide (~30MB) and numpy load from CDN on first use. The app requires an internet connection on first load per device.

**Workaround options (not yet implemented):**
- Accept online-only and remove offline claim from manifest
- Self-host Pyodide assets in the repo (adds ~30MB to repo size)

---

## 12. AI-Assisted Development Workflow

### 12.1 Current Pattern — Claude Code Integration

As of May 2026, the project uses **Claude Code** (Anthropic CLI tool) running directly in GitHub Codespaces. Claude Code reads the codebase, makes edits, and commits — all within the Codespace. The earlier deploy.sh / zip delivery pattern is deprecated.

**Advantages over the zip pattern:**
- Claude Code sees the full repo in context — cross-file issues are visible
- Edits are made directly to files — no zip, no copy-paste, no staging
- Git operations (add, commit, push) handled by Claude Code directly

### 12.2 Providing Code for Review

```bash
echo "===== detector.py =====" && cat detector.py && \
echo "===== index.html =====" && cat index.html && \
echo "===== processor.js =====" && cat processor.js && \
echo "===== service_worker.js =====" && cat service_worker.js && \
echo "===== manifest.json =====" && cat manifest.json
```

Then ask: `review it` or describe the specific issue.

### 12.3 Jupyter Notebook Integration

JupyterLab runs inside Codespaces and is accessible from any browser via the Codespaces port forwarding URL — including mobile. The analysis notebook (`analysis/cylinder_analysis.ipynb`) supports:
- Loading WAV or M4A recordings
- Live recording from the CM28 Base via `sounddevice`
- Audio playback per channel
- Full detection pipeline mirroring the PWA
- Coincidence quality scoring
- Session CSV logging
- Cross-session trend plotting
- CUSUM alert detection
- Inter-cylinder ratio tracking

### 12.4 Service Worker Cache Versioning

Each code delivery that changes app files should bump the service worker cache version (e.g., `cyl-v5` → `cyl-v6`). Claude Code handles this when making app file changes.

### 12.5 What to Tell Claude Code at the Start of a New Session

Upload the current version of this plan file. Claude Code reads the repo directly so source files do not need to be pasted manually.

---

## 13. Python Packages for the Pipeline

### 13.1 Use Immediately — Already in Pyodide

**`scipy.signal.find_peaks`** — purpose-built for finding T_start and T_end spikes.

**`scipy.signal.welch`** — Power Spectral Density for frequency domain analysis. The frequency features identified in Shanbhag et al. (PSD, mean frequency, median frequency) are candidates for a future FFT analysis phase.

**`scipy.stats`** — `linregress` for trend slopes, `zscore` for outlier flagging, confidence intervals.

**`pandas`** — time-indexed DataFrames for multi-session stroke time history. CSV export.

### 13.2 Trend and Degradation Detection Phase

**CUSUM (pure numpy)** — detects sustained shift in stroke time. Produces a boolean flag per session — clean input for a pass/fail alert in the UI. Implemented in `analysis/cylinder_analysis.ipynb`.

**`ruptures`** (micropip-installable) — dedicated changepoint detection for identifying *when* a cylinder started degrading.

### 13.3 ML Phase (Future)

**`scikit-learn`** — available in Pyodide. Isolation Forest for unsupervised anomaly detection across cylinders. Linear regression for wear curve projection.

### 13.4 Recommended Implementation Order

| Priority | Package / Algorithm | Pipeline Stage |
|---|---|---|
| **Now** | `scipy.signal.find_peaks` | `detector.py` batch path |
| **Now** | `scipy.signal.welch` | JupyterLab analysis |
| **Now** | `scipy.stats.linregress` | JupyterLab analysis |
| **Post-cylinder validation** | `pandas` | Data logging |
| **Post-logging** | CUSUM (numpy only) | `detector.py` |
| **Post-logging** | `ruptures` | JupyterLab analysis |
| **ML phase** | `scikit-learn` | JupyterLab / PWA |

---

## 14. Measurement Value — Sync and Degradation

### 14.1 Sync Interpretation (Primary Goal)

| Observation | Action |
|---|---|
| One cylinder starts or ends outside sync window | Adjust flow control valve on that cylinder |
| All cylinders within sync window | Pass — no adjustment needed |
| High shot-to-shot SD on one cylinder | Recheck mounting before adjusting valve |
| Valve-to-cylinder lag differs across cylinders | Investigate pneumatic supply routing |

### 14.2 Degradation Interpretation (Future Goal)

| Observation | Interpretation |
|---|---|
| Gradual increase in ΔT over weeks | Seal wear, increased friction |
| Sudden step change in ΔT | Damage, contamination, pressure change |
| One cylinder slower than others | Investigate that specific unit |
| All cylinders consistent and within spec | System healthy |
| High SD across 10 runs | Inconsistent pressure supply or mounting issue |

### 14.3 Additional Degradation Metrics (Future)

- **T_start signal energy** — breakaway burst amplitude may decrease as seals wear, appearing before stroke time changes
- **T_end impact sharpness** — rise time of T_end spike may broaden with wear
- **Return stroke timing** — extend vs retract comparison may reveal directional seal wear
- **Inter-cylinder ratio** — each cylinder relative to fleet mean normalizes out pressure fluctuations

### 14.4 Temperature Compensation (Future)

Cylinder stroke speed varies with air viscosity, which varies with temperature. A cheap BLE temperature sensor near the cylinders plus a correction factor in `detector.py` would remove temperature as a confounding variable in long-term trend analysis.

---

## 15. User-Defined Requirements

> **Note:** Items in this section are explicit requirements defined by the user/developer. They are not AI-generated suggestions.

### 15.1 [USER REQUIREMENT] PSI Recording

Every measurement session must record the supply pressure (PSI) at the time of measurement.

**Rationale:** Cylinder stroke speed is directly affected by supply pressure. Without a PSI reading it is impossible to distinguish genuine cylinder degradation from a pressure regulator adjustment.

**Implementation:**
- Single PSI entry field in the PWA UI — technician reads the gauge and types it in before starting
- **Start button is gated** — disabled until the PSI field has a value
- PSI is stored per session alongside stroke time, SD, and cylinder ID
- Date and time are auto-stamped by the app — no manual entry

**UI flow:**
1. Select cylinder (1–6)
2. Enter PSI (required)
3. Date/time stamped automatically
4. Start button unlocks → calibration runs → ready to fire

### 15.2 [USER REQUIREMENT] Calibration Report

When acceptance criteria are defined, the system must produce a formal calibration report.

**Rationale:** A documented, reproducible output is required for maintenance records and/or engineering sign-off.

**Format and content:** TBD — to be defined once acceptance criteria are established.

**Likely content (placeholder):**
- Date and time of calibration session
- Cylinder IDs tested
- PSI at time of test
- Stroke time measurements (raw + mean + SD)
- Pass/fail status against defined criteria
- Technician ID or notes field
- App version and sensor configuration used

---

## 16. Open Items

**Hardware:**
- [ ] CM28 Base acceptance test on arrival (mandatory — see Section 5.2)
- [ ] Confirm number of bottom cylinders (at least 1, possibly 2)
- [ ] Source neodymium disc magnets (10–15mm, N52) and thin steel adhesive plates
- [ ] Identify which cylinder will serve as the primary reference
- [ ] Define sync window tolerance (all cylinders must start/end within X ms)
- [ ] Confirm min/max stroke speed spec

**Software — post-cylinder-validation:**
- [ ] Tune HF Floor from real cylinder hfEnergy data
- [ ] Tighten MIN/MAX lookback window from real stroke time data
- [ ] PSI entry field in UI — manual entry, stored per session, gates Start button
- [ ] Cylinder selection (1–6) in UI
- [ ] Data logging / export (CSV, include PSI per session)
- [ ] Trend view across multiple sessions
- [ ] CUSUM pass/fail alert in UI
- [ ] Webhook / Teams / Slack alert when CUSUM flags degradation
- [ ] Calibration report generation — format and content TBD (Section 15.2)
- [ ] Test on Android Chrome
- [ ] Test on iPhone Safari — T_start detectability unconfirmed on iOS

**Analysis — post-logging:**
- [ ] Inter-cylinder ratio tracking (relative to fleet mean)
- [ ] Maintenance event logging (seal replacements, service dates)
- [ ] `ruptures` changepoint detection on stroke time trend
- [ ] `scikit-learn` isolation forest for cross-cylinder anomaly detection
- [ ] Frequency domain features (PSD, mean frequency) from `scipy.signal.welch`

**Infrastructure:**
- [ ] Resolve PWA offline limitation (Pyodide CDN dependency)
- [ ] Temperature compensation — BLE sensor + correction factor in detector.py

**Open questions:**
- [ ] Calibration report format: PDF, printed HTML, or exportable data?
- [ ] Acceptance criteria: who defines pass/fail thresholds and on what basis?
- [ ] Webhook alerts: is Teams or Slack available in the target environment?

---

## 17. Hardware Shopping List

| Item | Specification | Estimated Cost | Source |
|---|---|---|---|
| NEEWER CM28 Base | Dual USB-C wireless mic, 2.4 GHz, NR toggle, true stereo | ~$60 | Amazon — **ordered** |
| Neodymium disc magnets | 10–15 mm diameter, N52 grade | ~$8–12 (pack) | Amazon |
| Thin steel adhesive plates | "Phone magnet plates," <1 mm thick | ~$5–8 (pack) | Amazon |
| USB-C audio adapter (optional) | If using wired piezo fallback | ~$8–15 | Amazon |
| Murata 7BB-35-3L0 (optional) | Piezo disc for wired fallback | ~$1.50 each | Mouser Electronics |

**Total estimated cost (wireless path):** ~$75–100
**Total estimated cost (wired piezo fallback only):** ~$15–25

---

## 18. Empirical Validation Log

### 18.1 S22U Smartphone Tap Test (May 11, 2026)

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

### 18.2 Laptop Mic Device Troubleshooting (May 11, 2026)

| Device | API | Outcome |
|---|---|---|
| 23 — Intel Smart Sound | WASAPI | Failed — exclusive mode conflict |
| 2 — Intel Smart Sound | MME | Failed — channel count mismatch |
| 0 — Microsoft Sound Mapper | MME | Worked — routed to Jabra (wrong device) |
| **27 — Realtek HD Audio Mic** | **WDM-KS** | **Working — correct device** |

### 18.3 Multi-Shot 10-Tap Test — JupyterLab (May 11, 2026)

| Parameter | Value |
|---|---|
| Taps recorded | 10 |
| Clean deltas | 9 |
| Mean | 816.5 ms |
| SD | 31.5 ms |
| CV | 3.86% |

SD of 31.5 ms represents human tapping variability, not measurement error.

### 18.4 PWA Live Mic Test — Initial (May 12, 2026)

| Parameter | Value |
|---|---|
| Platform | Chrome browser, Windows laptop |
| Audio pipeline | Web Audio API → AudioWorklet → Pyodide |
| Sample rate | 48,000 Hz |
| Baseline RMS | 0.0189 |
| Working threshold | 5× baseline |

### 18.5 PWA Multiplier Tuning (May 12, 2026)

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

### 18.6 PWA 5-Set Tap Test — POC Validation (May 12, 2026)

| Cycle | Delta (ms) | Speed (in/s) |
|---|---|---|
| 1 | 266 | 3.759 |
| 2 | 268 | 3.731 |
| 3 | 270 | 3.704 |
| 4 | 261 | 3.831 |
| 5 | 298 | 3.356 |

**Mean delta:** 272.6ms | **SD:** 14ms | **CV:** 5.1%

**POC conclusion:** Full pipeline validated end-to-end on laptop mic. Ready for cylinder hardware validation.

### 18.7 Code Review — Bug Fixes Applied (May 12, 2026)

| Bug | Severity | Fix |
|---|---|---|
| Ring buffer injected via string interpolation — NaN/Infinity risk | High | Replaced with `pyodide.globals.set()` |
| Ring buffer not cleared between spikes — stale entries accumulate | High | Added `tracker.ring_buffer.clear()` before each injection |
| Calibration passed RMS value as timestamp | Medium | Fixed to use `audioCtx.currentTime` |
| Debounce not synced to worklet on settings change | Medium | `applyReset()` now sends `set_debounce` to worklet |
| Worklet debounce hardcoded at 50ms — ignored `processorOptions` | Medium | Fixed to read `debounceMs` from `processorOptions` at construction |

Service worker cache bumped to `cyl-v5`.

### 18.8 BY-V30 Hardware Mono Confirmed (May 18, 2026)

Acceptance test performed: one TX blocked, tap applied to other TX. Both L and R channels in Audacity showed identical waveforms. Hardware mono mix confirmed — not a software setting. CM28 Base ordered as replacement. BY-V30 retained for Tuesday validation session in mono mode.

---

## 19. Future Ideas and Platform Generalization

### 19.1 Multi-Cylinder Simultaneous Measurement

With 4 wireless sensors and coincidence detection it may be possible to fire all cylinders simultaneously and use time-of-arrival differences to attribute each spike to a specific cylinder. Technically ambitious — worth exploring once the roving mic protocol is validated.

**4-channel options:**
- **2× CM28 Base (~$120):** Two independent systems, sync via finger-snap clapperboard method. Millisecond offset between systems is possible.
- **COMICA Vimo Q (~$200–249) + 4-channel USB interface (~$200):** True 4-channel from one system, inherently time-synced. ~$400–450 total.

### 19.2 Reference Firing Baseline Calibration

Perform a known reference firing at the start of each session. Use that measurement to auto-scale thresholds for the session. Accounts for sensor mounting variation between sessions.

### 19.3 Platform Generalization

The physical principle validated by this project — contact acoustic timing of a mechanical event against a fixed end stop — is not specific to pneumatic cylinders. The same PWA with configurable stroke length and expected timing range could monitor hydraulic cylinders, solenoid valves, relay contactors, or any actuator with a metal body, a definable start event, and a definable end event.

### 19.4 Nerf Gun as Validation Proxy

A spring or air-powered Nerf blaster is a pneumatic cylinder. The physics are identical — plunger breaking free (T_start analog) then slamming into the end cap (T_end analog). Mounting both CM28 transmitters on the blaster body and firing 10 shots is the best available dress rehearsal before Tuesday's cylinder validation. NR must be OFF. See `docs/appendix/Appendix_Science_Experiments.md` for full setup and analysis code.

---

*Document compiled from Claude and Gemini conversations (May 10–18, 2026) plus empirical validation sessions, research sessions, and hardware evaluation.*

*Version 6.0 — 2026-05-18. Supersedes v5.0. Key changes: primary goal updated to synchronization; CM28 Base adopted as primary hardware (BY-V30 hardware mono confirmed); seven-phase roving mic measurement protocol added (Section 9); cylinder count updated to 5–6; PSI requirement refined to single field gated on Start button; notebook updated to v2 (live recording, session logging, CUSUM, trend plot, inter-cylinder ratio); Section 14 reorganized around sync primary / degradation secondary; hardware appendix referenced.*
