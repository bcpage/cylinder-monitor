# Appendix — Wireless Microphone Hardware Research and Evaluation
**Date:** 2026-05-15
**Project:** Pneumatic Cylinder Stroke Measurement
**Status:** Research complete — purchase decision pending
**Purpose:** Hardware evaluation for dual-channel contact acoustic sensing. To be included as an appendix in the final project report.

---

## Background — Why Hardware Matters

The project requires two independent wireless contact microphone channels — one sensor mounted on the pneumatic valve, one on the cylinder body. The two channels must be:

1. **Truly independent L/R channels** — not a mono mix duplicated to both channels
2. **NR (noise reduction) off** — consumer voice-optimised DSP will suppress or distort T_start transient spikes
3. **No AGC (automatic gain control)** — amplitude information is a primary measurement domain; AGC destroys it
4. **Manual gain control** — fixed gain needed for repeatable amplitude comparison across sessions

---

## The BY-V30 Problem — Why This Research Was Triggered

The project originally specified the Boya BY-V30 as the primary sensor hardware. Claude Code identified a critical hardware limitation during the validation session:

**Test performed:** One TX physically blocked, tap applied to the other TX. Both L and R channels in Audacity showed identical waveforms before export.

**Conclusion:** The BY-V30 RX hardware combines both TX inputs into a single mono signal and duplicates it to both L and R of the USB output. This is a hardware architecture decision, not a software setting. No app exists for the BY-V30 and no firmware path to separate the channels.

**What the BY-V30 can still do:**
- All timing domain measurements remain valid — stroke time, T_zero, T_start, T_end, pneumatic lag
- The combined mono signal preserves timing relationships between events from both sensors
- The two valve click arrivals (one from each TX) appear as two separate spikes in the mono signal with a measurable propagation delay — enabling timing-based coincidence detection
- Signal deconvolution using known inter-sensor distance may allow approximate channel separation in post-processing

**What is lost:**
- Amplitude ratio between channels
- True hardware coincidence detection (multiplicative method)
- Independent per-channel SNR measurement

**Status:** BY-V30 retained for Tuesday validation session in mono mode. Replacement hardware research initiated.

---

## Key Requirements for Replacement Hardware

| Requirement | Reason |
|---|---|
| True stereo — separate L/R per TX | Core measurement architecture requirement |
| NR off confirmed | Voice-gate NR suppresses T_start transient |
| No AGC or limiter in normal operation | Amplitude is a primary measurement domain |
| Manual gain control | Repeatable amplitude comparison across sessions |
| USB-C output preferred | Direct laptop connection, no adapter |
| 48kHz sample rate | Already validated in project pipeline |
| Price target | Under $100 preferred, under $150 acceptable |

---

## Safety Track — Definition

Safety Track (also called MS mode) is a recording mode where both channels carry audio but at different gain levels — typically the main channel at normal gain and the second channel at -6dB to -20dB lower. It provides a backup recording for clipping events. **Not useful for this project** — it duplicates one signal at two levels rather than recording two independent sensors independently.

---

## Products Evaluated

### RØDE Wireless GO II — ~$150–184

| Feature | Status |
|---|---|
| True stereo | ✅ Hardware L/R per TX — switchable via button or RØDE Central app |
| NR off | ✅ No onboard NR — RØDE design philosophy is clean signal |
| AGC | ✅ Manual gain only — 10-stage pad, -0dB to -30dB via RØDE Central |
| USB-C output | ✅ |
| Sample rate | 24-bit / 48kHz |
| Range | 200m |
| Price | ~$150–184 |

**Notes:** The gold standard for confirmed true stereo at this price range. Manual gain with no AGC, no NR processing. Design philosophy is "clean signal, process in post" — directly aligned with project requirements. Available on sale periodically at ~$150. Used units available ~$120–140.

**Verdict:** Best option if budget extends to $150. Confirmed true stereo, no processing, manual gain.

---

### DJI Mic Mini (2TX + 1RX + Charging Case) — ~$79

| Feature | Status |
|---|---|
| True stereo | ✅ TX1 to Left, TX2 to Right — confirmed in product FAQ |
| NR off | ✅ Two levels plus off |
| AGC | ⚠️ Automatic limiting active — reduces gain at clipping threshold only |
| USB-C output | ✅ |
| Sample rate | 48kHz |
| Range | 400m |
| Price | ~$79 |

