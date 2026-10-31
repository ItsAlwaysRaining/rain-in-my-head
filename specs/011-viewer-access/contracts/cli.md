# Contract: the `viewer` commands

Run on the owner's Mac only. Every command takes `--env dev|prod` (default `dev`) and prints `[dev]` or `[prod]` on its first line. They read the owner URL from `.env`: `VIEWERS_OWNER_URL_DEV` or `VIEWERS_OWNER_URL_PROD`. A missing value ends the command with a message naming the variable (never its value).

| Command | What it does | Output |
|---|---|---|
| `viewer init` | Creates the app role `rain_app` (password taken from `VIEWERS_APP_URL_<ENV>`), the four tables and the app role's grants. Safe to run again. | `[dev] ready: 4 tables, role rain_app` |
| `viewer add NAME [--tier guest\|trusted]` | Makes a person and a code. Refuses a name that already has an active code. | `[dev] added Sam (guest)` then `code: xxxx-xxxx-xxxx-xxxx` once, and a reminder that it can't be shown again |
| `viewer list` | Shows every person, newest first. | Table: name, tier, extra pages, status, created, last login |
| `viewer revoke NAME` | Marks the active code revoked and deletes its sessions. | `[dev] revoked Sam, ended 2 sessions` |
| `viewer grant NAME [--page KEY] [--remove-page KEY] [--tier guest\|trusted]` | Adds or takes a page, or changes the tier. At least one option is required. | `[dev] Sam: +analyst` |

**Errors** end with exit code 1 and one plain line: unknown name, unknown page key (the message lists the valid keys), a revoked person (`viewer grant` refuses, since they have no active code), and a database that can't be reached.

**Never printed**: a code after `add`, a connection string, or a password.

**Page keys**: `overview`, `new-artists`, `genre`, `artist`, `slot`, `mainstream`, `analyst`, `ai`, `storm`, `about`, `contact`.
