# Spec Delta

## Purpose

The hosted site's own web address, `rain.storyandstructure.studio`, set up in code like the rest of the hosting, with the `.vercel.app` address kept as a backup.

## ADDED Requirements

### Requirement: Site reachable at the custom address over https
Once the owner has added the DNS record, the hosted site SHALL be reachable at `https://rain.storyandstructure.studio` with a valid certificate. Requests to the `http://` address SHALL be sent on to `https://`.

#### Scenario: Open the address after the DNS record spreads
- **WHEN** a browser opens `https://rain.storyandstructure.studio` after the DNS record has spread
- **THEN** the page loads with no certificate warning and the browser shows a padlock

#### Scenario: Plain http
- **WHEN** a browser opens `http://rain.storyandstructure.studio`
- **THEN** it ends up on the `https://` address

#### Scenario: Before the first deploy
- **WHEN** the domain is attached but the site has not been deployed yet
- **THEN** the address shows Vercel's "deployment not found" page over https, and nothing else is served

### Requirement: Backup address keeps working
The site SHALL stay reachable at its `.vercel.app` address after the custom domain is attached. The custom domain SHALL NOT redirect it.

#### Scenario: Backup address
- **WHEN** a browser opens the project's `.vercel.app` address after the domain is attached
- **THEN** it serves the same site as before, with no redirect to the custom address

### Requirement: Only the subdomain is attached
The project SHALL have exactly one custom domain, `rain.storyandstructure.studio`. The bare `storyandstructure.studio` and `www.storyandstructure.studio` SHALL NOT be attached to it.

#### Scenario: Bare name left free
- **WHEN** the project's domains are listed after the change is applied
- **THEN** only `rain.storyandstructure.studio` appears, besides the `.vercel.app` address

### Requirement: Declared in code, applied only on request
The domain SHALL be declared in `infra/` and attached by the same manual **Run workflow** apply as other hosting changes. Merging the pull request SHALL NOT attach it, and a plan of the unchanged code afterwards SHALL show no changes.

#### Scenario: Plan on the pull request
- **WHEN** the pull request that adds the domain is checked
- **THEN** the plan comment shows 1 to add, 0 to change and 0 to destroy

#### Scenario: Merge does not apply
- **WHEN** the pull request is merged
- **THEN** the Vercel project's domain list is unchanged until someone runs the workflow

#### Scenario: Nothing drifts after the apply
- **WHEN** the apply has finished and a new plan is made
- **THEN** it shows 0 to add, 0 to change and 0 to destroy

### Requirement: No new secrets and no change to access
Attaching the domain SHALL NOT add a secret, change who can open a page, or change the Preview deployments' login protection. Visitors' login codes and sessions SHALL work the same on the custom address as on the backup address, each address keeping its own session cookie.

#### Scenario: Preview protection unchanged
- **WHEN** the plan for the change is read
- **THEN** it contains no change to the project's authentication settings or environment variables

#### Scenario: Login on the custom address
- **WHEN** a visitor with a valid code logs in at the custom address, once the site is deployed
- **THEN** they are signed in on that address only, and are not signed in on the `.vercel.app` address
