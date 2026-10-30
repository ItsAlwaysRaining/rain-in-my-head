# Proposal

## Why

The hosted site will only have a `.vercel.app` address. The owner bought `storyandstructure.studio` on Spaceship on 30 Oct and wants the site at `rain.storyandstructure.studio`. The constitution and CLAUDE.md say hosting changes are made in `infra/` through a pull request, so the domain has to be declared there, not added in the Vercel dashboard.

## What Changes

- Add `vercel_project_domain` for `rain.storyandstructure.studio` to the existing Vercel project in `infra/vercel.tf`. The name is a variable with that default, so `infra/` has no hard-coded host and a later rename is a one-line change.
- Output the domain name from `infra/outputs.tf` (not a secret).
- Keep the `.vercel.app` address working as a backup. It needs no code: Vercel keeps it as long as the project exists.
- Add a short note to the README's "Hosting infrastructure" section: after the apply, add one CNAME record at Spaceship, using the target value Vercel shows for the domain.
- No `www` redirect and no apex (bare name) domain. The bare `storyandstructure.studio` stays free for a future Story and Structure site.
- No new dependency: the `vercel` provider is already pinned at 5.21.1 and has this resource.

Not in this change: the DNS record itself (done by the owner at Spaceship, because that is where the DNS is kept), pointing the nameservers at Vercel, and updating links that mention the `.vercel.app` address (a follow-up once the domain works).

## Capabilities

### New Capabilities
- `custom-domain`: the hosted site is reachable at `rain.storyandstructure.studio` over https, declared in code, with the `.vercel.app` address kept as a backup.

### Modified Capabilities

None. Spec 010 (Spec Kit) covers the infrastructure as a whole; this adds one resource to it and does not change any of its requirements.

## Impact

- `infra/vercel.tf`, `infra/variables.tf`, `infra/outputs.tf`: one resource, one variable, one output.
- `README.md`: a short paragraph under "Hosting infrastructure".
- The PR's plan check should show 1 to add, 0 to change, 0 to destroy. The apply runs from **Actions → Infrastructure → Run workflow** on a throwaway branch, after the merge.
- Until phase 6 deploys the site, the domain shows Vercel's "deployment not found" page. That is expected.
- Constitution VII (free plans, no card): a domain on a Hobby project is free on Vercel's side. The only cost is the yearly Spaceship renewal, which the owner already pays.