**Notes:** Stereo separation confirmed at hardware level. NR off confirmed. The automatic limiting is the one concern — described as preventing clipping rather than compressing dynamic range, so it may only activate at extreme signal levels above normal cylinder impact amplitudes. Manual gain dial on receiver. Strong value at $79.

**Verdict:** Strong option under $100. Run Audacity block test on arrival. If limiting does not affect transient spikes at normal cylinder signal levels, this is suitable.

---

### NEEWER CM28 Base — ~$60

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
| SNR | Unconfirmed |
| Range | 200m |
| Price | ~$60 |

**Notes:** Best documented value option in the entire search. Stereo confirmed in manual and by independent reviewer. NR has a confirmed off state — not just level control. Low cut filter independently switchable from NR. TX standalone recording enables coworker deployment without a laptop. No AGC mentioned anywhere. 16-bit is sufficient for transient spike detection.

**Verdict: Recommended purchase.** Run Audacity block-one-mic test on arrival as standard acceptance test.

---

### NEEWER CM28 Pro — ~$72–90

| Feature | Status |
|---|---|
| True stereo | ✅ |
| NR off | ✅ |
| AGC | ✅ Not mentioned |
| Manual gain | ✅ 5-level |
| Low cut filter | ✅ 75/150Hz/OFF |
| TX standalone recording | ✅ 4GB / 9hrs |
| Sample rate | 48kHz / 16-bit |
| SNR | 87dB confirmed |
| Range | 200m |
| Price | ~$72–90 |

**Notes:** Based on all research, the Pro is essentially the same hardware as the base in a slightly more compact form factor with a confirmed 87dB SNR spec. Range is 200m on both — not 300m as some listings suggest. The additional cost is not justified for this project's requirements.

**Verdict:** Pass. CM28 Base covers all requirements at lower cost.

---

### NEEWER CM28 Max — ~$100–120

| Feature | Status |
|---|---|
| True stereo | ✅ |
| NR off | ✅ |
| AGC | ✅ Not mentioned |
| Manual gain | ✅ 5-level |
| Low cut filter | ✅ 75/150Hz/OFF |
| TX standalone recording | ✅ 4GB / 9hrs |
| Sample rate | ✅ **48kHz/24-bit float OR 16-bit — switchable** |
| SNR | 87dB confirmed |
| Range | **300m** |
| Price | ~$100–120 |

**Notes:** The standout upgrade from base is the switchable 24-bit float recording. 24-bit float cannot clip regardless of signal level — if T_end is very loud relative to T_start, float recording captures both without clipping either. This is genuinely useful for transient acoustic measurement. 300m range is irrelevant for this application.

**Verdict:** Worth considering if budget extends to ~$110. The 24-bit float is a meaningful advantage over the base for transient spike measurement. Not essential but useful.

---

### NEEWER CM31 — ~$100–120

| Feature | Status |
|---|---|
| True stereo | ✅ |
| NR off | ✅ |
| AGC | ✅ Not mentioned |
| Manual gain | ✅ **15-level** |
| TX standalone recording | ✅ **8GB / 9hrs** |
| Sample rate | 48kHz / 24-bit |
| Range | 300m |
| Price | ~$100–120 |

**Notes:** 15-level gain control is significantly finer than the 5-level on the CM28 family — more precise tuning to cylinder signal levels. 8GB storage doubles standalone recording capacity. 24-bit sample rate. Similar price to CM28 Max.

**Verdict:** Strong alternative to CM28 Max at the same price point. 15-level gain is the differentiator.

---

### NEEWER CM26 Pro — ~$50–70

| Feature | Status |
|---|---|
| True stereo | ✅ |
| NR off | ✅ |
| AGC | ❌ **Always-on AGC and distortion limiter confirmed** |
| Sample rate | 48kHz / 24-bit |
| TX standalone recording | ❌ Not mentioned |
| Price | ~$50–70 |

**Notes:** Eliminated by always-on AGC. The distortion limiter and AGC are described as always-active features in the signal chain. AGC will compress T_start transients and distort amplitude information. No TX standalone recording.

**Verdict: Rejected.** AGC in signal path is a disqualifying feature for this project.

---

### NEEWER KM19 — ~$50–70

