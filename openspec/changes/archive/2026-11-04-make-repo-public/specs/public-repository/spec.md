# Spec Delta

## Purpose

States what the public repository contains and what it never contains, so that making it public exposes only what the owner has chosen to share.

## ADDED Requirements

### Requirement: Only chosen data is committed
Of the `data/` folder, the repository SHALL contain only `data/raw/` and `data/cache/`. Secrets (tokens, passphrases, connection strings), `data/listening.db` and its journal files, and `data/public.db` SHALL NOT be committed. The OpenTofu state in `infra/` SHALL be committed only encrypted.

#### Scenario: Tracked files
- **WHEN** the tracked files of `main` are listed
- **THEN** under `data/` only `data/raw/` and `data/cache/` appear, and no `.env`, key, or unencrypted state file appears

#### Scenario: Encrypted state
- **WHEN** `infra/terraform.tfstate` is opened
- **THEN** its contents are encrypted and a passphrase is needed to read any resource value

### Requirement: The docs describe the repository as public
Once the repository is public, `README.md`, `CLAUDE.md` and the constitution SHALL NOT call it private, SHALL NOT tell users to push to a private repository, and SHALL NOT describe a private branch for visitor data. The constitution SHALL state that all scrobbles since 2011 are public and that visitor data never enters the repository.

#### Scenario: Search for "private"
- **WHEN** the three docs are searched for statements that the repository or the `analytics` branch is private
- **THEN** there are none, and the README setup step says the listening history in `data/raw/` becomes public

#### Scenario: Constitution version
- **WHEN** the constitution is read
- **THEN** its Data and Privacy section matches this spec, and its version is 1.3.0 with Last Amended 2026-11-04

### Requirement: No workflow force-pushes
After the analytics workflow is removed, no workflow SHALL force-push any branch, and `CLAUDE.md` SHALL no longer list an exception.

#### Scenario: Workflow search
- **WHEN** `.github/workflows/` and `.github/scripts/` are searched for `push --force` or `--force-with-lease`
- **THEN** there are no matches
