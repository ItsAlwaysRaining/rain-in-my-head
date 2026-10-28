# Quickstart: first apply and checks

## Before you start (owner)

1. Create the accounts, tokens and passphrase, and the four GitHub secrets (see the to-do page).
2. Send Claude your Vercel **Team ID** (Settings → General) and your Neon **organization ID** (Organization settings → General, starts with `org-`). Neither is secret; both go in `infra/terraform.tfvars`.

## First apply, from your Mac (about 10 minutes)

Paste each value from your password manager when prompted. Nothing is echoed or saved to your shell history.

```sh
cd infra
read -s "VERCEL_API_TOKEN?Vercel token: " && export VERCEL_API_TOKEN
read -s "NEON_API_KEY?Neon API key: " && export NEON_API_KEY
read -s "GITHUB_TOKEN?GitHub infra token: " && export GITHUB_TOKEN
read -s "TF_VAR_state_passphrase?State passphrase: " && export TF_VAR_state_passphrase
tofu init
tofu plan     # read it: 1 Vercel project + 6 env vars, Neon project/branch/endpoint/role/db, 6 GitHub values, 4 passwords
tofu apply
git add terraform.tfstate && git commit -m "Initial encrypted infrastructure state" && git push
```

## Checks (SC-001, SC-002)

```sh
tofu plan -detailed-exitcode; echo $?          # 0 = no changes
python3 -c 'import json; print(sorted(json.load(open("terraform.tfstate"))))'   # only encrypted_data, encryption_version, lineage, meta, serial
grep -c neon.tech terraform.tfstate             # 0
gh secret list; gh variable list                # NEON_* secrets and VERCEL_* variables listed (names only)
```

Then check the dashboards:
- **Vercel:** project `rain-in-my-head`, Git not connected, Deployment Protection set to Standard, and 6 environment variables.
- **Neon:** project `rain-in-my-head` with branches `prod` and `dev`.

## Later changes

1. Open a PR that touches `infra/`, and read the plan comment.
2. Go to **Actions → Infrastructure → Run workflow** and choose the PR's branch.
3. The encrypted state is committed to the branch. Merge the PR.
