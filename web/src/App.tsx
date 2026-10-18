import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Component, createContext, useContext, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { BrowserRouter, NavLink, Route, Routes } from "react-router";
import styles from "./App.module.css";
import { Notice } from "./components/ui";
import Genre from "./pages/Genre";
import Overview from "./pages/Overview";
import Sql from "./pages/Sql";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: false, refetchOnWindowFocus: false } },
});

// Same pages, order and paths as the Streamlit dashboard (dashboard/app.py).
const PAGES = [
  { path: "/", label: "Overview", icon: "▥" },
  { path: "/genre", label: "Genre", icon: "◇" },
  { path: "/sql", label: "SQL", icon: "⛁" },
  { path: "/schema", label: "Schema", icon: "⊶" },
  { path: "/playlists", label: "Playlists", icon: "♫" },
];

/** Pages put their filters in the sidebar, under the menu, through this slot. */
const SidebarSlot = createContext<HTMLElement | null>(null);

export function Sidebar({ children }: { children: ReactNode }) {
  const slot = useContext(SidebarSlot);
  return slot ? createPortal(children, slot) : null;
}

function ComingSoon({ title }: { title: string }) {
  return (
    <>
      <h1>{title}</h1>
      <div style={{ marginTop: 24 }}>
        <Notice>This page is coming in a later slice. It's available in the Streamlit dashboard meanwhile.</Notice>
      </div>
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

export default function App() {
  const [slot, setSlot] = useState<HTMLElement | null>(null);
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SidebarSlot.Provider value={slot}>
          <div className={styles.shell}>
            <aside className={styles.sidebar}>
              <nav className={styles.nav}>
                {PAGES.map((p) => (
                  <NavLink key={p.path} to={p.path} end className={({ isActive }) => (isActive ? styles.navActive : styles.navLink)}>
                    <span className={styles.navIcon} aria-hidden>
                      {p.icon}
                    </span>
                    {p.label}
                  </NavLink>
                ))}
              </nav>
              <div ref={setSlot} className={styles.sidebarSlot} />
            </aside>
            <main className={styles.main}>
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<Overview />} />
                  <Route path="/genre" element={<Genre />} />
                  <Route path="/sql" element={<Sql />} />
                  <Route path="/schema" element={<ComingSoon title="Schema" />} />
                  <Route path="/playlists" element={<ComingSoon title="Playlists" />} />
                  <Route path="*" element={<ComingSoon title="Not found" />} />
                </Routes>
              </ErrorBoundary>
            </main>
          </div>
        </SidebarSlot.Provider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
