# The site: the TypeScript dashboard plus the API as one Python function. No Git connection: CI builds and
# deploys with the Vercel CLI (phase 6), so pushes to GitHub never deploy on their own.

resource "vercel_project" "site" {
  name      = "rain-in-my-head"
  framework = null

  resource_config = {
    function_default_regions = ["iad1"] # next to Neon aws-us-east-1
  }

  # Preview deployments (dev) need a Vercel login with access to this team.
  vercel_authentication = {
    deployment_type = "standard_protection"
  }
}

# No redirect, so the .vercel.app address keeps serving the site as a backup. The DNS record is added by hand at Spaceship.
resource "vercel_project_domain" "site" {
  project_id = vercel_project.site.id
  domain     = var.site_domain
}

resource "random_password" "session_prod" {
  length  = 64
  special = false
}

resource "random_password" "session_dev" {
  length  = 64
  special = false
}

locals {
  site_env = {
    production = { database_url = local.prod_app_url, session_secret = random_password.session_prod.result }
    preview    = { database_url = local.dev_app_url, session_secret = random_password.session_dev.result }
  }
}

resource "vercel_project_environment_variable" "hosted" {
  for_each = local.site_env

  project_id = vercel_project.site.id
  key        = "LISTENING_HOSTED"
  value      = "1"
  target     = [each.key]
  sensitive  = false
  comment    = "Hosted mode: immutable database, refuses writes, playlists, typed SQL and AI"
}

resource "vercel_project_environment_variable" "database_url" {
  for_each = local.site_env

  project_id = vercel_project.site.id
  key        = "DATABASE_URL"
  value      = each.value.database_url
  target     = [each.key]
  sensitive  = true
  comment    = "Neon, app role only (${each.key == "production" ? "prod" : "dev"} branch)"
}

resource "vercel_project_environment_variable" "session_secret" {
  for_each = local.site_env

  project_id = vercel_project.site.id
  key        = "SESSION_SECRET"
  value      = each.value.session_secret
  target     = [each.key]
  sensitive  = true
  comment    = "Signs visitor session cookies"
}
