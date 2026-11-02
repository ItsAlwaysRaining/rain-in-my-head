// Login: one field for the invite code (specs/011-viewer-access). Public. The notice says what the site records
// (specs/012-usage-tracking, research R10): keep it in step with what usage.py stores and how long it keeps it.
import { useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router";
import { login, type Me } from "../api";
import { ME_KEY, useAuth } from "../auth";
import { Button, Notice, PageHeader } from "../components/ui";
import styles from "./Login.module.css";

/** Only a path on this site, so a crafted link can't send someone elsewhere after logging in. */
const safeNext = (next: string | null) => (next && /^\/(?!\/)/.test(next) ? next : "/dashboards");

export default function Login() {
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const auth = useAuth();
  const next = safeNext(params.get("next"));

  if (auth.local || auth.loggedIn) return <Navigate to={next} replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const me: Me = await login(code);
      queryClient.setQueryData(ME_KEY, me);
      navigate(next, { replace: true });
    } catch (e) {
      setError(e instanceof Error ? e.message : "That code didn't work.");
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Log in">Enter the invite code you were given.</PageHeader>
      <form className={styles.form} onSubmit={submit}>
        <label className={styles.label} htmlFor="code">
          Invite code
        </label>
        <input
          id="code"
          className={styles.input}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="xxxx-xxxx-xxxx-xxxx"
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          maxLength={64}
          autoFocus
        />
        {error && <Notice tone="error">{error}</Notice>}
        <div>
          <Button variant="primary" type="submit" disabled={busy || !code.trim()}>
            {busy ? "Checking…" : "Log in"}
          </Button>
        </div>
      </form>
      <p className={styles.privacy}>
        This site records which pages you open, which features you use, and how long you stay, against your name. Records are kept for 12
        months, then deleted. Raw IP addresses are never stored.
      </p>
    </>
  );
}
