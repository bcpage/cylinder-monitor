// processor.js — AudioWorkletProcessor v5
// Additive combined signal, ring buffer, FFT gate, spike-only Pyodide calls.
// Debounce synced from main thread via set_debounce message.
// Snapshot mode: on-demand RMS+HF capture for calibration tab keypress events.

class CylinderProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();

    this.chunkSamples  = options.processorOptions?.chunkSamples ?? 480;
    this.sampleRate    = options.processorOptions?.sampleRate   ?? 48000;
    this.buffer        = [];

    this.threshold     = null;
    this.debounceMs    = options.processorOptions?.debounceMs ?? 50;
    this.lastSpikeTime = -Infinity;

    this.hfBinLow  = options.processorOptions?.hfBinLow  ?? 10;
    this.hfBinHigh = options.processorOptions?.hfBinHigh ?? 100;
    this.hfFloor   = options.processorOptions?.hfFloor   ?? 0.01;

    this.ringSize   = 25;
    this.ringBuffer = [];

    // Latest chunk values — used for snapshot requests from calibration tab
    this.lastRms      = 0;
    this.lastHfEnergy = 0;

    this.port.onmessage = (e) => {
      if (e.data.type === 'set_threshold')  this.threshold  = e.data.value;
      if (e.data.type === 'set_debounce')   this.debounceMs = e.data.value;
      if (e.data.type === 'set_hf_floor')   this.hfFloor    = e.data.value;
      if (e.data.type === 'snapshot') {
        // Calibration tab requested current RMS + HF — reply immediately
        this.port.postMessage({
          type:      'snapshot',
          rms:       this.lastRms,
          hfEnergy:  this.lastHfEnergy,
          timestamp: currentTime * 1000,
        });
      }
    };
  }

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

  _hfEnergy(mags) {
    let energy = 0;
    const hi = Math.min(this.hfBinHigh, mags.length - 1);
    for (let k = this.hfBinLow; k <= hi; k++) energy += mags[k];
    return energy;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const ch0 = input[0];
    const ch1 = input[1] ?? ch0;

    for (let i = 0; i < ch0.length; i++) {
      this.buffer.push(Math.abs(ch0[i]) + Math.abs(ch1[i]));
    }

    while (this.buffer.length >= this.chunkSamples) {
      const chunk = this.buffer.splice(0, this.chunkSamples);

      let sumSq = 0;
      for (let i = 0; i < chunk.length; i++) sumSq += chunk[i] * chunk[i];
      const rms   = Math.sqrt(sumSq / chunk.length);
      const nowMs = currentTime * 1000;

      // Compute HF for every chunk so snapshot always has fresh values
      const mags     = this._computeFFTMagnitudes(chunk);
      const hfEnergy = this._hfEnergy(mags);

      this.lastRms      = rms;
      this.lastHfEnergy = hfEnergy;

      this.ringBuffer.push({ rms, t: nowMs });
      if (this.ringBuffer.length > this.ringSize) this.ringBuffer.shift();

      this.port.postMessage({ type: 'rms', value: rms });

      if (this.threshold !== null && rms >= this.threshold) {
        if (hfEnergy < this.hfFloor) {
          this.port.postMessage({ type: 'gated', rms, hfEnergy });
          continue;
        }
        if (nowMs - this.lastSpikeTime < this.debounceMs) continue;
        this.lastSpikeTime = nowMs;

        this.port.postMessage({
          type:       'spike',
          rms,
          hfEnergy,
          timestamp:  nowMs,
          ringBuffer: this.ringBuffer.map(e => [e.rms, e.t])
        });
      }
    }

    return true;
  }
}

registerProcessor('cylinder-processor', CylinderProcessor);
