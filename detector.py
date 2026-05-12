import numpy as np
import time
from datetime import datetime
from collections import deque

SAMPLE_RATE       = 48000
CHUNK_MS          = 10
MULTIPLIER        = 10
DEBOUNCE_MS       = 50
MAX_CYCLE_MS      = 3000
MIN_CYCLE_MS      = 3
DEFAULT_STROKE    = 1.0
CHUNK_SAMPLES     = int(SAMPLE_RATE * CHUNK_MS / 1000)

CAL_DURATION_S    = 1.5
ADAPTIVE_WINDOW_S = 5.0
CAL_CHUNKS_NEED   = int(CAL_DURATION_S * 1000 / CHUNK_MS)
ADAPTIVE_CHUNKS   = int(ADAPTIVE_WINDOW_S * 1000 / CHUNK_MS)


class CycleTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.baseline      = None
        self.cal_rms       = []
        self.cal_done      = False
        self.rms_history   = deque(maxlen=ADAPTIVE_CHUNKS)
        self.last_spike_t  = None
        self.cycle_start_t = None
        self.cycles        = []
        self.stroke_in     = DEFAULT_STROKE
        self.multiplier    = MULTIPLIER
        self.debounce_ms   = DEBOUNCE_MS

    def process(self, samples):
        rms = float(np.sqrt(np.mean(np.array(samples, dtype=np.float32) ** 2)))

        # Always push to rolling history
        self.rms_history.append(rms)

        if not self.cal_done:
            self.cal_rms.append(rms)
            if len(self.cal_rms) >= CAL_CHUNKS_NEED:
                self.baseline = float(np.percentile(self.cal_rms, 80))
                self.cal_done = True
                return 'ready', None
            pct = int(len(self.cal_rms) / CAL_CHUNKS_NEED * 100)
            return f'cal:{pct}', None

        # Continuously update baseline from rolling window,
        # but only when not mid-cycle (prevents spike contamination)
        if self.cycle_start_t is None and len(self.rms_history) >= CAL_CHUNKS_NEED:
            self.baseline = float(np.percentile(self.rms_history, 80))

        threshold = self.baseline * self.multiplier
        if rms < threshold:
            return 'listen', None

        now = time.time()
        if self.last_spike_t and (now - self.last_spike_t) * 1000 < self.debounce_ms:
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


tracker = CycleTracker()


def process_chunk(samples):
    status, cycle = tracker.process(samples)
    if cycle:
        return status, cycle['n'], cycle['delta_ms'], cycle['speed'], cycle['ts']
    return status, None, None, None, None


def reset_tracker(stroke_in=1.0, multiplier=10, debounce_ms=50):
    tracker.reset()
    tracker.stroke_in   = stroke_in
    tracker.multiplier  = multiplier
    tracker.debounce_ms = debounce_ms


def get_cycles():
    return [(c['n'], c['delta_ms'], c['speed'], c['ts']) for c in tracker.cycles]


def get_baseline():
    return tracker.baseline
