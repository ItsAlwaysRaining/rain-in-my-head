# Design

## Context

`infra/vercel.tf` already declares the `vercel_project.site` project (no Git link, deployed by CI in phase 6). The provider is pinned at `vercel/vercel` 5.21.1, which has `vercel_project_domain`. The team ID is passed through the provider block, so the new resource needs only the project ID and the domain name. See proposal.md for why.

DNS for `storyandstructure.studio` stays at Spaceship (its default nameservers). Vercel cannot create records there, so the owner adds the record by hand. OpenTofu is not the place for it: there is no Spaceship provider in the project and adding one would be a new dependency and a new secret.

## Goals / Non-Goals

**Goals:**
- Attach `rain.storyandstructure.studio` to the project through the normal PR, plan, manual-apply flow.
- Keep the `.vercel.app` address working.
- Leave a README note that tells the owner exactly which record to add and how to check it.

**Non-Goals:**
- Managing DNS records, or moving the nameservers to Vercel.
- The bare name or `www`.
- Changing links in the README, quickstarts or specs that mention the `.vercel.app` address (a follow-up).

## Decisions

**A variable with a default, not a literal.** `variable "site_domain"` defaults to `rain.storyandstructure.studio`. Not a secret, so no tfvars entry is needed. Alternative: a literal in `vercel.tf`. Rejected because a rename would touch resource code rather than one default.

**No `redirect` on the domain.** With no redirect set, the `.vercel.app` address keeps serving the site, which is the backup the owner asked for. Alternative: redirect `.vercel.app` to the custom name. Rejected: it would break the backup.

**Subdomain, not the apex.** A subdomain needs one CNAME and leaves `storyandstructure.studio` free for the Story and Structure brand site. An apex needs an A record and uses up the bare name.

**Don't read the CNAME target from Terraform.** Vercel now gives project-specific DNS values and shows them on the project's Domains page, and the provider's domain resource doesn't expose a verified target. The README therefore says "use the value Vercel shows", rather than baking in an old value such as `cname.vercel-dns.com` that could go stale.

**Cookies need no change.** The session cookie is host-only, so each address has its own. That is why the spec says a login on one address doesn't carry to the other. Making the cookie shared across both would need a `Domain` attribute and is not wanted.

**Output the domain.** `outputs.tf` gets `site_domain` so the quickstart and the later link updates read it from one place.

## Risks / Trade-offs

- [Domain attached before DNS exists, so Vercel shows "Invalid Configuration"] → Expected. The README says so, and the check is `dig +short rain.storyandstructure.studio`.
- [The apply fails because the domain is already on another Vercel account or project] → It's a new domain, so unlikely. If it happens, the error names the other project, and the owner removes it there.
- [A wrong or default record at Spaceship (a parking page) shadows the CNAME] → The README tells the owner to delete default records for the `rain` host before adding the CNAME.
- [Domain expires and the address stops resolving] → The `.vercel.app` backup still works. The owner already has auto-renew on, and the to-do page has a renewal reminder.
- [Nameserver changes later at Spaceship] → Out of scope. The README says the nameservers must stay Spaceship's.
