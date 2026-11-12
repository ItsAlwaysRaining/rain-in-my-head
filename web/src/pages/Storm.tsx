// Storm: full-window rain with optional sound (Figma Storm · Desktop; specs/007-storm-mode,
// openspec storm-page). The rain is the two exported "Storm / Rain" layers looping in CSS. Rain and
// Thunder are separate switches, each with its own volume, and both are off whenever the page opens,
// so nothing plays until someone chooses it.
import { useEffect, useRef, useState } from "react";
import { createStorm, type Storm as StormSound } from "../storm/sound";
import styles from "./Storm.module.css";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const between = (lo: number, hi: number) => lo + Math.random() * (hi - lo);

interface ControlProps {
  name: "Rain" | "Thunder";
  on: boolean;
  volume: number;
  onToggle: () => void;
  onVolume: (v: number) => void;
}

function SoundControl({ name, on, volume, onToggle, onVolume }: ControlProps) {
  const icon = name === "Rain" ? "/storm/sound-on.svg" : on ? "/storm/bolt-on.svg" : "/storm/bolt-off.svg";
  return (
    <div className={`${styles.pill} ${styles.sound}`}>
      <button type="button" className={on ? styles.toggleOn : styles.toggleOff} aria-pressed={on} onClick={onToggle}>
        <span className={styles.icon}>
          <img src={icon} alt="" width={name === "Rain" ? 13.5151 : 10.5} height={name === "Rain" ? 11.5 : 14.5001} />
        </span>
        {name}: {on ? "On" : "Off"}
      </button>
      <label className={on ? styles.volume : `${styles.volume} ${styles.asleep}`}>
        <span className={styles.visuallyHidden}>{name} volume</span>
        <input
          type="range"
          min={0}
          max={100}
          value={volume}
          disabled={!on}
          title={on ? undefined : `Turn on ${name} to change its volume`}
          onChange={(e) => onVolume(Number(e.target.value))}
        />
      </label>
    </div>
  );
}

export default function Storm() {
  const [rain, setRain] = useState(false);
  const [thunder, setThunder] = useState(false);
  const [rainVolume, setRainVolume] = useState(60);
  const [thunderVolume, setThunderVolume] = useState(60);
  const [strike, setStrike] = useState(0);
  const sound = useRef<StormSound | null>(null);

  // Audio starts from the click itself (browsers only allow audio after a gesture) and closes once
  // both switches are off or the page is left.
  const toggle = (which: "rain" | "thunder") => {
    const nextRain = which === "rain" ? !rain : rain;
    const nextThunder = which === "thunder" ? !thunder : thunder;
    if (nextRain || nextThunder) {
      sound.current ??= createStorm();
    } else {
      sound.current?.close();
      sound.current = null;
    }
    setRain(nextRain);
    setThunder(nextThunder);
  };
  useEffect(() => () => sound.current?.close(), []);
  useEffect(() => {
    sound.current?.setRain(rain ? rainVolume / 100 : 0);
  }, [rain, rainVolume]);
  useEffect(() => {
    sound.current?.setThunder(thunder ? thunderVolume / 100 : 0);
  }, [thunder, thunderVolume]);

  // Lightning every 6–14 s while Thunder is on, then thunder a moment later.
  useEffect(() => {
    if (!thunder) return;
    let timer: ReturnType<typeof setTimeout>;
    const schedule = () => {
      timer = setTimeout(() => {
        if (!reducedMotion()) setStrike((n) => n + 1);
        timer = setTimeout(() => {
          sound.current?.thunder();
          schedule();
        }, between(400, 1500));
      }, between(6000, 14000));
    };
    schedule();
    return () => clearTimeout(timer);
  }, [thunder]);

  return (
    <>
      <h1 className={styles.visuallyHidden}>Storm</h1>
      <div className={styles.rain} aria-hidden>
        <div className={styles.far} />
        <div className={styles.near} />
        {strike > 0 && <div key={strike} className={styles.flash} data-testid="flash" />}
      </div>

      <div className={styles.controls}>
        <div className={styles.sounds}>
          <SoundControl name="Rain" on={rain} volume={rainVolume} onToggle={() => toggle("rain")} onVolume={setRainVolume} />
          <SoundControl name="Thunder" on={thunder} volume={thunderVolume} onToggle={() => toggle("thunder")} onVolume={setThunderVolume} />
        </div>
        <p className={`${styles.pill} ${styles.hint}`}>Click the cloud icon to go Home</p>
      </div>
    </>
  );
}
