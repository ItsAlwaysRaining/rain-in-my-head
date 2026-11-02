// Tells the hosted site which page a logged-in visitor opened and how long they were on it (specs/012-usage-tracking,
// research R3). Two small reports per visit: one when the page opens, one when it is left. Time counts only while
// the tab is on screen and the visitor has moved, typed, scrolled or touched within the last minute.
// Does nothing on your Mac (no login there) or for anyone who isn't logged in.
import { useEffect } from "react";
import { useLocation } from "react-router";
import { sendEvent } from "./api";
import { useAuth } from "./auth";
import { PAGE_KEYS } from "./routes";

const TICK_MS = 5_000;
const IDLE_MS = 60_000;
const MAX_SECONDS = 1800;
const ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const ACTIVITY = ["pointermove", "pointerdown", "keydown", "scroll", "wheel", "touchstart"] as const;

const newVisit = () => Array.from(crypto.getRandomValues(new Uint8Array(12)), (b) => ALPHABET[b % ALPHABET.length]).join("");

export function useTracking() {
  const { pathname } = useLocation();
  const auth = useAuth();
  const tracking = auth.status === "ready" && !auth.local && auth.loggedIn;
  const page = tracking ? (PAGE_KEYS as Record<string, string | undefined>)[pathname] : undefined;

  useEffect(() => {
    if (!page) return;
    const visit = newVisit();
    let seconds = 0;
    let lastActive = Date.now();
    let sent = false;

    const leave = () => {
      if (sent) return;
      sent = true;
      sendEvent({ event: "leave", visit, page, seconds: Math.min(Math.round(seconds), MAX_SECONDS) });
    };
    const touch = () => {
      lastActive = Date.now();
    };
    // Hiding the tab sends the time so far. Coming back starts counting again under the same visit.
    const onVisibility = () => {
      if (document.visibilityState === "hidden") leave();
      else {
        sent = false;
        seconds = 0;
        touch();
      }
    };
    const tick = window.setInterval(() => {
      if (document.visibilityState === "visible" && Date.now() - lastActive < IDLE_MS) seconds += TICK_MS / 1000;
    }, TICK_MS);

    sendEvent({ event: "open", visit, page });
    for (const name of ACTIVITY) window.addEventListener(name, touch, { passive: true });
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("pagehide", leave);
    return () => {
      window.clearInterval(tick);
      for (const name of ACTIVITY) window.removeEventListener(name, touch);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("pagehide", leave);
      leave();
    };
  }, [page]);
}
