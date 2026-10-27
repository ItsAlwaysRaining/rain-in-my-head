// Landing: the Rain Girl hero from the Figma prototype (Landing · Desktop, "Landing / Rain Girl hero";
// specs/006-landing-page). The artwork is the Figma export of the rain loop with its own bolt hidden,
// inlined so CSS can swap which rain lines are lit. The bolt on top is the Lightning bolt component and
// opens Storm mode.
import { Link } from "react-router";
import rainGirl from "../assets/landing/rain-girl.svg?raw";
import styles from "./Landing.module.css";

export default function Landing() {
  return (
    <div className={styles.landing}>
      <h1 className={styles.visuallyHidden}>Rain in My Head</h1>
      <div className={styles.hero}>
        <div className={styles.art} role="img" aria-label="Rain in My Head: a storm cloud with lightning over a girl, with rain falling" dangerouslySetInnerHTML={{ __html: rainGirl }} />
        <Link to="/storm" viewTransition className={styles.bolt} aria-label="Storm mode" title="Storm mode">
          <img src="/landing/bolt.svg" alt="" width={134} height={155} />
        </Link>
      </div>
    </div>
  );
}