| Feature | Status |
|---|---|
| True stereo | ✅ |
| NR off | ✅ |
| AGC | ✅ Not mentioned |
| Transmission | ⚠️ **Bluetooth to phone** |
| TX standalone recording | ❌ |
| Price | ~$50–70 |

**Notes:** Uses Bluetooth for TX-to-phone connection. Bluetooth packet drops (~10ms gaps) are a disqualifying feature — one dropped packet can swallow T_start entirely. The project plan documents this as a hard rejection criterion.

**Verdict: Rejected.** Bluetooth transmission incompatible with transient spike detection.

---

### Hollyland Lark M2 — ~$100–130

| Feature | Status |
|---|---|
| True stereo | ⚠️ Stereo confirmed via 3.5mm to camera — **not via USB-C to phone/laptop** |
| NR off | ✅ |
| AGC | Unknown |
| Price | ~$100–130 |

**Notes:** Stereo mode is blocked when connected via USB-C to a phone or laptop — only works via 3.5mm to camera. This is a hardware/OS limitation. Requires 3.5mm to USB-C adapter and further investigation before considering.

**Verdict:** Requires further investigation. Stereo via USB-C not confirmed.

---

### SYNCO G2(A2) — ~$70–90

| Feature | Status |
|---|---|
| True stereo | ✅ Stereo mode confirmed — hardware channel routing |
| NR off | Unknown |
| AGC | Unknown |
| Output | 3.5mm TRS — requires USB-C adapter |
| Stereo via phone | ⚠️ Stereo not available for phone recording — camera only |
| Price | ~$70–90 |

**Notes:** Similar limitation to Hollyland — stereo mode only confirmed via camera connection, not phone. Requires USB-C audio adapter for laptop use. Unknown NR and AGC status.

**Verdict:** Uncertain. USB-C adapter path may work for laptop use — needs testing.

---

### Movo WMX-2-DUO — ~$60–80

| Feature | Status |
|---|---|
| True stereo | ✅ Claims L/R per TX |
| NR off | Unknown |
| AGC | Unknown |
| Output | 3.5mm TRS |
| Price | ~$60–80 |

**Notes:** Claims stereo but unverified by independent testing. NR and AGC status unknown. Requires USB-C audio adapter.

**Verdict:** Unverified. CM28 base is better documented at similar price.

---

### Saramonic Blink 500 T4 — ~$250

| Feature | Status |
|---|---|
| True 4 channels | ✅ Via TRRRS splitter cable |
| NR off | ✅ Per TX |
| AGC | Unknown |
| Output | TRRRS splitter → requires 4-channel audio interface |
| Price | ~$250 + 4-channel interface (~$200) |

**Notes:** Only confirmed 4-channel option found. Requires a 4-channel audio interface (e.g., Focusrite Scarlett 4i4) to receive all 4 tracks simultaneously. Total system cost ~$450.

**Verdict:** Best 4-channel option but expensive. Relevant if simultaneous multi-cylinder measurement is pursued (Section 19 of project plan).

---

### COMICA Vimo Q — ~$200–249

| Feature | Status |
|---|---|
| True 4 channels | ✅ In Quad mode — 4 independent tracks |
| NR off | ✅ Button per TX |
| USB-C 4-channel | ❌ USB-C = 2 channels max — Quad requires both 3.5mm outputs |
| Price | ~$200–249 + 4-channel interface |

**Notes:** Only budget 4-channel option with confirmed independent tracks. But Quad mode requires both 3.5mm outputs simultaneously into a 4-channel audio interface — same total system cost issue as the Saramonic.

**Verdict:** Best budget 4-channel option. Requires 4-channel interface for full Quad mode.

---

### Products Rejected Immediately

| Product | Reason |
|---|---|
| Boya BY-V30 (original) | Hardware mono mix — all TX channels combined before USB output. No stereo mode, no app, no fix. |
| Boya BY-V4 | Same architecture as BY-V30 assumed — mono mix likely |
| FULAIM X6 | Dual-channel receiver regardless of transmitter count — documented in original project plan |
| FULAIM X6 Pro | Same architecture as X6 — "dual-channel receiver" confirmed in manufacturer description. NR off confirmed per TX — the one improvement — but channel count unchanged |
| 7RYMS iRay DW40 | "Does not support split-track output" — confirmed in UK Amazon listing. Aggressive AI NR always on |
| SVBONY SVMic D4 | Dual channel only from 4 TX — 2 channels maximum. No confirmed NR off state |

