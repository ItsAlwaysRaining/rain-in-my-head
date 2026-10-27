# Data Model: Prototype Redesign

No new data, tables or API shapes. Everything here is front-end only.

## Route entry (`web/src/routes.ts`)

| Field | Meaning |
|---|---|
| `path` | URL path, e.g. `/dashboards/new-artists` |
| `label` | Breadcrumb label, e.g. "New artists" |
| `section` | Top-bar section it belongs to: `dashboards`, `playlists`, `analyst`, `about`, `contact`, or none (home, storm) |

## Placeholder (Coming Soon)

| Field | Meaning |
|---|---|
| `title` | Page or tab title |
| `description` | One or two sentences on the planned feature |
| `issue` | GitHub issue number. The link is `https://github.com/ItsAlwaysRaining/rain-in-my-head/issues/<n>` |

| Placeholder | Issue |
|---|---|
| Home (Landing) | 27 |
| Storm | 28 |
| Listening slot | 30 |
| Mainstream vs. niche | 12 |
| About | 33 |
| Contact Me | 34 |
| SQL playlist tab | 31 |
| AI playlist tab | 32 |

## URL state

- Dashboards: `preset`, `start`, `end`, `grain`, `measure`, `period`. These are unchanged and carried into Genre, Artist and New artists so "Back to Dashboards" can restore them.
- New artists: `month` (an `over_time.period` label at month grain).
- Playlists: `type` = `slot | discovery | binges | ai | sql`.
- Analyst: `schema=open` expands the schema card.
