// Contact Me: Email, LinkedIn, GitHub, Last.fm, Résumé and Portfolio links (Figma Contact Me ·
// Desktop; openspec/specs/contact-page). Icons are the Figma icon components in public/contact/.
import { PageHeader } from "../components/ui";
import styles from "./Contact.module.css";

const EMAIL = "August@storyandstructure.studio";
const CV_URL = "https://app.notion.com/p/R-sum-Data-Product-Designer-407bd4600b7981808f4fef088372c75e";
const PORTFOLIO_URL = "https://app.notion.com/p/3f3bd4600b7980d088a1e74e415022d3";

const LINKS = [
  // The mail icon is the inner group of icon/mail, drawn at 1.25x and centred as in the design.
  { name: "Email", href: `mailto:${EMAIL}`, display: EMAIL, icon: "mail", width: 16.875, height: 13.125 },
  { name: "LinkedIn", href: "https://www.linkedin.com/in/augustowheeler/", display: "linkedin.com/in/augustowheeler", icon: "linkedin" },
  { name: "GitHub", href: "https://github.com/ItsAlwaysRaining", display: "github.com/ItsAlwaysRaining", icon: "github" },
  { name: "Last.fm", href: "https://www.last.fm/user/UntiLiUnderstan", display: "last.fm/user/UntiLiUnderstan", icon: "lastfm" },
  { name: "Résumé", href: CV_URL, display: "app.notion.com", icon: "notion" },
  { name: "Portfolio", href: PORTFOLIO_URL, display: "app.notion.com", icon: "notion" },
];

export default function Contact() {
  return (
    <>
      <PageHeader title="Contact Me">Questions about the project, a role, or your own listening data? Get in touch.</PageHeader>
      <section className={styles.body} aria-labelledby="get-in-touch">
        <h2 id="get-in-touch">Get in touch</h2>
        <ul className={styles.links}>
          {LINKS.map((l) => {
            const external = !l.href.startsWith("mailto:");
            return (
              <li key={l.name}>
                <a className={styles.link} href={l.href} {...(external && { target: "_blank", rel: "noreferrer" })}>
                  <span className={styles.iconCircle}>
                    <img src={`/contact/${l.icon}.svg`} alt="" width={l.width ?? 20} height={l.height ?? 20} />
                  </span>
                  <span className={styles.text}>
                    <span className={styles.name}>{l.name}</span>
                    <span className={styles.address}>{l.display}</span>
                  </span>
                  {external && <span className={styles.visuallyHidden}> (opens in a new tab)</span>}
                </a>
              </li>
            );
          })}
        </ul>
      </section>
    </>
  );
}
