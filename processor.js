// processor.js — AudioWorkletProcessor
// v5: ring buffer in worklet, RMS sent every chunk for cal/baseline,
//     spike fired on hard hit only — lookback handled in detector.py
//     debounce synced from main thread via set_debounce message
//
// Pipeline per 10ms chunk:
//   1. Compute additive combined signal (|ch0| + |ch1|)
//   2. Compute RMS — always sent to main thread (cal + adaptive baseline)
//   3. Store (rms, timestamp) in ring buffer
//   4. FFT gate — if HF energy below hfFloor, discard
//   5. If RMS >= impact threshold AND passed FFT gate — fire spike
//      Main thread passes spike + ring buffer snapshot to Pyodide for lookback

class CylinderProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();

    this.chunkSamples  = options.processorOptions?.chunkSamples ?? 480;
    this.sampleRate    = options.processorOptions?.sampleRate   ?? 48000;
    this.buffer        = [];

    // Detection state
    this.threshold     = null;   // impact threshold — set from main thread after cal
    this.debounceMs    = options.processorOptions?.debounceMs ?? 50;
    this.lastSpikeTime = -Infinity;

    // FFT gate
    this.hfBinLow  = options.processorOptions?.hfBinLow  ?? 10;
    this.hfBinHigh = options.processorOptions?.hfBinHigh ?? 100;
    this.hfFloor   = options.processorOptions?.hfFloor   ?? 0.01;

    // Ring buffer — stores {rms, t} for last ~250ms of chunks
    // 250ms / 10ms = 25 slots
    this.ringSize   = 25;
    this.ringBuffer = [];

    this.port.onmessage = (e) => {
      if (e.data.type === 'set_threshold')  this.threshold  = e.data.value;
      if (e.data.type === 'set_debounce')   this.debounceMs = e.data.value;
      if (e.data.type === 'set_hf_floor')   this.hfFloor    = e.data.value;
    };
  }

  // Real-valued DFT — sufficient for 480-sample chunks
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

      // RMS
      let sumSq = 0;
      for (let i = 0; i < chunk.length; i++) sumSq += chunk[i] * chunk[i];
      const rms = Math.sqrt(sumSq / chunk.length);
      const nowMs = currentTime * 1000;

      // Always push to ring buffer
      this.ringBuffer.push({ rms, t: nowMs });
      if (this.ringBuffer.length > this.ringSize) this.ringBuffer.shift();

      // Always send RMS to main thread for cal / adaptive baseline
      this.port.postMessage({ type: 'rms', value: rms });

      // Impact detection
      if (this.threshold !== null && rms >= this.threshold) {

        // FFT gate
        const mags     = this._computeFFTMagnitudes(chunk);
        const hfEnergy = this._hfEnergy(mags);

        if (hfEnergy < this.hfFloor) {
          this.port.postMessage({ type: 'gated', rms, hfEnergy });
          continue;
        }

        // Debounce
        if (nowMs - this.lastSpikeTime < this.debounceMs) continue;
        this.lastSpikeTime = nowMs;

        // Fire spike — include snapshot of ring buffer for lookback in Python
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
