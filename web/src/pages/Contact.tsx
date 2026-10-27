// Contact Me: Email, LinkedIn, GitHub and Last.fm links, Send email and Download CV (Figma Contact Me ·
// Desktop; openspec/changes/contact-page). Icons are the Figma icon components in public/contact/.
import { ButtonLink, PageHeader } from "../components/ui";
import styles from "./Contact.module.css";

// Placeholder until the owner supplies the real address (issue #34).
const EMAIL = "hello@example.com";

const LINKS = [
  // The mail icon is the inner group of icon/mail, drawn at 1.25x and centred as in the design.
  { name: "Email", href: `mailto:${EMAIL}`, display: EMAIL, icon: "mail", width: 16.875, height: 13.125 },
  // Placeholder until the owner supplies the real profile (issue #34).
  { name: "LinkedIn", href: "https://www.linkedin.com/in/your-name", display: "linkedin.com/in/your-name", icon: "linkedin" },
  { name: "GitHub", href: "https://github.com/ItsAlwaysRaining", display: "github.com/ItsAlwaysRaining", icon: "github" },
  { name: "Last.fm", href: "https://www.last.fm/user/ItsAlwaysRaining", display: "last.fm/user/ItsAlwaysRaining", icon: "lastfm" },
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
        <div className={styles.actions}>
          <ButtonLink variant="primary" href={`mailto:${EMAIL}`}>
            Send email
          </ButtonLink>
          <ButtonLink href="/contact/cv.pdf" download>
            Download CV
          </ButtonLink>
        </div>
      </section>
    </>
  );
}
