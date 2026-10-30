# Tasks

## 1. Declare the domain

- [x] 1.1 `infra/variables.tf`: add `site_domain` (string, default `rain.storyandstructure.studio`, with a description saying it isn't a secret). Verify `tofu validate` in `infra/` passes.
- [x] 1.2 `infra/vercel.tf`: add `vercel_project_domain.site` with `project_id = vercel_project.site.id`, `domain = var.site_domain` and no `redirect`. Verify `tofu validate` passes and `git grep -n "storyandstructure" infra/` finds the host only in `variables.tf`.
- [x] 1.3 `infra/outputs.tf`: add a `site_domain` output. Verify `tofu validate` passes.

## 2. Document it

- [x] 2.1 `README.md`, "Hosting infrastructure": add a "Custom domain" paragraph covering the CNAME record at Spaceship (host `rain`, value as shown on the project's Domains page in Vercel, nameservers left as Spaceship's, default records for that host deleted first), the `dig +short rain.storyandstructure.studio` check, the expected "deployment not found" page until phase 6, and that the `.vercel.app` address stays as a backup. Verify the paragraph contains no secret and that its one command runs as written.

## 3. Check the plan and open the PR

- [x] 3.1 Load `TF_VAR_state_passphrase` and the three tokens as in `specs/010-infrastructure/quickstart.md`, then run `tofu plan` in `infra/`. Verify it says 1 to add, 0 to change, 0 to destroy, and that the only new resource is the domain. Do not apply it.
- [x] 3.2 `/opsx:archive` the change on the branch, so the PR includes the new `openspec/specs/custom-domain/spec.md`. Verify the file exists and `openspec list` no longer shows `custom-domain` as in progress.
- [ ] 3.3 Push `feature/custom-domain` and open a draft PR with `.github/pull_request_template.md`. Verify the Infrastructure workflow's plan comment on the PR says 1 to add, 0 to change, 0 to destroy, and the PR's "How it was tested" lists the local plan and what wasn't checked (the apply, DNS and https, which come after the merge).

## 4. After the merge (owner steps, not Claude's)

- [ ] 4.1 Owner: merge the PR, then run **Actions → Infrastructure → Run workflow** from a throwaway branch such as `chore/attach-domain`. Verify the log says 1 added, 0 changed, 0 destroyed, then delete the throwaway branch.
- [ ] 4.2 Owner: add the CNAME record at Spaceship using the value Vercel shows. Verify `dig +short rain.storyandstructure.studio` prints a Vercel name and IP addresses, and Vercel's Domains page shows Valid Configuration.
- [ ] 4.3 Owner: open `https://rain.storyandstructure.studio`. Verify there is a padlock and a Vercel page (a 404 is fine before phase 6), and that `http://` jumps to `https://`.
- [ ] 4.4 Claude: after 4.1, run a second `tofu plan` and verify it shows 0 changes. Then list the files that mention the `.vercel.app` address and propose the link updates in a small follow-up PR.
