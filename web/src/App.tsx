import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Component, type ReactNode } from "react";
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
import NewArtists from "./pages/NewArtists";
import Overview from "./pages/Overview";
import { ListeningSlot, Mainstream } from "./pages/Placeholders";
import Playlists from "./pages/Playlists";
import Storm from "./pages/Storm";
import { breadcrumbs, visibleSections } from "./routes";

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

function TopBar() {
  const auth = useAuth();
  const navigate = useNavigate();
  return (
    <header className={styles.topBar}>
      <div className={styles.topBarInner}>
        {/* Dissolves home, as the prototype's "Back to home" from Storm does. */}
        <Link to="/" viewTransition className={styles.brand}>
          <CloudLogo />
          Rain in My Head
        </Link>
        <nav aria-label="Main" className={styles.nav}>
          {visibleSections(auth.can).map((s) => (
            <NavLink key={s.path} to={s.path} className={({ isActive }) => (isActive ? styles.navActive : styles.navLink)}>
              {s.label}
            </NavLink>
          ))}
          {auth.loggedIn && (
            <button
              type="button"
              className={styles.logout}
              onClick={() => auth.logOut().then(() => navigate("/login", { replace: true }))}
            >
              Log out
            </button>
          )}
        </nav>
      </div>
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
