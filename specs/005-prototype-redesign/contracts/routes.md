# Contract: Web Routes

The app's public interface is its URLs, which people bookmark. The API is unchanged; see `specs/003-typescript-dashboard/contracts/api.md`.

| Path | Page | Top-bar section | Breadcrumb |
|---|---|---|---|
| `/` | Home (Coming Soon, #27) | — | — |
| `/dashboards` | Overview | Dashboards | Home › Dashboards |
| `/dashboards/new-artists?month=` | New artists | Dashboards | Home › Dashboards › New artists |
| `/dashboards/genre?genre=&start=&end=` | Genre | Dashboards | Home › Dashboards › Genre |
| `/dashboards/artist?artist=&start=&end=` | Artist | Dashboards | Home › Dashboards › Artist |
| `/dashboards/slot` | Listening slot (Coming Soon, #30) | Dashboards | Home › Dashboards › When you listen |
| `/dashboards/mainstream` | Mainstream vs. niche (Coming Soon, #12) | Dashboards | Home › Dashboards › Mainstream vs. niche |
| `/playlists?type=` | Playlist Generator | Playlist Generator | Home › Playlist Generator |
| `/analyst` | Analyst (SQL + Schema) | Analyst | Home › Analyst |
| `/ai` | AI (Coming Soon, #32) | AI | Home › AI |
| `/about` | About (Coming Soon, #33) | About | Home › About |
| `/contact` | Contact Me (Coming Soon, #34) | Contact Me | Home › Contact Me |
| `/storm` | Storm (Coming Soon, #28) | — | Home › Storm |
| anything else | Not found | — | Home › Not found |

## Redirects (query string kept)

| Old | New |
|---|---|
| `/genre` | `/dashboards/genre` |
| `/artist` | `/dashboards/artist` |
| `/sql` | `/analyst` |
| `/schema` | `/analyst?schema=open` |
