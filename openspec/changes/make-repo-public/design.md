# Design

## Context

See proposal.md for why. Today `analytics.yml` runs nightly at 02:43 UTC and does two things: `viewer prune` (deletes usage records older than 12 months) and `viewer export` followed by a force-push of the two CSVs to the `analytics` branch. Only the second step is a problem in a public repository. The prune is called from nowhere else, so deleting the workflow without a replacement would silently end the 12-month promise made on the login page.

Observed in the repo: the visitor CSVs exist on exactly two refs, `origin/analytics` and `origin/analytics-dev` (one commit each). Four analytics workflow runs exist. `infra/github.tf` sets `NEON_PROD_OWNER_URL` and `NEON_DEV_OWNER_URL`, used only by `analytics.yml`. `deploy.yml` (nightly rebuild at 03:00 UTC) does not hold those secrets.

## Goals / Non-Goals

**Goals:**
- No visitor data reachable from the public repository, now or after the flip.
- The 12-month deletion keeps running every night with the same output (a count, nothing else).
- The docs and constitution tell the truth about a public repository.

**Non-Goals:**
- Flipping visibility or deleting remote branches and runs (owner steps, after merge).
- A replacement backup of visitor data. The owner chose to stop the export.
- Removing the `viewer export` CLI command. It writes to a local folder and never touches git.
- Changing `infra/`.

## Decisions

**1. A new `prune.yml`, not a step in `deploy.yml`.** The deploy workflow handles Vercel tokens and builds from the repo. Adding the database owner connection there gives that larger workflow a powerful secret it does not need. A 20-line workflow that holds only the owner URL and runs one command keeps each secret with the smallest set of code. Alternative considered: add the step to the nightly deploy. Rejected for the secret reach, and because a failed deploy would then also skip the prune.

**2. Keep the schedule (02:43 UTC), the `prod`/`dev` choice, the concurrency group and `permissions: contents: read`.** The new workflow never writes to the repository, so it drops `contents: write`. That also makes it impossible for this job to publish data by accident.

**3. Delete the workflow runs and branches, not only the files.** Deleting `analytics.yml` leaves its old run logs, and force-push output in those logs includes commit hashes. An unreachable commit stays fetchable by hash for a while. Once the repository is public, anyone who reads a run log could fetch a copy of visitor names. The owner therefore deletes the two branches and all analytics runs before flipping, in that order.

**4. Constitution bump is MINOR (1.3.0).** Governance reserves MAJOR for removing or redefining a principle. No principle changes, but the Data and Privacy guidance changes materially (private to public, a new rule that visitor data never enters the repository), which is MINOR.

**5. Spec 012 gets short "superseded" notes, not a rewrite.** It is a Spec Kit spec and a record of what was built. Rewriting it would hide history. The notes point to this change. CLAUDE.md says the spec is updated first when code differs, so the notes land in the same PR.

## Risks / Trade-offs

- [Visitor data loses its backup outside Neon; the free database could lose it] → Accepted by the owner. The data is only 12 months of usage and a short list of invited people, and `viewer export` can still be run by hand on the Mac.
- [Old commits of visitor data stay fetchable by hash after branch deletion] → Delete the old runs before the flip so no log shows a hash; no one else has them while the repository is private. If doubt remains, ask GitHub Support to run garbage collection.
- [Public Actions logs] → The prune prints counts only. Checked in task 3.
- [Branch protection now free, but `sync.yml` pushes to `main` every 6 hours] → Not enabled here. If the owner enables it later, the Actions bot needs a bypass. Noted in CLAUDE.md.
- [Encrypted state is public] → Depends on the passphrase. Owner confirmed it is strong and single-use.
- [Public repository invites pull requests and forks] → Fork PRs already get no secrets (production-deploy spec). Owner may also set "Require approval for first-time contributors" in Settings, which is not part of this change.
