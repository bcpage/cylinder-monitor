class CylinderProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = [];
    this._chunkSamples = Math.floor(sampleRate * 0.01); // 10ms chunks
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    // Mix down to mono if stereo
    const ch0 = input[0];
    const ch1 = input[1] || ch0;
    const mono = new Float32Array(ch0.length);
    for (let i = 0; i < ch0.length; i++) {
      mono[i] = (ch0[i] + ch1[i]) / 2;
    }

    // Accumulate samples
    for (let i = 0; i < mono.length; i++) {
      this._buffer.push(mono[i]);
    }

    // When we have enough for a 10ms chunk, send it
    while (this._buffer.length >= this._chunkSamples) {
      const chunk = this._buffer.splice(0, this._chunkSamples);
      this.port.postMessage({ chunk });
    }

    return true;
  }
}

registerProcessor('cylinder-processor', CylinderProcessor);
