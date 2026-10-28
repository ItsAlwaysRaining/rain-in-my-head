# Everything hosted for Rain in My Head: the Vercel site, Neon visitor data and the GitHub Actions values the
# workflows read (specs/010-infrastructure). Change hosting only here, through a pull request.
#
# Credentials come from the environment, never from files:
#   VERCEL_API_TOKEN, NEON_API_KEY, GITHUB_TOKEN (the fine-grained GH_INFRA_TOKEN),
#   TF_VAR_state_passphrase (encrypts the state committed next to this file).

terraform {
  required_version = ">= 1.10"

  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "5.21.1"
    }
    neon = {
      source  = "kislerdm/neon"
      version = "0.18.0"
    }
    github = {
      source  = "integrations/github"
      version = "6.13.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.9.1"
    }
  }

  # State and saved plans are encrypted before they're written, so terraform.tfstate can be committed.
  encryption {
    key_provider "pbkdf2" "passphrase" {
      passphrase = var.state_passphrase
    }

    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.passphrase
    }

    state {
      method   = method.aes_gcm.state
      enforced = true
    }

    plan {
      method   = method.aes_gcm.state
      enforced = true
    }
  }
}

provider "vercel" {
  team = var.vercel_team_id
}

provider "neon" {}

provider "github" {
  owner = var.github_owner
}
