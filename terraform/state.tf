terraform {
  backend "s3" {
    bucket               = "tfstate.taskaprosthetics.com"
    workspace_key_prefix = "website-django"
    key                  = "tfstate"
    region               = "eu-central-1"

    dynamodb_table = "terraform-locks-website-django"
    encrypt        = true
  }
}
