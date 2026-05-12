import numpy as np
import time
from datetime import datetime

# ── Tuning constants ──────────────────────────────────────────────
SAMPLE_RATE     = 48000
CHUNK_MS        = 10
MULTIPLIER      = 30
DEBOUNCE_MS     = 50
CAL_DURATION_S  = 1.5
MAX_CYCLE_MS    = 3000
MIN_CYCLE_MS    = 3
DEFAULT_STROKE  = 1.0

CHUNK_SAMPLES   = int(SAMPLE_RATE * CHUNK_MS / 1000)

class CycleTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.baseline        = None
        self.cal_rms         = []
        self.cal_done        = False
        self.cal_chunks_need = int(CAL_DURATION_S * 1000 / CHUNK_MS)
        self.last_spike_t    = None
        self.cycle_start_t   = None
        self.cycles          = []
        self.stroke_in       = DEFAULT_STROKE
        self.multiplier      = MULTIPLIER

    def process(self, samples):
        """
        Feed one chunk of float32 samples.
        Returns (status, cycle_dict or None)
        status values:
          cal:N     — calibrating, N = percent complete
          ready     — calibration done, listening
          listen    — below threshold, waiting
          breakaway — first spike detected
          cycle     — full cycle complete, cycle dict returned
          timeout   — gap too long, reset
          noise     — gap too short, ignored
          debounce  — within debounce window, ignored
        """
        rms = float(np.sqrt(np.mean(np.array(samples, dtype=np.float32) ** 2)))

        # ── Calibration ───────────────────────────────────────────
        if not self.cal_done:
            self.cal_rms.append(rms)
            if len(self.cal_rms) >= self.cal_chunks_need:
                self.baseline = float(np.percentile(self.cal_rms, 80))
                self.cal_done = True
                return 'ready', None
            pct = int(len(self.cal_rms) / self.cal_chunks_need * 100)
            return f'cal:{pct}', None

        threshold = self.baseline * self.multiplier

        if rms < threshold:
            return 'listen', None

        # ── Spike detected ────────────────────────────────────────
        now = time.time()

        if self.last_spike_t and (now - self.last_spike_t) * 1000 < DEBOUNCE_MS:
            return 'debounce', None
        self.last_spike_t = now

        if self.cycle_start_t is None:
            self.cycle_start_t = now
            return 'breakaway', None

        delta_ms = (now - self.cycle_start_t) * 1000

        if delta_ms < MIN_CYCLE_MS:
            self.cycle_start_t = now
            return 'noise', None

        if delta_ms > MAX_CYCLE_MS:
            self.cycle_start_t = now
            return 'timeout', None

        speed = (self.stroke_in / delta_ms) * 1000
        cycle = {
            'n':        len(self.cycles) + 1,
            'delta_ms': round(delta_ms, 2),
            'speed':    round(speed, 3),
            'ts':       datetime.now().strftime('%H:%M:%S'),
        }
        self.cycles.append(cycle)
        self.cycle_start_t = None
        return 'cycle', cycle


# Module-level tracker instance
tracker = CycleTracker()

def process_chunk(samples):
    """Called from JavaScript via Pyodide."""
    status, cycle = tracker.process(samples)
    if cycle:
        return status, cycle['n'], cycle['delta_ms'], cycle['speed'], cycle['ts']
    return status, None, None, None, None

def reset_tracker(stroke_in=1.0, multiplier=30):
    tracker.reset()
    tracker.stroke_in  = stroke_in
    tracker.multiplier = multiplier

def get_cycles():
    return [(c['n'], c['delta_ms'], c['speed'], c['ts']) for c in tracker.cycles]
