# Research Note — Science Experiments with the BY-V30 Contact Microphones
**Date:** 2026-05-15
**Project:** Pneumatic Cylinder Stroke Measurement
**Status:** Weekend preparation + future experiments — informational

---

## Most Important — Nerf Gun as Cylinder Analog

### Why This Matters

A spring or air-powered nerf blaster is a **pneumatic cylinder**. The physics are identical to the industrial cylinders being measured on Tuesday. This makes the nerf gun the single best weekend preparation tool available.

**Direct mapping:**

| Nerf Blaster | Industrial Cylinder |
|---|---|
| Plunger breaking free from compressed position | T_start — breakaway burst |
| Spring/air pressure overcoming static friction | Air pressure overcoming seal friction |
| Plunger slamming into front end cap | T_end — end-stop impact |
| Plastic blaster body | Metal cylinder body |
| Repeating trigger pull | Repeating solenoid fire |
| Shot-to-shot SD | Cycle-to-cycle SD across 10 measurements |

**Both events transmit through the blaster body to the sensors:**
- T_start burst — complex multi-spike breakaway signal
- T_end impact — sharp clean spike as plunger hits end cap
- Delta between them = plunger stroke time

### Setup

Mount both BY-V30 transmitters on the blaster body — one near the back of the plunger tube, one near the front end cap. Fire without a dart. Record both channels. Look for T_start burst followed by T_end spike on both channels simultaneously.

**NR must be OFF (Blue light)** — the blaster produces a complex signal that NR processing will mangle, suppressing T_start entirely.

### Why It's Better Than a Random Household Object

- Repeating actuator you control completely
- Definable stroke length measurable with a ruler
- Fire 10 times and measure SD — identical to the Tuesday cylinder protocol
- Stroke time will be in a similar millisecond range to the real cylinders
- Dress rehearsal for Tuesday with the actual sensors and PWA pipeline

### What Tuesday Will Be Different

Metal body transmits vibration much more efficiently than plastic. Real cylinder signals will likely be significantly stronger and cleaner than the nerf gun signals. If detection works on plastic it will work better on metal.

### Nerf Dart Speed Measurement

An extension of the same experiment — measure the dart's muzzle velocity using the two sensors as a chronograph.

**Setup:** Two acoustic gates a known distance apart (2 feet recommended). Dart flies through gate 1 then gate 2. Time delta divided by distance gives speed.

**The math at typical nerf velocities (50–100 ft/sec):**

At 70 ft/sec across 2 feet: delay = 28.6ms — very comfortable at 48kHz sample rate.

**Gate options:**
- Toilet paper tubes taped end to end — dart flies through, sensors clamped to outside
- Thin paper membranes stretched across hoops — dart punches through each
- Tissue paper flags hanging across dart path against a coupled surface

**JupyterLab analysis:**

```python
import numpy as np
from scipy.signal import find_peaks

def measure_dart_speed(recording, sr=48000, gate_distance_ft=2.0):
    ch0 = recording[:, 0]
    ch1 = recording[:, 1]

    peaks0, _ = find_peaks(np.abs(ch0), height=threshold, distance=100)
    peaks1, _ = find_peaks(np.abs(ch1), height=threshold, distance=100)

    if len(peaks0) == 0 or len(peaks1) == 0:
        return None

    delay_samples = peaks1[0] - peaks0[0]
    delay_seconds = delay_samples / sr

    speed_fps = gate_distance_ft / delay_seconds
    speed_mph = speed_fps * 0.6818

    print(f"Delay: {delay_seconds*1000:.2f}ms")
    print(f"Speed: {speed_fps:.1f} ft/sec = {speed_mph:.1f} mph")
    return speed_fps, speed_mph
```

**Interesting extensions:**
- Muzzle velocity vs range — plot deceleration curve, fit drag coefficient
- Compare different dart types (standard, elite, mega)
- Compare different blasters
- Shot-to-shot consistency — SD of 10 shots directly analogous to cylinder SD
- Temperature effect on spring-powered blasters

### Nerf Target Plate Hit Detection and Position Estimation

Mount both sensors at opposite corners of a plywood backing board. Attach paper or plastic plates as targets. Dart impacts transmit through the board to both sensors.

**Hit detection:** Immediate — same spike detection pipeline as the cylinder project, zero code changes needed.

**Plate discrimination with 2 sensors:**

