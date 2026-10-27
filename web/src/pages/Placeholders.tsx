// Pages from the Figma prototype that aren't built yet. Each shows what's planned and links to the
// GitHub issue that tracks it (specs/005-prototype-redesign, data-model.md).
import { ComingSoon } from "../components/ComingSoon";
import { BackLink, PageHeader } from "../components/ui";

export function ListeningSlot() {
  return (
    <>
      <BackLink />
      <PageHeader title="When you listen" />
      <ComingSoon title="Tracks for one hour of the week" issue={30}>
        Click a square in the heatmap to see the songs you play at that hour on that weekday, such as Thursdays 15:00–16:00, with
        Day and Hour pickers to move around.
      </ComingSoon>
    </>
  );
}

export function Mainstream() {
  return (
    <>
      <BackLink />
      <PageHeader title="Mainstream vs. niche" />
      <ComingSoon title="The artists behind each bar" issue={12}>
        Every artist in a Last.fm listener band (for example 100k–1M) that you played in the range, with their listener count and
        your plays.
      </ComingSoon>
    </>
  );
}
