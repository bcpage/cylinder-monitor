// processor.js — AudioWorkletProcessor
// v3: RMS in JS, spike-only Pyodide calls, FFT high-frequency gate (Option A)
//
// Pipeline per 10ms chunk:
//   1. Compute additive combined signal (|ch0| + |ch1|)
//   2. Compute RMS — send to main thread for adaptive baseline tracking
//   3. FFT gate — if HF energy (>= HF_BIN_LOW) is below HF_FLOOR, discard chunk
//   4. If RMS >= threshold AND chunk passed FFT gate, fire spike event
//
// Parameters (all tunable from main thread via postMessage):
//   set_threshold  — absolute RMS threshold (baseline * multiplier), updated after each spike
//   set_debounce   — debounce window in ms (default 50)
//   set_hf_floor   — HF energy gate floor (default 0.01, tune empirically on cylinder)
//   set_hf_bin_low — lowest FFT bin index treated as HF (default = bin for ~1kHz at 48kHz/480samples)

class CylinderProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();

    // 10ms chunk at 48kHz = 480 samples
    this.chunkSamples  = options.processorOptions?.chunkSamples ?? 480;
    this.sampleRate    = options.processorOptions?.sampleRate   ?? 48000;
    this.buffer        = [];

    // Detection state
    this.threshold     = null;
    this.debounceMs    = 50;
    this.lastSpikeTime = -Infinity;

    // FFT gate parameters
    // At 48kHz with 480-sample FFT: bin width = 48000/480 = 100 Hz per bin
    // Bin for 1kHz = 1000/100 = bin 10
    // Bin for 10kHz = 10000/100 = bin 100
    // Default gate: sum energy in bins 10-100, compare to HF_FLOOR
    this.hfBinLow  = options.processorOptions?.hfBinLow  ?? 10;   // ~1kHz
    this.hfBinHigh = options.processorOptions?.hfBinHigh ?? 100;  // ~10kHz
    this.hfFloor   = options.processorOptions?.hfFloor   ?? 0.01; // tune on cylinder

    this.port.onmessage = (e) => {
      if (e.data.type === 'set_threshold')  this.threshold  = e.data.value;
      if (e.data.type === 'set_debounce')   this.debounceMs = e.data.value;
      if (e.data.type === 'set_hf_floor')   this.hfFloor    = e.data.value;
      if (e.data.type === 'set_hf_bin_low') this.hfBinLow   = e.data.value;
    };
  }

  // Real-valued DFT — sufficient for 480-sample chunks in a worklet
  // Returns array of magnitudes, length = chunkSamples/2
  _computeFFTMagnitudes(chunk) {
    const N    = chunk.length;
    const half = Math.floor(N / 2);
    const mags = new Float32Array(half);

    for (let k = 0; k < half; k++) {
      let re = 0, im = 0;
      for (let n = 0; n < N; n++) {
        const angle = (2 * Math.PI * k * n) / N;
        re += chunk[n] * Math.cos(angle);
        im -= chunk[n] * Math.sin(angle);
      }
      mags[k] = Math.sqrt(re * re + im * im) / N;
    }
    return mags;
  }

  // Sum magnitude energy in HF band [hfBinLow, hfBinHigh]
  _hfEnergy(mags) {
    let energy = 0;
    const hi = Math.min(this.hfBinHigh, mags.length - 1);
    for (let k = this.hfBinLow; k <= hi; k++) {
      energy += mags[k];
    }
    return energy;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const ch0 = input[0];
    const ch1 = input[1] ?? ch0;  // mono fallback

    // Accumulate additive combined signal
    for (let i = 0; i < ch0.length; i++) {
      this.buffer.push(Math.abs(ch0[i]) + Math.abs(ch1[i]));
    }

    // Process complete 10ms chunks
    while (this.buffer.length >= this.chunkSamples) {
      const chunk = this.buffer.splice(0, this.chunkSamples);

      // Step 1 — RMS (broadband, always computed)
      let sumSq = 0;
      for (let i = 0; i < chunk.length; i++) sumSq += chunk[i] * chunk[i];
      const rms = Math.sqrt(sumSq / chunk.length);

      // Step 2 — Send RMS to main thread for adaptive baseline tracking (always)
      this.port.postMessage({ type: 'rms', value: rms });

      // Step 3 — FFT gate (only runs if RMS is already above threshold)
      // Avoids FFT cost on quiet chunks — FFT only runs when something is loud enough
      if (this.threshold !== null && rms >= this.threshold) {
        const mags     = this._computeFFTMagnitudes(chunk);
        const hfEnergy = this._hfEnergy(mags);

        // Gate: if HF energy is below floor, this is low-frequency noise — discard
        if (hfEnergy < this.hfFloor) {
          this.port.postMessage({ type: 'gated', rms: rms, hfEnergy: hfEnergy });
          continue; // skip spike — chunk failed FFT gate
        }

        // Step 4 — Passed both RMS threshold and FFT gate — fire spike
        const nowMs = currentTime * 1000;
        if (nowMs - this.lastSpikeTime >= this.debounceMs) {
          this.lastSpikeTime = nowMs;
          this.port.postMessage({
            type:      'spike',
            rms:       rms,
            hfEnergy:  hfEnergy,
            timestamp: nowMs
          });
        }
      }
    }

    return true;
  }
}

registerProcessor('cylinder-processor', CylinderProcessor);
