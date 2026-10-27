// Storm: full-window rain with optional thunder (Figma Storm · Desktop; specs/007-storm-mode). The rain
// is the two exported "Storm / Rain" layers looping in CSS. Thunder is the one switch for sound and
// lightning, and it's off whenever the page opens, so nothing plays until someone chooses it.
import { useEffect, useRef, useState } from "react";
import { createStorm, type Storm as StormSound } from "../storm/sound";
import styles from "./Storm.module.css";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const between = (lo: number, hi: number) => lo + Math.random() * (hi - lo);

export default function Storm() {
  const [thunder, setThunder] = useState(false);
  const [volume, setVolume] = useState(60);
  const [strike, setStrike] = useState(0);
  const sound = useRef<StormSound | null>(null);

  // Sound starts from the click itself (browsers only allow audio after a gesture) and stops when
  // Thunder goes off or the page is left.
  const toggle = () => {
    if (thunder) {
      sound.current?.close();
      sound.current = null;
    } else {
      sound.current = createStorm(volume / 100);
    }
    setThunder(!thunder);
  };
  useEffect(() => () => sound.current?.close(), []);
  useEffect(() => {
    sound.current?.setVolume(volume / 100);
  }, [volume]);

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
        <div className={styles.pill}>
          <div className={styles.sound}>
            <button type="button" className={thunder ? styles.thunderOn : styles.thunderOff} aria-pressed={thunder} onClick={toggle}>
              <span className={styles.icon}>
                <img src={thunder ? "/storm/bolt-on.svg" : "/storm/bolt-off.svg"} alt="" width={10.5} height={14.5001} />
              </span>
              Thunder: {thunder ? "On" : "Off"}
            </button>
            <label className={thunder ? styles.volume : `${styles.volume} ${styles.asleep}`}>
              Rain volume
              <span className={styles.icon}>
                <img src="/storm/sound-on.svg" alt="" width={13.5151} height={11.5} />
              </span>
              <input
                type="range"
                min={0}
                max={100}
                value={volume}
                disabled={!thunder}
                title={thunder ? undefined : "Turn on Thunder to hear the rain"}
                onChange={(e) => setVolume(Number(e.target.value))}
              />
            </label>
          </div>
        </div>
        <p className={`${styles.pill} ${styles.hint}`}>Click the cloud icon to go Home</p>
      </div>
    </>
  );
}
