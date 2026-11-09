-- The visitor database (Neon). Run by `rain-in-my-head viewer init` as the owner role, on dev and on prod.
-- Safe to run twice. Nothing here touches listening data (specs/011-viewer-access/data-model.md).

CREATE TABLE IF NOT EXISTS viewers (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name          text NOT NULL,
    tier          text NOT NULL CHECK (tier IN ('guest', 'trusted')),
    code_hash     text NOT NULL UNIQUE,
    status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked')),
    created_at    timestamptz NOT NULL DEFAULT now(),
    revoked_at    timestamptz,
    last_login_at timestamptz
);

-- Names are unique among active codes only, so a revoked person can be added again.
CREATE UNIQUE INDEX IF NOT EXISTS viewers_active_name ON viewers (lower(name)) WHERE status = 'active';

CREATE TABLE IF NOT EXISTS viewer_pages (
    viewer_id bigint NOT NULL REFERENCES viewers (id) ON DELETE CASCADE,
    page      text NOT NULL,
    PRIMARY KEY (viewer_id, page)
);

CREATE TABLE IF NOT EXISTS sessions (
    id_hash    text PRIMARY KEY,
    viewer_id  bigint NOT NULL REFERENCES viewers (id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL
);

CREATE INDEX IF NOT EXISTS sessions_viewer ON sessions (viewer_id);

CREATE TABLE IF NOT EXISTS login_attempts (
    source_key      text PRIMARY KEY,
    window_start    timestamptz NOT NULL,
    window_failures integer NOT NULL DEFAULT 0,
    day_failures    integer NOT NULL DEFAULT 0,
    locked_until    timestamptz,
    updated_at      timestamptz NOT NULL DEFAULT now()
);

-- Usage records (specs/012-usage-tracking/data-model.md): one row per page view, time on a page, feature use or
-- limit hit. The per-person limit is counted from these same rows.
CREATE TABLE IF NOT EXISTS usage_events (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    viewer_id bigint NOT NULL REFERENCES viewers (id) ON DELETE CASCADE,
    kind      text NOT NULL CHECK (kind IN ('view', 'time', 'feature', 'limit')),
    page      text,
    feature   text,
    detail    text,
    visit     text,
    seconds   integer CHECK (seconds BETWEEN 0 AND 1800),
    at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS usage_events_viewer_kind_at ON usage_events (viewer_id, kind, at DESC);
CREATE INDEX IF NOT EXISTS usage_events_at ON usage_events (at);

-- What the website's role may do: read people, and write sessions and attempt counts. It can't add, promote
-- or revoke anyone, so a stolen site password can't invite itself. The role is created by `viewer init`.
GRANT SELECT ON viewers, viewer_pages TO rain_app;
GRANT UPDATE (last_login_at) ON viewers TO rain_app;
GRANT SELECT, INSERT, DELETE ON sessions TO rain_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON login_attempts TO rain_app;
-- Usage records: the site adds rows and reads back only the columns it needs to count for the limit. It can't
-- change or delete a record; `viewer prune` (the owner role) does the deleting.
GRANT INSERT ON usage_events TO rain_app;
GRANT SELECT (viewer_id, kind, page, at) ON usage_events TO rain_app;

-- Heavy requests from visitors with no login (specs/open-dashboards-without-login): counted per hashed client
-- address, so one visitor can't use up the allowance for everyone. The address itself is never stored.
CREATE TABLE IF NOT EXISTS anonymous_usage (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visitor_hash text NOT NULL,  -- sha256 of the client address
    page         text NOT NULL,
    feature      text NOT NULL,
    at           timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS anonymous_usage_hash_at ON anonymous_usage (visitor_hash, at DESC);
GRANT INSERT ON anonymous_usage TO rain_app;
GRANT SELECT (visitor_hash, at) ON anonymous_usage TO rain_app;
