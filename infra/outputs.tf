output "vercel_project_id" {
  value = vercel_project.site.id
}

output "neon_project_id" {
  value = neon_project.visitors.id
}

# For the owner's Mac (.env), e.g. `tofu output -raw prod_owner_url`. Never printed in plans or logs.
output "prod_owner_url" {
  value     = local.prod_owner_url
  sensitive = true
}

output "dev_owner_url" {
  value     = local.dev_owner_url
  sensitive = true
}

# The site's database role, for `viewer init` and for running the site locally in hosted mode against dev.
# Same rules as the owner URLs above: read them with `tofu output -raw`, never print them.
output "prod_app_url" {
  value     = local.prod_app_url
  sensitive = true
}

output "dev_app_url" {
  value     = local.dev_app_url
  sensitive = true
}
