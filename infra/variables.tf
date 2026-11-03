variable "state_passphrase" {
  description = "Encrypts the committed state and plans. Set as TF_VAR_state_passphrase; at least 16 characters."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.state_passphrase) >= 16
    error_message = "The state passphrase must be at least 16 characters."
  }
}

variable "vercel_team_id" {
  description = "The Vercel team the project lives in (Settings > General > Team ID). Not a secret: set in terraform.tfvars."
  type        = string
}

variable "neon_org_id" {
  description = "The Neon organization the project lives in (Organization settings > General). Neon requires it for new projects. Not a secret: set in terraform.tfvars."
  type        = string
}

variable "github_owner" {
  description = "GitHub account that owns the repository."
  type        = string
  default     = "ItsAlwaysRaining"
}

variable "github_repository" {
  description = "Repository whose Actions secrets and variables are managed here."
  type        = string
  default     = "rain-in-my-head"
}

variable "site_domain" {
  description = "Custom domain for the site, a subdomain of a domain whose DNS is kept at Cloudflare (registered at Spaceship). Not a secret. The DNS record is added by hand (README, Hosting infrastructure)."
  type        = string
  default     = "rain.storyandstructure.studio"
}

variable "neon_region" {
  description = "Neon region, close to Vercel's default function region (iad1)."
  type        = string
  default     = "aws-us-east-1"
}
