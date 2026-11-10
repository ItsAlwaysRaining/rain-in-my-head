// Pages from the Figma prototype that aren't built yet. Each shows what's planned and links to the
// GitHub issue that tracks it (specs/005-prototype-redesign, data-model.md).
import { ComingSoon } from "../components/ComingSoon";
import { BackLink, PageHeader } from "../components/ui";

/** The AI playlist's Coming soon card, shown on the AI page and on the Playlist Generator's AI tab. */
export function AiPlaylistComingSoon() {
  return (
    <ComingSoon title="Describe a playlist in your own words" issue={32}>
      Ask for a mood, a time or a memory, like “songs I binged at the end of 2023 but haven't played since”, and get a playlist built only from your
      own listening history, with a reason for every track.
    </ComingSoon>
  );
}

export function Ai() {
  return (
    <>
      <PageHeader title="AI" />
      <AiPlaylistComingSoon />
    </>
  );
}

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
