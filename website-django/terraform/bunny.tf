resource "bunnynet_compute_script" "auth" {
  type    = "middleware"
  name    = "website-django-${terraform.workspace}-auth"
  content = file("bunny-cf-auth.js")
}

resource "bunnynet_storage_zone" "content" {
  name      = "website-django-${terraform.workspace}-content"
  region    = "DE"
  zone_tier = "Standard"
}

resource "bunnynet_pullzone" "content" {
  name = "website-django-${terraform.workspace}-content"

  origin {
    type              = "StorageZone"
    storagezone       = bunnynet_storage_zone.content.id
    middleware_script = bunnynet_compute_script.auth.id
  }

  routing {
    tier    = "Standard"
    zones   = ["ASIA", "EU", "US"]
    filters = ["scripting"]
  }
}

resource "bunnynet_pullzone_hostname" "content" {
  pullzone = bunnynet_pullzone.content.id
  name     = var.content_hostname
}
