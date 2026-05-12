import numpy as np
import time
from datetime import datetime
from collections import deque

SAMPLE_RATE        = 48000
CHUNK_MS           = 10
IMPACT_MULTIPLIER  = 10
BREAKAWAY_MULT     = 3
DEBOUNCE_MS        = 50
MAX_LOOKBACK_MS    = 100
MIN_LOOKBACK_MS    = 15
DEFAULT_STROKE     = 1.0

CAL_DURATION_S     = 1.5
ADAPTIVE_WINDOW_S  = 10.0          # default longer window — settable from UI
CAL_CHUNKS_NEED    = int(CAL_DURATION_S  * 1000 / CHUNK_MS)

RING_BUFFER_MS     = 250
RING_BUFFER_CHUNKS = int(RING_BUFFER_MS / CHUNK_MS)

# Baseline percentile — lower = less influenced by noise bursts
BASELINE_PERCENTILE = 50


class CycleTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.baseline           = None
        self.cal_rms            = []
        self.cal_done           = False

        # Adaptive window — size set by reset_tracker()
        self.adaptive_window_s  = ADAPTIVE_WINDOW_S
        adaptive_chunks         = int(self.adaptive_window_s * 1000 / CHUNK_MS)
        self.rms_history        = deque(maxlen=adaptive_chunks)

        self.ring_buffer        = deque(maxlen=RING_BUFFER_CHUNKS)
        self.last_spike_t       = None
        self.cycles             = []

        # Tunable params
        self.stroke_in          = DEFAULT_STROKE
        self.impact_mult        = IMPACT_MULTIPLIER
        self.breakaway_mult     = BREAKAWAY_MULT
        self.debounce_ms        = DEBOUNCE_MS
        self.max_lookback_ms    = MAX_LOOKBACK_MS
        self.min_lookback_ms    = MIN_LOOKBACK_MS
        self.baseline_pct       = BASELINE_PERCENTILE

    def process(self, rms, timestamp_s):
        self.rms_history.append(rms)

        # ── Calibration ───────────────────────────────────────────────────
        if not self.cal_done:
            self.cal_rms.append(rms)
            if len(self.cal_rms) >= CAL_CHUNKS_NEED:
                self.baseline = float(np.percentile(self.cal_rms, self.baseline_pct))
                self.cal_done = True
                return 'ready', None
            pct = int(len(self.cal_rms) / CAL_CHUNKS_NEED * 100)
            return f'cal:{pct}', None

        # ── Adaptive baseline ─────────────────────────────────────────────
        if len(self.rms_history) >= CAL_CHUNKS_NEED:
            self.baseline = float(np.percentile(self.rms_history, self.baseline_pct))

        # ── Ring buffer ───────────────────────────────────────────────────
        self.ring_buffer.append((rms, timestamp_s))

        impact_threshold    = self.baseline * self.impact_mult
        breakaway_threshold = self.baseline * self.breakaway_mult

        if rms < impact_threshold:
            return 'listen', None

        # ── Debounce ──────────────────────────────────────────────────────
        now = timestamp_s
        if self.last_spike_t and (now - self.last_spike_t) * 1000 < self.debounce_ms:
            return 'debounce', None
        self.last_spike_t = now

        # ── Lookback for T_start ──────────────────────────────────────────
        t_end     = now
        t_end_rms = rms
        best_rms  = None
        best_t    = None

        for (chunk_rms, chunk_t) in self.ring_buffer:
            delta_ms = (t_end - chunk_t) * 1000
            if delta_ms < self.min_lookback_ms:
                continue
            if delta_ms > self.max_lookback_ms:
                continue
            if chunk_rms < breakaway_threshold:
                continue
            if best_rms is None or chunk_rms > best_rms:
                best_rms = chunk_rms
                best_t   = chunk_t

        if best_t is None:
            unmatched = {
                'n':          len(self.cycles) + 1,
                'delta_ms':   None,
                'speed':      None,
                'ts':         datetime.now().strftime('%H:%M:%S'),
                'status':     'unmatched',
                'tend_rms':   round(t_end_rms, 6),
                'tstart_rms': None,
                'baseline':   round(self.baseline, 6),
            }
            self.cycles.append(unmatched)
            return 'unmatched', unmatched

        delta_ms = (t_end - best_t) * 1000
        speed    = (self.stroke_in / delta_ms) * 1000

        cycle = {
            'n':          len(self.cycles) + 1,
            'delta_ms':   round(delta_ms, 2),
            'speed':      round(speed, 3),
            'ts':         datetime.now().strftime('%H:%M:%S'),
            'status':     'cycle',
            'tend_rms':   round(t_end_rms, 6),
            'tstart_rms': round(best_rms, 6),
            'baseline':   round(self.baseline, 6),
        }
        self.cycles.append(cycle)
        return 'cycle', cycle


tracker = CycleTracker()


def process_chunk(rms, timestamp_s):
    status, cycle = tracker.process(rms, timestamp_s)
    if cycle:
        return (
            status,
            cycle['n'],
            cycle['delta_ms'],
            cycle['speed'],
            cycle['ts'],
            cycle['tend_rms'],
            cycle['tstart_rms'],
            cycle['baseline'],
        )
    return status, None, None, None, None, None, None, None


def reset_tracker(stroke_in=1.0, impact_mult=10, breakaway_mult=3,
                  debounce_ms=50, max_lookback_ms=100, min_lookback_ms=15,
                  adaptive_window_s=10.0, baseline_pct=50):
    tracker.reset()
    tracker.stroke_in         = stroke_in
    tracker.impact_mult       = impact_mult
    tracker.breakaway_mult    = breakaway_mult
    tracker.debounce_ms       = debounce_ms
    tracker.max_lookback_ms   = max_lookback_ms
    tracker.min_lookback_ms   = min_lookback_ms
    tracker.baseline_pct      = baseline_pct
    # Rebuild rms_history deque with new window size
    tracker.adaptive_window_s = adaptive_window_s
    adaptive_chunks           = int(adaptive_window_s * 1000 / CHUNK_MS)
    tracker.rms_history       = deque(maxlen=adaptive_chunks)


def get_cycles():
    return [(c['n'], c['delta_ms'], c['speed'], c['ts'], c['status']) for c in tracker.cycles]


def get_baseline():
    return tracker.baseline
