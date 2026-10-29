# Data model: Invite codes and locked pages

All tables live in the Neon visitor database, in the `public` schema, on both branches. They're made by `viewer init` ([viewer_schema.sql](../../src/rain_in_my_head/viewer_schema.sql), to be written in the tasks). Nothing here is in `public.db`.

## viewers

One row per invite. Adding a person again after a revoke makes a new row.

| Column | Type | Notes |
|---|---|---|
| `id` | bigint, generated | primary key |
| `name` | text, not null | what the owner typed |
| `tier` | text, not null | `guest` or `trusted` (a check constraint) |
| `code_hash` | text, not null, unique | hex SHA-256 of the cleaned code ([research R3](research.md)) |
| `status` | text, not null, default `active` | `active` or `revoked` (a check constraint) |
| `created_at` | timestamptz, not null, default now | |
| `revoked_at` | timestamptz | set by `viewer revoke` |
| `last_login_at` | timestamptz | the only column the site may update |

**Rules**
- A unique index on `lower(name)` where `status = 'active'` makes names unique among active codes (spec edge case).
- A code is never stored. Only `code_hash` is.

## viewer_pages

The pages granted to one person on top of their tier.

| Column | Type | Notes |
|---|---|---|
| `viewer_id` | bigint, not null | references `viewers(id)`, deleted with it |
| `page` | text, not null | a page key from `access.py` |

Primary key: `(viewer_id, page)`. A grant that's already in the tier's starting pages is allowed and harmless.

## sessions

| Column | Type | Notes |
|---|---|---|
| `id_hash` | text | primary key. Hex SHA-256 of the session id in the cookie |
| `viewer_id` | bigint, not null | references `viewers(id)`, deleted with it |
| `created_at` | timestamptz, not null, default now | |
| `expires_at` | timestamptz, not null | `created_at` plus 30 days |

An index on `viewer_id` lets `viewer revoke` delete a person's sessions quickly.

## login_attempts

| Column | Type | Notes |
|---|---|---|
| `source_key` | text | primary key. Hex HMAC of day plus address ([research R7](research.md)) |
| `window_start` | timestamptz, not null | start of the current one-minute window |
| `window_failures` | integer, not null | wrong codes in this window |
| `day_failures` | integer, not null | wrong codes today |
| `locked_until` | timestamptz | set at 20 wrong codes |
| `updated_at` | timestamptz, not null | rows older than a day are deleted |

There is never a raw address, and the key changes each day.

## State changes

```text
viewers.status:   active ──viewer revoke──▶ revoked      (no way back; add the person again for a new row)
viewers.tier:     guest ◀──viewer grant --tier──▶ trusted
session:          created at login ──▶ ends at expiry, log out, or revoke
login source:     counting ──6th wrong code in a minute──▶ refused for the rest of that minute
                  counting ──20th wrong code today──▶ locked for 15 minutes
```

## What the app role may do

| Table | SELECT | INSERT | UPDATE | DELETE |
|---|---|---|---|---|
| `viewers` | yes | no | `last_login_at` only | no |
| `viewer_pages` | yes | no | no | no |
| `sessions` | yes | yes | no | yes |
| `login_attempts` | yes | yes | yes | yes |

The owner role does everything else, and is used only by the commands on the owner's Mac.
