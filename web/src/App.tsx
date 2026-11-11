import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Component, useEffect, useRef, useState, type ReactNode } from "react";
import { BrowserRouter, Link, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router";
import { ApiError, type Me } from "./api";
import styles from "./App.module.css";
import { AuthProvider, ME_KEY, RequireAccess, useAuth } from "./auth";
import { Breadcrumbs, Notice, PageHeader } from "./components/ui";
import About from "./pages/About";
import Analyst from "./pages/Analyst";
import Artist from "./pages/Artist";
import Contact from "./pages/Contact";
import Genre from "./pages/Genre";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import { Mainstream } from "./pages/Mainstream";
import NewArtists from "./pages/NewArtists";
import Overview from "./pages/Overview";
import { Ai, ListeningSlot } from "./pages/Placeholders";
import Playlists from "./pages/Playlists";
import Storm from "./pages/Storm";
import Visitors from "./pages/Visitors";
import { breadcrumbs, lockReason, SECTIONS } from "./routes";
import { useTracking } from "./usage";

// A data request the hosted site answers with "log in" (no session, or it was ended) sends the visitor to the login page.
const sessionEnded = (error: unknown) => {
  if (error instanceof ApiError && error.kind === "locked") queryClient.setQueryData<Me>(ME_KEY, { logged_in: false });
};

const queryClient: QueryClient = new QueryClient({
  queryCache: new QueryCache({ onError: sessionEnded }),
  mutationCache: new MutationCache({ onError: sessionEnded }),
  defaultOptions: { queries: { staleTime: 60_000, retry: false, refetchOnWindowFocus: false } },
});

/** The cloud from the logo, as an outline. */
function CloudLogo() {
  return (
    <svg viewBox="0 0 32 22" width="28" height="20" aria-hidden>
      <path d="M8 20h16a6 6 0 0 0 .5-12A8 8 0 0 0 9 9.5 5.3 5.3 0 0 0 8 20Z" fill="none" stroke="var(--rain)" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}

/** A small padlock beside a locked section. The reason is in text for screen readers, so this is decoration. */
function LockIcon() {
  return (
    <svg viewBox="0 0 12 14" width="10" height="12" aria-hidden className={styles.lock}>
      <rect x="1" y="6" width="10" height="7" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3.5 6V4a2.5 2.5 0 0 1 5 0v2" fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** The section links and Log out. The desktop bar and the Mobile menu both use this, so locks stay in one place. */
function NavLinks({ className }: { className: string }) {
  const auth = useAuth();
  const navigate = useNavigate();
  return (
    <>
      {SECTIONS.map((s) => {
        const locked = lockReason(s, auth);
        const short = "short" in s ? s.short : undefined;
        return (
          // A locked section is still a link: its page shows the login or "not available" screen, never data.
          <NavLink
            key={s.path}
            to={s.path}
            className={({ isActive }) => `${isActive ? styles.navActive : styles.navLink}${locked ? ` ${styles.navLocked}` : ""} ${className}`}
          >
            {locked && <LockIcon />}
            {/* Tablet widths swap in the short label (Figma Site Header, Tablet). */}
            {short ? (
              <>
                <span className={styles.fullLabel}>{s.label}</span>
                <span className={styles.shortLabel}>{short}</span>
              </>
            ) : (
              s.label
            )}
            {locked && <span className={styles.srOnly}>, locked: {locked}</span>}
          </NavLink>
        );
      })}
      {auth.loggedIn && (
        <button type="button" className={`${styles.logout} ${className}`} onClick={() => auth.logOut().then(() => navigate("/login", { replace: true }))}>
          Log out
        </button>
      )}
      {/* Logged out on the hosted site: Log in sits where Log out would. On your Mac there is no login. */}
      {auth.status === "ready" && !auth.loggedIn && !auth.local && (
        <NavLink to="/login" className={({ isActive }) => `${isActive ? styles.navActive : styles.navLink} ${className}`}>
          Log in
        </NavLink>
      )}
    </>
  );
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden>
      <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function TopBar() {
  const [open, setOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const { pathname } = useLocation();

  // A new page closes the Mobile menu.
  useEffect(() => setOpen(false), [pathname]);

  // Escape closes it and puts focus back on the button.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      setOpen(false);
      button.current?.focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header className={styles.topBar}>
      <div className={styles.topBarInner}>
        {/* Dissolves home, as the prototype's "Back to home" from Storm does. */}
        <Link to="/" viewTransition className={styles.brand}>
          <CloudLogo />
          <span className={styles.wordmark}>Rain in My Head</span>
        </Link>
        <nav aria-label="Main" className={styles.nav}>
          <NavLinks className="" />
        </nav>
        <button
          ref={button}
          type="button"
          className={styles.menuButton}
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen((o) => !o)}
        >
          <MenuIcon />
          <span className={styles.srOnly}>Menu</span>
        </button>
      </div>
      {open && (
        <nav
          id="mobile-menu"
          aria-label="Main"
          className={styles.mobileMenu}
        >
          <NavLinks className={styles.mobileItem} />
        </nav>
      )}
    </header>
  );
}

/** Sends an old address to its new page, keeping the query string. */
function Redirect({ to, extra }: { to: string; extra?: Record<string, string> }) {
  const params = new URLSearchParams(useLocation().search);
  for (const [k, v] of Object.entries(extra ?? {})) params.set(k, v);
  return <Navigate to={params.size ? `${to}?${params}` : to} replace />;
}

function NotFound() {
  return (
    <>
      <PageHeader title="Not found">There's no page at this address. It may have moved in the redesign.</PageHeader>
      <Notice>
        Try <Link to="/dashboards">Dashboards</Link>, or pick a section from the top bar.
      </Notice>
    </>
  );
}

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  render() {
    if (this.state.error) return <Notice tone="error">Something went wrong: {this.state.error.message}</Notice>;
    return this.props.children;
  }
}

function Shell() {
  const { pathname } = useLocation();
  useTracking();
  return (
    <>
      <TopBar />
      <main className={styles.main}>
        <Breadcrumbs crumbs={breadcrumbs(pathname)} />
        <div className={styles.page}>
          {/* Keyed by path so an error on one page clears when you navigate away. */}
          <ErrorBoundary key={pathname}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboards" element={<RequireAccess page="overview"><Overview /></RequireAccess>} />
              <Route path="/dashboards/new-artists" element={<RequireAccess page="new-artists"><NewArtists /></RequireAccess>} />
              <Route path="/dashboards/genre" element={<RequireAccess page="genre"><Genre /></RequireAccess>} />
              <Route path="/dashboards/artist" element={<RequireAccess page="artist"><Artist /></RequireAccess>} />
              <Route path="/dashboards/slot" element={<RequireAccess page="slot"><ListeningSlot /></RequireAccess>} />
              <Route path="/dashboards/mainstream" element={<RequireAccess page="mainstream"><Mainstream /></RequireAccess>} />
              <Route path="/playlists" element={<RequireAccess page="playlists"><Playlists /></RequireAccess>} />
              <Route path="/analyst" element={<RequireAccess page="analyst"><Analyst /></RequireAccess>} />
              <Route path="/visitors" element={<RequireAccess page="visitors"><Visitors /></RequireAccess>} />
              <Route path="/ai" element={<RequireAccess page="ai"><Ai /></RequireAccess>} />
              <Route path="/about" element={<RequireAccess page="about"><About /></RequireAccess>} />
              <Route path="/contact" element={<RequireAccess page="contact"><Contact /></RequireAccess>} />
              <Route path="/storm" element={<RequireAccess page="storm"><Storm /></RequireAccess>} />
              {/* Addresses from before the redesign (same paths as the Streamlit dashboard). */}
              <Route path="/genre" element={<Redirect to="/dashboards/genre" />} />
              <Route path="/artist" element={<Redirect to="/dashboards/artist" />} />
              <Route path="/sql" element={<Redirect to="/analyst" />} />
              <Route path="/schema" element={<Redirect to="/analyst" extra={{ schema: "open" }} />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </ErrorBoundary>
        </div>
      </main>
    </>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Shell />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
