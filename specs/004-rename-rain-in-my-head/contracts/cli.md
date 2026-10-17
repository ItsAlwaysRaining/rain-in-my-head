# Contract: Command line

The command is renamed; its subcommands, options, output and exit codes are unchanged.

| Before | After |
|---|---|
| `uv run listening fetch` | `uv run rain-in-my-head fetch` |
| `uv run listening build` | `uv run rain-in-my-head build` |
| `uv run listening enrich [--limit N]` | `uv run rain-in-my-head enrich [--limit N]` |
| `uv run listening stats` | `uv run rain-in-my-head stats` |
| `uv run listening serve [--dev] [--host] [--port]` | `uv run rain-in-my-head serve [--dev] [--host] [--port]` |
| `uv run listening spotify-login` | `uv run rain-in-my-head spotify-login` |
| `uv run listening playlist …` | `uv run rain-in-my-head playlist …` |
| `uv run --no-default-groups listening fetch` (sync workflow) | `uv run --no-default-groups rain-in-my-head fetch` |

- `uv run rain-in-my-head --help` shows `usage: rain-in-my-head …`.
- `uv run listening …` fails with uv's "Failed to spawn: `listening`" (no alias, FR-002).
- Messages that tell the user what to run (no database, not logged in to Spotify, run enrich) quote
  the new command, in the CLI, both dashboards and the API's `no_database` error.

## Web

- `GET /api/*` routes and response shapes are unchanged. The `no_database` message text quotes the
  new command. The OpenAPI title is "Rain in My Head".
