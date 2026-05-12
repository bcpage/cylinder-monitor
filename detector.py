import numpy as np
import time
from datetime import datetime
from collections import deque

SAMPLE_RATE        = 48000
CHUNK_MS           = 10
IMPACT_MULTIPLIER  = 10       # threshold multiplier for hard hit (T_end)
BREAKAWAY_MULT     = 3        # threshold multiplier for soft tap search in ring buffer
DEBOUNCE_MS        = 50
MAX_LOOKBACK_MS    = 100      # how far back to search for T_start
MIN_LOOKBACK_MS    = 15       # minimum gap — ignore anything closer than this
DEFAULT_STROKE     = 1.0

CAL_DURATION_S     = 1.5
ADAPTIVE_WINDOW_S  = 5.0
CAL_CHUNKS_NEED    = int(CAL_DURATION_S  * 1000 / CHUNK_MS)
ADAPTIVE_CHUNKS    = int(ADAPTIVE_WINDOW_S * 1000 / CHUNK_MS)

# Ring buffer size — store enough chunks to cover lookback window + margin
RING_BUFFER_MS     = 250
RING_BUFFER_CHUNKS = int(RING_BUFFER_MS / CHUNK_MS)   # 25 chunks


class CycleTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.baseline          = None
        self.cal_rms           = []
        self.cal_done          = False
        self.rms_history       = deque(maxlen=ADAPTIVE_CHUNKS)

        # Ring buffer: stores (rms, timestamp_s) for last ~250ms of chunks
        self.ring_buffer       = deque(maxlen=RING_BUFFER_CHUNKS)

        self.last_spike_t      = None
        self.cycles            = []

        # Tunable params
        self.stroke_in         = DEFAULT_STROKE
        self.impact_mult       = IMPACT_MULTIPLIER
        self.breakaway_mult    = BREAKAWAY_MULT
        self.debounce_ms       = DEBOUNCE_MS
        self.max_lookback_ms   = MAX_LOOKBACK_MS
        self.min_lookback_ms   = MIN_LOOKBACK_MS

    def process(self, rms, timestamp_s):
        """
        Called on every chunk. rms is the chunk RMS, timestamp_s is wall-clock time.
        Returns (status, cycle_dict_or_None)
        """
        self.rms_history.append(rms)

        # ── Calibration ───────────────────────────────────────────────────
        if not self.cal_done:
            self.cal_rms.append(rms)
            if len(self.cal_rms) >= CAL_CHUNKS_NEED:
                self.baseline = float(np.percentile(self.cal_rms, 80))
                self.cal_done = True
                return 'ready', None
            pct = int(len(self.cal_rms) / CAL_CHUNKS_NEED * 100)
            return f'cal:{pct}', None

        # ── Adaptive baseline (only when not frozen) ──────────────────────
        if len(self.rms_history) >= CAL_CHUNKS_NEED:
            self.baseline = float(np.percentile(self.rms_history, 80))

        # ── Always push chunk into ring buffer ────────────────────────────
        self.ring_buffer.append((rms, timestamp_s))

        impact_threshold    = self.baseline * self.impact_mult
        breakaway_threshold = self.baseline * self.breakaway_mult

        # ── Below impact threshold — nothing to do ────────────────────────
        if rms < impact_threshold:
            return 'listen', None

        # ── Debounce ──────────────────────────────────────────────────────
        now = timestamp_s
        if self.last_spike_t and (now - self.last_spike_t) * 1000 < self.debounce_ms:
            return 'debounce', None
        self.last_spike_t = now

        # ── Hard hit detected — look back for soft tap ────────────────────
        t_end     = now
        t_end_rms = rms

        # Search ring buffer for highest soft spike in [min_lookback, max_lookback] before T_end
        best_rms  = None
        best_t    = None

        for (chunk_rms, chunk_t) in self.ring_buffer:
            delta_ms = (t_end - chunk_t) * 1000
            if delta_ms < self.min_lookback_ms:
                continue   # too close — within debounce / same event
            if delta_ms > self.max_lookback_ms:
                continue   # too far back
            if chunk_rms < breakaway_threshold:
                continue   # below breakaway sensitivity
            if best_rms is None or chunk_rms > best_rms:
                best_rms = chunk_rms
                best_t   = chunk_t

        if best_t is None:
            # No T_start found in window — log as unmatched hard hit
            unmatched = {
                'n':          len(self.cycles) + 1,
                'delta_ms':   None,
                'speed':      None,
                'ts':         datetime.now().strftime('%H:%M:%S'),
                'status':     'unmatched',
                'tend_rms':   round(t_end_rms, 6),
                'tstart_rms': None,
            }
            self.cycles.append(unmatched)
            return 'unmatched', unmatched

        # ── Confirmed cycle ───────────────────────────────────────────────
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
        )
    return status, None, None, None, None, None, None


def reset_tracker(stroke_in=1.0, impact_mult=10, breakaway_mult=3,
                  debounce_ms=50, max_lookback_ms=100, min_lookback_ms=15):
    tracker.reset()
    tracker.stroke_in       = stroke_in
    tracker.impact_mult     = impact_mult
    tracker.breakaway_mult  = breakaway_mult
    tracker.debounce_ms     = debounce_ms
    tracker.max_lookback_ms = max_lookback_ms
    tracker.min_lookback_ms = min_lookback_ms


def get_cycles():
    return [(c['n'], c['delta_ms'], c['speed'], c['ts'], c['status']) for c in tracker.cycles]


def get_baseline():
    return tracker.baseline
