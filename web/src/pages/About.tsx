// About: a photo beside About Me and About This App (Figma "About · Desktop", node 262:1334).
// The copy is drawn from the Figma research page (openspec/changes/about-page/design.md).
import { useState } from "react";
import { PageHeader } from "../components/ui";
import styles from "./About.module.css";

/** The design process file: research, wireframes, prototype, visual design and states. */
const FIGMA_URL = "https://www.figma.com/design/1rbbEne7pW8oA2JCNmjhrm";

/** The photo, or the design's dashed frame until web/public/about/photo.jpg is added. */
function Photo() {
  const [missing, setMissing] = useState(false);
  if (missing) {
    return (
      <div className={`${styles.photo} ${styles.empty}`} aria-hidden>
        <span className={styles.icon}>
          <img src="/about/image.svg" alt="" />
        </span>
      </div>
    );
  }
  return (
    <img className={styles.photo} src="/about/photo.jpg" alt="Photo of the author of Rain in My Head" onError={() => setMissing(true)} />
  );
}

export default function About() {
  return (
    <>
      <PageHeader title="About" />
      <div className={styles.body}>
        <Photo />
        <div className={styles.text}>
          <h2>About Me</h2>
          <div className={styles.copy}>
            <p>
              I'm a big nerd. In 2011 I started "scrobbling" all of my music listening data to Last.fm (So, I've always been like this).
              Streaming services were just starting to become popular and I started using Spotify but I really missed some of the "Smart
              Playlist" features Windows Media Player had. Those features never made it back into music players.
            </p>
            <p>
              I accepted this as a trade-off but eventually I became a data engineer and managed to carve out a little time for a
              personal project. This has been an experiment for me in many ways. I wanted to learn more about UI/UX (current obsession -
              every page here has a wireframe and clickable prototype in Figma), Web Dev and web hosting applications, AI (Vibe coding -
              I'm not a front end developer, spec driven design, and integrating AI into a web app - in progress). Now I get to see my
              own data, make custom playlists, and play with generating my own AI playlists (though the data is pretty limited - for
              now).
            </p>
          </div>
          <h2>About This App</h2>
          <div className={styles.copy}>
            <p>
              Rain in My Head turns my Last.fm listening history into dashboards I can explore and playlists I can save to Spotify. Its
              North Star is simple: control over my own data, so I can run my own analytics. It answers questions like what I've been
              listening to lately, which artists are new to me, and what I played the summer three years ago, and it builds playlists
              for times of day or seasons of my life. It builds playlists for me based on my listening history because Friday from 5 pm to 7 pm has its own
              feeling.
            </p>
            <p>
              Every page was designed in Figma first, from research and wireframes to a clickable prototype. You can follow the whole
              process in the{" "}
              <a href={FIGMA_URL} target="_blank" rel="noreferrer">
                Rain in My Head design file on Figma
                <span className={styles.visuallyHidden}> (opens in a new tab)</span>
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
