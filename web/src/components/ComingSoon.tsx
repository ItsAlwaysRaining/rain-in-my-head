// The placeholder for a prototype feature that isn't built yet: the landing page's storm cloud
// (bolt glow, lightning, falling rain), a "Coming soon" pill, what's planned, and its GitHub issue.
import type { ReactNode } from "react";
import { issueUrl } from "../routes";
import styles from "./ComingSoon.module.css";

const RAIN = [
  { x: 34, delay: 0, len: 22 },
  { x: 50, delay: 0.5, len: 30 },
  { x: 64, delay: 0.2, len: 18 },
  { x: 78, delay: 0.8, len: 26 },
  { x: 142, delay: 0.35, len: 24 },
  { x: 156, delay: 0.95, len: 30 },
  { x: 170, delay: 0.15, len: 20 },
  { x: 184, delay: 0.65, len: 28 },
];

export function ComingSoon({ title, issue, children }: { title: string; issue: number; children: ReactNode }) {
  return (
    <div className={styles.wrap}>
      <svg className={styles.art} viewBox="0 0 220 180" role="img" aria-label="A storm cloud with lightning and rain">
        <defs>
          <filter id="cs-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g className={styles.rain}>
          {RAIN.map((d) => (
            <line key={d.x} x1={d.x} x2={d.x} y1={104} y2={104 + d.len} style={{ animationDelay: `${d.delay}s` }} />
          ))}
        </g>
        <path
          className={styles.cloud}
          filter="url(#cs-glow)"
          d="M52 98c-17 0-29-12-29-27s12-27 28-27c4-19 21-32 41-32 17 0 31 9 38 23 4-2 9-3 14-3 18 0 33 14 33 32s-14 34-33 34Z"
        />
        <path className={styles.bolt} d="M118 52 98 82h15l-9 26 26-36h-15l9-20Z" />
      </svg>
      <span className={styles.pill}>Coming soon</span>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.text}>{children}</p>
      <a className={styles.issue} href={issueUrl(issue)} target="_blank" rel="noreferrer">
        Follow the plan in issue #{issue} <span aria-hidden>↗</span>
      </a>
    </div>
  );
}
