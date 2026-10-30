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

-- What the website's role may do: read people, and write sessions and attempt counts. It can't add, promote
-- or revoke anyone, so a stolen site password can't invite itself. The role is created by `viewer init`.
GRANT SELECT ON viewers, viewer_pages TO rain_app;
GRANT UPDATE (last_login_at) ON viewers TO rain_app;
GRANT SELECT, INSERT, DELETE ON sessions TO rain_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON login_attempts TO rain_app;
