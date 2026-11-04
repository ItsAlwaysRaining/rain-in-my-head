# production-deploy Specification

## Purpose
The live site at `rain.storyandstructure.studio` is deployed from `main` and rebuilt every night, so it always serves the newest committed plays on the `prod` visitor data. Each deploy is checked before visitors see it, and a deploy that fails the check never goes live.

## Requirements

### Requirement: A merge deploys production
When a commit is pushed to `main`, a workflow SHALL build the two-year dataset and the site and deploy them to Vercel as the **production** deployment. Pull requests, forks and other branches SHALL NOT deploy to production.

#### Scenario: Merge a pull request
- **WHEN** the owner merges a pull request into `main`
- **THEN** within about ten minutes `https://rain.storyandstructure.studio` serves the build of the merged commit

#### Scenario: Open a pull request
- **WHEN** a pull request is opened or updated
- **THEN** the production deployment is unchanged

#### Scenario: Pull request from a fork
- **WHEN** a pull request comes from a fork
- **THEN** no production deploy runs and no secret is exposed to it

### Requirement: Rebuilt every night at 03:00 UTC
The same workflow SHALL run every night at 03:00 UTC and deploy a fresh production build from the latest `main`, so the site's two-year window moves forward and new plays appear even when nothing was merged. The owner SHALL also be able to start it by hand.

#### Scenario: A quiet day
- **WHEN** no pull request was merged for a day and the 03:00 UTC run finishes
- **THEN** the production dataset's newest play is no more than 7 days older than the run, and its oldest play is no more than 738 days old

#### Scenario: New plays from the sync
- **WHEN** the scheduled sync commits new plays to `main` during the day
- **THEN** they appear on the site after the next 03:00 UTC run, or after the next merge, whichever is first

#### Scenario: Start it by hand
- **WHEN** the owner starts the workflow from the Actions page on `main`
- **THEN** it deploys production exactly like the nightly run

### Requirement: Production serves the real site on prod data
The production deployment SHALL serve the built dashboard and the API from the two-year dataset, and SHALL keep invite codes, sessions and usage records in the Neon `prod` branch only. It SHALL NOT read or write the `dev` branch. Every page except the landing page and login page SHALL still need an invite code.

#### Scenario: Open the address with no code
- **WHEN** a browser with no session opens `https://rain.storyandstructure.studio`
- **THEN** the landing page or the login page loads, and no listening data is shown

#### Scenario: Log in with a code made on prod
- **WHEN** a visitor enters an invite code created on the `prod` branch
- **THEN** the pages that code unlocks load with listening data

#### Scenario: A dev code on production
- **WHEN** someone enters an invite code that exists only on the `dev` branch
- **THEN** the login is refused like any unknown code

#### Scenario: Pages of the app load directly
- **WHEN** a browser opens the live address ending in an app route such as `/genre`
- **THEN** the app loads that page, not an error

### Requirement: Production bundle holds only what the site needs
The production function bundle SHALL follow the same rules as a preview's: it SHALL include `data/public.db` and `src/rain_in_my_head`, and SHALL NOT include `data/raw`, `data/cache`, `infra`, the tooling folders, a `.env` file, or any file of the full database (`data/listening.db` and its `-wal` and `-shm` side files). The workflow SHALL list the bundle before deploying and SHALL stop without deploying if a required file is missing or a forbidden path is present.

#### Scenario: A clean bundle
- **WHEN** the workflow lists the production function's files after the build
- **THEN** the required files are in the list, no forbidden path is, and the deploy goes ahead

#### Scenario: A forbidden file
- **WHEN** a forbidden path is in the list
- **THEN** the run fails before the deploy step and production keeps serving the previous build

### Requirement: The dataset window is checked before deploying
The workflow SHALL stop without deploying if the built dataset holds a play older than 738 days (the 730-day window, the 7-day lag, and one day of margin).

#### Scenario: A play outside the window
- **WHEN** the built dataset holds a play 739 days old
- **THEN** the run fails before the deploy step and production keeps serving the previous build

### Requirement: A new deployment must pass a check before it serves visitors
After building, the workflow SHALL put the new production deployment up without serving visitors from it yet, and SHALL ask it for `/api/health` and expect a successful answer saying the app is up. It SHALL also ask it for a locked data route with no session and expect a refusal. It SHALL retry for up to two minutes before giving up. Only a deployment that passes both checks SHALL become the one the live address serves. If either check fails, the live address SHALL keep serving the previous production deployment and the run SHALL finish red. The checks SHALL read no visitor data and SHALL print no secret.

#### Scenario: A healthy deploy
- **WHEN** the new deployment answers `/api/health` with `{"ok": true}` and refuses a locked data route with no session
- **THEN** the live address serves it and the run finishes green

#### Scenario: The app does not start
- **WHEN** `/api/health` keeps failing for two minutes
- **THEN** the live address still serves the previous production deployment and the run is red

#### Scenario: The login gate is missing
- **WHEN** a locked data route answers a request with no session with data instead of a refusal
- **THEN** the live address still serves the previous production deployment and the run is red

#### Scenario: The very first production deploy
- **WHEN** there is no earlier production deployment and the check fails
- **THEN** the live address still shows Vercel's "deployment not found" page and the run is red

### Requirement: One production deploy at a time
Production deploys SHALL run one after another. A deploy that is running SHALL NOT be cancelled by a newer one; the newer one SHALL wait.

#### Scenario: Merge during the nightly run
- **WHEN** a pull request is merged while the 03:00 UTC run is deploying
- **THEN** the nightly run finishes, then the merge's deploy runs

### Requirement: Secrets stay secret
The workflow SHALL read the Vercel token only from the repository's Actions secrets, SHALL NOT print it or any connection string, and SHALL NOT write secret values to the job summary or any comment.

#### Scenario: Read the logs
- **WHEN** the logs of a production run are searched for the token and for `postgres://`
- **THEN** neither is found