| Shot location | Channel behavior |
|---|---|
| Near Transmitter 1 | Ch1 higher amplitude, fires first |
| Center | Both channels equal amplitude, simultaneous |
| Near Transmitter 2 | Ch2 higher amplitude, fires first |

Three plates along a line are distinguishable by amplitude ratio and time delay direction. Four or more start to get ambiguous in the middle zone.

**Time delay calculation:**

Speed of sound in plywood ~13,000 ft/sec. On a 2-foot board, sensor-to-plate path differences produce delays of ~77 microseconds = ~3-4 samples at 48kHz. Marginal for timing alone — use amplitude ratio as primary discriminator, time delay direction as confirmation.

**Simple classifier in Python:**

```python
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# Features: [amplitude_ch1, amplitude_ch2, amplitude_ratio, time_delay_ms]
X_train = np.array([
    [0.8, 0.2,  4.0, -0.08],   # Plate A — T1 louder, fires first
    [0.5, 0.5,  1.0,  0.00],   # Plate B — equal
    [0.2, 0.8,  0.25, 0.08],   # Plate C — T2 louder, fires first
])
y_train = ['A', 'B', 'C']

clf = KNeighborsClassifier(n_neighbors=1)
clf.fit(X_train, y_train)

# Classify new shot
new_shot = np.array([[0.75, 0.25, 3.0, -0.07]])
print(clf.predict(new_shot))  # → ['A']
```

**Weekend build:** Mount sensors on opposite corners of plywood, attach 3 plates evenly spaced, fire 5 calibration shots at each plate, plot amplitude ratio clusters — should separate cleanly into 3 groups.

---

## Vehicle Speed Measurement

### Time-of-Flight Method

Two sensors mounted on a curb or metal surface a known distance apart. Vehicle passes sensor 1 then sensor 2. Time delta divided by sensor spacing gives speed — same architecture as the cylinder T_start/T_end detection but spatially separated.

**The math:**
- Sensors 10 feet apart
- Car at 30mph (44 ft/sec): delay = 227ms — very comfortable
- Car at 60mph (88 ft/sec): delay = 114ms — still clean

**Best coupling surfaces:** Concrete curb, metal drain cover, manhole cover, steel guardrail. Asphalt is uncertain — more damping.

**Calibration:** Walk past at known pace (3mph), then bicycle, then car. Build speed curve from slow to fast.

**Extensions:**
- Vehicle length estimation from axle timing
- Direction detection — Ch1 fires first for northbound, reversed for southbound
- Traffic counting over time

### Doppler Method

As a car approaches, tire contact patch repetition rate is compressed (higher frequency). As it recedes, it stretches (lower frequency). The ratio gives speed independent of sensor spacing.

**Tire pulse rate** = vehicle speed / tire circumference. Typical tire circumference ~6.5 feet.
- At 30mph (44 ft/sec): ~6.8 Hz
- At 60mph (88 ft/sec): ~13.5 Hz

**Analysis:** Spectrogram shows dominant frequency sweeping downward as car passes.

```python
from scipy.signal import spectrogram

f, t, Sxx = spectrogram(signal, fs=sample_rate, nperseg=512)
# Watch dominant low-frequency peak shift from higher to lower as car passes

# Speed from frequency ratio:
# v = c × (f_approach - f_recede) / (f_approach + f_recede)
```

**Best sources:** Loud exhaust, diesel engine, motorcycle — stronger tonal components in 50-200 Hz range where mics respond well.

**The interesting combination:** Run both time-of-flight and Doppler simultaneously on the same recording. Two independent physics-based methods on the same event. If they agree, you've cross-validated with commodity hardware.

---

## Rotational Balance Measurement

### Ceiling Fan

Mount both transmitters on the motor housing 90° apart. A balanced fan produces low-amplitude broadband vibration. An out-of-balance fan produces a strong periodic signal at blade-pass frequency.

**Test:** Record both channels while fan runs at fixed speed. FFT the signal — imbalance shows up as a spike at rotation frequency. Tape a penny to one blade and repeat — watch the imbalance peak grow.

**Phase difference** between the two channels tells you the angular position of the imbalance — which blade is heavy.

This is the most immediately achievable rotational experiment — ceiling fan is right there, setup takes minutes, result is clear.

### General Rotating Machinery

Any rotating shaft with bearings — bench grinder, drill press, skateboard wheel in a vise. Healthy bearing = broadband low-amplitude noise. Worn bearing = characteristic frequency spikes at ball pass frequency and inner/outer race frequency multiples.

---

