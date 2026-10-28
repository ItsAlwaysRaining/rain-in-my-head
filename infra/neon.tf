# Visitor data (codes, sessions, events) lives in Neon; listening data never does.
#
# Each branch has an owner role, made here, which owns the database and is used only by OpenTofu, the
# nightly clean-up and the owner's Mac. The website's app role is NOT made here: roles created through
# Neon's API are members of neon_superuser, which is far more than the site needs. Phase 4 creates the
# app role with plain SQL (as the owner role) using the password generated below, then grants it only
# what it needs on the visitor tables.

resource "neon_project" "visitors" {
  name                      = "rain-in-my-head"
  org_id                    = var.neon_org_id
  region_id                 = var.neon_region
  pg_version                = 17
  history_retention_seconds = 21600 # 6 hours, within the free plan

  # The project's default branch is production.
  branch {
    name          = "prod"
    database_name = "visitors"
    role_name     = "rain_owner"
  }

  primary_compute {
    autoscaling_limit_min_cu = 0.25
    autoscaling_limit_max_cu = 0.25
  }
}

resource "neon_branch" "dev" {
  project_id = neon_project.visitors.id
  parent_id  = neon_project.visitors.default_branch_id
  name       = "dev"
}

resource "neon_endpoint" "dev" {
  project_id = neon_project.visitors.id
  branch_id  = neon_branch.dev.id
  type       = "read_write"

  autoscaling_limit_min_cu = 0.25
  autoscaling_limit_max_cu = 0.25
}

# dev starts as a copy of prod, so it also has rain_owner and visitors. Its own names keep the two apart.
resource "neon_role" "dev_owner" {
  project_id = neon_project.visitors.id
  branch_id  = neon_branch.dev.id
  name       = "rain_dev_owner"
}

resource "neon_database" "dev" {
  project_id = neon_project.visitors.id
  branch_id  = neon_branch.dev.id
  name       = "visitors_dev"
  owner_name = neon_role.dev_owner.name
}

# Passwords for the app roles that phase 4 creates with SQL.
resource "random_password" "app_prod" {
  length  = 40
  special = false
}

resource "random_password" "app_dev" {
  length  = 40
  special = false
}

locals {
  app_role = "rain_app"

  prod_host = neon_project.visitors.database_host
  dev_host  = neon_endpoint.dev.host

  prod_owner_url = "postgresql://${neon_project.visitors.database_user}:${neon_project.visitors.database_password}@${local.prod_host}/${neon_project.visitors.database_name}?sslmode=require"
  dev_owner_url  = "postgresql://${neon_role.dev_owner.name}:${neon_role.dev_owner.password}@${local.dev_host}/${neon_database.dev.name}?sslmode=require"

  prod_app_url = "postgresql://${local.app_role}:${random_password.app_prod.result}@${local.prod_host}/${neon_project.visitors.database_name}?sslmode=require"
  dev_app_url  = "postgresql://${local.app_role}:${random_password.app_dev.result}@${local.dev_host}/${neon_database.dev.name}?sslmode=require"
}
