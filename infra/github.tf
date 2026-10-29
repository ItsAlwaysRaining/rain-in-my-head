# Values the deploy (phase 6) and clean-up (phase 7) workflows read. Written here so nobody copies them by hand.

resource "github_actions_variable" "vercel_project_id" {
  repository    = var.github_repository
  variable_name = "VERCEL_PROJECT_ID"
  value         = vercel_project.site.id
}

resource "github_actions_variable" "vercel_org_id" {
  repository    = var.github_repository
  variable_name = "VERCEL_ORG_ID"
  value         = var.vercel_team_id
}

# Owner-role connection strings: for creating tables and the app role (phase 4) and deleting old events
# (phase 7). The website never sees these.
resource "github_actions_secret" "neon_prod_owner_url" {
  repository      = var.github_repository
  secret_name     = "NEON_PROD_OWNER_URL"
  plaintext_value = local.prod_owner_url
}

resource "github_actions_secret" "neon_dev_owner_url" {
  repository      = var.github_repository
  secret_name     = "NEON_DEV_OWNER_URL"
  plaintext_value = local.dev_owner_url
}

# App-role connection strings, so phase 4's migration can create rain_app with the same password the site uses.
resource "github_actions_secret" "neon_prod_app_url" {
  repository      = var.github_repository
  secret_name     = "NEON_PROD_APP_URL"
  plaintext_value = local.prod_app_url
}

resource "github_actions_secret" "neon_dev_app_url" {
  repository      = var.github_repository
  secret_name     = "NEON_DEV_APP_URL"
  plaintext_value = local.dev_app_url
}
