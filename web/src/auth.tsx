// Who is logged in, and which pages they may open (specs/011-viewer-access, research R10). The server checks every
// request for data; this only decides what to show. On your Mac there is no login and every page opens.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, type ReactNode, useContext, useEffect, useRef } from "react";
import { Navigate, useLocation } from "react-router";
import { fetchMe, logout as logoutRequest, type Me } from "./api";
import { ErrorState, Loading } from "./components/ui";
import NotAvailable from "./pages/NotAvailable";
import type { PageKey } from "./routes";

export const ME_KEY = ["me"];

interface Auth {
  status: "loading" | "ready" | "error";
  error: unknown;
  local: boolean;
  loggedIn: boolean;
  name: string | undefined;
  /** True if this visitor may open the page (always true on your Mac). */
  can: (page: string) => boolean;
  logOut: () => Promise<void>;
}

const AuthContext = createContext<Auth | null>(null);

export function useAuth(): Auth {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth needs an AuthProvider");
  return auth;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ME_KEY, queryFn: fetchMe, staleTime: 0 });
  const { refetch } = query;

  // Ask again on every page change, so a revoked or changed code takes effect on the visitor's next click.
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    void refetch();
  }, [pathname, refetch]);

  const logOut = useMutation({
    mutationFn: logoutRequest,
    onSettled: () => {
      queryClient.removeQueries({ predicate: (q) => q.queryKey[0] !== ME_KEY[0] });
      queryClient.setQueryData<Me>(ME_KEY, { logged_in: false });
    },
  });

  const me = query.data;
  const local = !!me?.local;
  const loggedIn = !!me?.logged_in;
  const pages = new Set(me?.pages ?? []);
  const auth: Auth = {
    status: me === undefined ? (query.isError ? "error" : "loading") : "ready",
    error: query.error,
    local,
    loggedIn,
    name: me?.name,
    can: (page) => local || pages.has(page),
    logOut: () => logOut.mutateAsync(),
  };
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

/** Shows the page if the visitor may open it; otherwise the login page, or "not available to you". */
export function RequireAccess({ page, children }: { page: PageKey; children: ReactNode }) {
  const auth = useAuth();
  const { pathname, search } = useLocation();
  if (auth.status === "loading") return <Loading />;
  if (auth.status === "error") return <ErrorState error={auth.error} />;
  // Visitors with no login open the guest pages (open-dashboards-without-login). Others are sent to log in.
  if (!auth.can(page)) {
    if (!auth.loggedIn) return <Navigate to={`/login?next=${encodeURIComponent(pathname + search)}`} replace />;
    return <NotAvailable />;
  }
  return <>{children}</>;
}