## Structural and Material Science

### Resonant Frequency of Objects

Strike any object and record the decay ringdown. FFT gives the object's natural resonant frequencies. Different materials have characteristic signatures — steel vs aluminum vs cast iron vs wood all produce distinct frequency fingerprints.

Good objects to try: wine glass, metal pipe, wooden beam, ceramic mug, wrench.

### Crack Detection

An intact object and a cracked object of the same type ring differently when struck — the crack damps certain frequencies and introduces asymmetry. This is the industrial principle behind hammer tap testing of aircraft panels and concrete. Test with a ceramic mug vs a chipped one.

### Speed of Sound in Materials

Mount one transmitter at each end of a long metal pipe or wooden beam. Strike one end sharply. Measure the time delay between spike on channel 1 and arrival on channel 2. Divide length by delay — speed of sound in that material.

**Reference values:**
- Steel: ~16,400 ft/sec
- Aluminum: ~16,700 ft/sec
- Wood (along grain): ~10,000–13,000 ft/sec
- Concrete: ~10,000–13,000 ft/sec

Quick and gives a satisfying quantitative result that you can verify against published values.

### Loose Joint Detection

Run a power tool or motor near various joints, connections, and fasteners. Loose ones rattle at specific frequencies. Both sensors help distinguish structure-borne from airborne noise via coincidence detection.

### Wood Quality Assessment

Tap along a wooden beam at regular intervals. Voids, knots, and delamination change the resonant response. Same principle used to inspect wooden utility poles and timber structures.

---

## Physics Experiments

### Pendulum Period Measurement

Hang a weight on a string from a rigid mount with a sensor attached. Each swing produces a tiny impulse at the mount point. Spike detection measures the period automatically to millisecond precision — much more accurate than a stopwatch.

Verify the pendulum relationship: T = 2π√(L/g) with high accuracy.

### Spring Constant Measurement

Mount sensor on a surface, attach a spring vertically, hang known weights, release from stretch. Oscillation frequency gives spring constant: f = (1/2π)√(k/m).

### Impact Force Estimation

Drop known weights from known heights onto a surface with a sensor. Spike amplitude and duration correlate with impact force. With calibration against a known force, builds a rough impact force meter.

---

## Acoustic Experiments

### Room Reverberation Time

Use one mic as a contact sensor on a wall. Clap sharply. Measure RT60 — the time for sound to decay 60dB. Different rooms and surface materials have characteristic reverberation signatures.

### Acoustic Direction Finding

Place both sensors a known distance apart on a flat surface. A tap closer to sensor 1 arrives on channel 1 first. Time delay gives direction of source — basic acoustic triangulation. On a tabletop you could locate a tap position to within a few centimeters.

### Fluid Flow in Pipes

Press a sensor against a water pipe before and after opening a valve. Turbulent flow vs laminar flow have different acoustic signatures. A slow leak produces broadband high-frequency hiss detectable through the pipe wall — same principle as industrial leak detection.

---

## Engineering Diagnostics

### Belt Tension

A loose belt on any driven machine produces periodic slap at belt-pass frequency. Pluck a drive belt like a guitar string and measure the fundamental frequency — directly related to tension.

### Bearing Condition

Spin any shaft with bearings. Record and FFT. Characteristic frequencies:
- Ball pass frequency outer race (BPFO)
- Ball pass frequency inner race (BPFI)
- Ball spin frequency (BSF)

A worn bearing shows energy at these specific frequencies that a healthy bearing does not.

---

## Connection Back to the Cylinder Project

Every experiment above builds directly relevant skills:

| Experiment | Skill transferred to Tuesday |
|---|---|
| Nerf gun plunger | T_start/T_end detection on plastic — dress rehearsal |
| Dart chronograph | Sequential channel triggering — same as time-of-flight speed |
| Target plate discrimination | Amplitude ratio + delay as position classifier |
| Ceiling fan balance | FFT peak identification at known frequency |
| Speed of sound | Structure-borne propagation timing — same physics as cylinder body |
| Resonant frequency | Material characterization — understand cylinder body behavior |
| Room acoustics | Ambient noise baseline understanding |
| Bearing detection | Frequency domain wear signatures — future cylinder FFT phase |

The nerf gun experiment is the most important this weekend. Everything else is bonus.

---

*Note compiled May 15, 2026. All experiments use the Boya BY-V30 dual wireless contact microphone system. NR must be OFF (Blue light) for all experiments involving transient mechanical events.*
