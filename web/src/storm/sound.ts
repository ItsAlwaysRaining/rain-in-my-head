// Storm mode's sound (specs/007-storm-mode): rain and thunder synthesised with the Web Audio API, so
// there are no audio files. Create it only from a click; browsers block audio that starts on its own.

export interface Storm {
  /** 0–1. */
  setVolume: (volume: number) => void;
  /** One rumble, 4–6 s long. */
  thunder: () => void;
  close: () => void;
}

/** Two seconds of white noise, looped for rain and sliced for thunder. */
function noise(ctx: AudioContext): AudioBuffer {
  const buffer = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
  return buffer;
}

export function createStorm(volume: number): Storm | null {
  const Ctx = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!Ctx) return null;
  const ctx = new Ctx();
  const buffer = noise(ctx);

  const master = ctx.createGain();
  master.gain.value = 0;
  master.connect(ctx.destination);
  const setVolume = (v: number) => {
    master.gain.setTargetAtTime(v * 0.6, ctx.currentTime, 0.1);
  };
  setVolume(volume);

  // Rain: steady hiss, band-limited so it sounds like rain on a window rather than static.
  const rain = ctx.createBufferSource();
  rain.buffer = buffer;
  rain.loop = true;
  const high = new BiquadFilterNode(ctx, { type: "highpass", frequency: 400 });
  const low = new BiquadFilterNode(ctx, { type: "lowpass", frequency: 3200 });
  const rainGain = new GainNode(ctx, { gain: 0.35 });
  rain.connect(high).connect(low).connect(rainGain).connect(master);
  rain.start();

  const thunder = () => {
    const t = ctx.currentTime;
    const length = 4 + Math.random() * 2;
    const burst = ctx.createBufferSource();
    burst.buffer = buffer;
    burst.loop = true;
    // The crack is brighter, then the rumble rolls off.
    const filter = new BiquadFilterNode(ctx, { type: "lowpass", frequency: 900, Q: 0.7 });
    filter.frequency.setValueAtTime(900, t);
    filter.frequency.exponentialRampToValueAtTime(120, t + 1.2);
    const gain = new GainNode(ctx, { gain: 0.0001 });
    gain.gain.exponentialRampToValueAtTime(1.6, t + 0.08);
    gain.gain.exponentialRampToValueAtTime(0.5, t + 1);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + length);
    burst.connect(filter).connect(gain).connect(master);
    burst.start(t);
    burst.stop(t + length);
  };

  return {
    setVolume,
    thunder,
    close: () => {
      master.gain.setTargetAtTime(0, ctx.currentTime, 0.05);
      setTimeout(() => void ctx.close(), 200);
    },
  };
}