---

## The Standard Acceptance Test

Following the BY-V30 experience, all new wireless microphone hardware must pass this test before being relied upon:

1. Power on both TX units and RX
2. Set to stereo mode
3. Physically block TX1 completely (hand over mic, no sound)
4. Tap TX2 sharply
5. Open Audacity — look at both L and R channels before export
6. **Pass:** Left channel shows nothing, Right channel shows the tap spike
7. **Fail:** Both channels show identical waveforms — hardware mono mix confirmed

This test takes 2 minutes and definitively confirms or rejects true stereo separation at the hardware level.

---

## Recommended Purchase Path

### Immediate — Primary sensor hardware

**NEEWER CM28 Base — ~$60**
Run acceptance test on arrival. If it passes, this is your production sensor hardware. If it fails, return and escalate to CM28 Max or DJI Mic Mini.

### If CM28 Base fails acceptance test

**DJI Mic Mini — ~$79**
Second option. Stereo more thoroughly documented. Run acceptance test regardless.

### If budget extends to ~$110

**NEEWER CM28 Max — ~$110**
24-bit float recording is a meaningful upgrade for transient spike measurement. Switchable between 24-bit float and 16-bit. 87dB SNR confirmed.

### Future — 4-channel simultaneous measurement

**COMICA Vimo Q (~$200–249) + 4-channel USB interface (~$200)**
When simultaneous multi-cylinder measurement is pursued (project plan Section 19). Total system cost ~$400–450.

---

## NR Frequency Response — Important Nuance

Consumer NR in budget wireless mics is almost always voice-optimised. Two types exist:

**Fixed frequency filter** — high-pass and low-pass filter outside the voice band. If the filter stays outside your signal's frequency range, it is harmless and can be left on for factory noise reduction benefit.

**Adaptive voice gate / spectral subtraction** — looks at signal characteristics and suppresses anything that does not resemble a voice. A sharp transient impact spike does not look like a voice and may be suppressed regardless of frequency content.

**Recommended validation:** On the actual cylinder, record one firing with NR ON and one with NR OFF. Compare spike amplitude and waveform shape in Audacity. If identical — NR ON may be left active for factory noise reduction benefit without harming measurement accuracy.

---

## 4-Channel Architecture Notes

Two approaches to 4-channel wireless:

**2× dual-channel systems (e.g., 2× CM28 Base)**
- Total cost: ~$120
- Each system provides stereo L/R independently
- Both USB-C receivers plugged into laptop simultaneously as two separate audio devices
- Sync challenge: two independent recording clocks need sync via finger-snap clapperboard method
- Sample accuracy between systems not guaranteed — millisecond offset possible

**Dedicated 4-channel system (e.g., Saramonic or Comica Vimo Q)**
- Total cost: ~$400–450 including 4-channel interface
- All 4 channels from one system — inherently time-synced
- No clapperboard sync required
- More expensive but operationally simpler

---

## The Finger-Snap Sync Method

When using two independent recording devices (e.g., 2× CM28 Base TX in standalone mode), sync is achieved by:

1. Enable standalone recording on both TX units
2. Hold both TX units physically together — mics within millimeters of each other
3. Snap fingers sharply in front of both
4. Mount TX units at their respective locations and record session
5. In JupyterLab: find the sync snap spike on both recordings, measure sample offset, align

```python
import numpy as np
from scipy.signal import find_peaks

# Find sync snap on both recordings
peaks_tx1, _ = find_peaks(np.abs(tx1_recording), height=threshold)
peaks_tx2, _ = find_peaks(np.abs(tx2_recording), height=threshold)

# Offset in samples
offset_samples = peaks_tx2[0] - peaks_tx1[0]

# Align
if offset_samples > 0:
    tx2_aligned = tx2_recording[offset_samples:]
    tx1_aligned = tx1_recording
else:
    tx1_aligned = tx1_recording[abs(offset_samples):]
    tx2_aligned = tx2_recording
```

Two snaps rather than one — the second confirms the offset measurement.

---

*Research conducted May 15, 2026. Prices are approximate Amazon US prices as of research date and subject to change. All hardware claims should be verified against current manufacturer documentation before purchase. The Audacity acceptance test is mandatory for any new hardware regardless of documented specifications.*
