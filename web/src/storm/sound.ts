// Storm mode's sound (specs/007-storm-mode): rain and thunder synthesised with the Web Audio API, so
// there are no audio files. Create it only from a click; browsers block audio that starts on its own.

export interface Storm {
  /** Rain hiss volume, 0–1 (0 is silent). */
  setRain: (volume: number) => void;
  /** Thunder volume, 0–1 (0 is silent). */
  setThunder: (volume: number) => void;
  /** One distant rumble, 7 s long. */
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

export function createStorm(): Storm | null {
  const Ctx = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!Ctx) return null;
  const ctx = new Ctx();
  const buffer = noise(ctx);

  // Rain and thunder each have their own volume, so one never changes the other.
  const level = () => {
    const g = new GainNode(ctx, { gain: 0 });
    g.connect(ctx.destination);
    return g;
  };
  const rainLevel = level();
  const thunderLevel = level();
  const set = (g: GainNode) => (v: number) => g.gain.setTargetAtTime(v * 0.6, ctx.currentTime, 0.1);

  // Rain ("Drops on a roof", picked in #39): a soft band-limited bed with separate drops tapping on top.
  const rain = ctx.createBufferSource();
  rain.buffer = buffer;
  rain.loop = true;
  const high = new BiquadFilterNode(ctx, { type: "highpass", frequency: 300 });
  const low = new BiquadFilterNode(ctx, { type: "lowpass", frequency: 2000 });
  const rainGain = new GainNode(ctx, { gain: 0.18 });
  rain.connect(high).connect(low).connect(rainGain).connect(rainLevel);
  rain.start();

  // About 28 drops a second: each a tiny burst of noise at a random pitch, decaying in 30–70 ms.
  let dropTimer: ReturnType<typeof setTimeout>;
  const drop = () => {
    if (ctx.state === "closed") return;
    const t = ctx.currentTime;
    const s = ctx.createBufferSource();
    s.buffer = buffer;
    const pitch = new BiquadFilterNode(ctx, { type: "bandpass", frequency: 1500 + Math.random() * 3500, Q: 6 });
    const g = new GainNode(ctx, { gain: 0.0001 });
    g.gain.exponentialRampToValueAtTime(0.5 * (0.4 + Math.random() * 0.6), t + 0.003);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.03 + Math.random() * 0.04);
    s.connect(pitch).connect(g).connect(rainLevel);
    s.start(t, Math.random());
    s.stop(t + 0.1);
    dropTimer = setTimeout(drop, ((Math.random() * 2) / 28) * 1000);
  };
  drop();

  // Thunder ("Distant rumble", picked in #39): no crack, a slow low swell far away, 7 s long.
  const thunder = () => {
    const t = ctx.currentTime;
    const length = 7;
    const burst = ctx.createBufferSource();
    burst.buffer = buffer;
    burst.loop = true;
    const filter = new BiquadFilterNode(ctx, { type: "lowpass", frequency: 220, Q: 0.7 });
    filter.frequency.setValueAtTime(220, t);
    filter.frequency.exponentialRampToValueAtTime(80, t + 1.2);
    const gain = new GainNode(ctx, { gain: 0.0001 });
    gain.gain.exponentialRampToValueAtTime(1.4, t + 0.8);
    gain.gain.exponentialRampToValueAtTime(0.42, t + 1.8);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + length);
    burst.connect(filter).connect(gain).connect(thunderLevel);
    burst.start(t);
    burst.stop(t + length);
  };

  return {
    setRain: set(rainLevel),
    setThunder: set(thunderLevel),
    thunder,
    close: () => {
      clearTimeout(dropTimer);
      for (const g of [rainLevel, thunderLevel]) g.gain.setTargetAtTime(0, ctx.currentTime, 0.05);
      setTimeout(() => void ctx.close(), 200);
    },
  };
}
