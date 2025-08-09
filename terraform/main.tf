terraform {
  required_version = ">= 1.1.3"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.89.0"
    }

    bunnynet = {
      source  = "BunnyWay/bunnynet"
      version = "0.6.1"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

provider "bunnynet" {
}

module "repo" {
  source = "git@github.com:taska-prosthetics/terraform-common.git//modules/container_repo?ref=798e623c1089991d7a6a23d382f1cd5a216a2cc0"

  repo_name = "website-django"
  count     = terraform.workspace == "prod" ? 1 : 0
}

module "repo_iam" {
  source = "git@github.com:taska-prosthetics/terraform-common.git//modules/container_repo_iam?ref=798e623c1089991d7a6a23d382f1cd5a216a2cc0"

  repo_name  = "website-django"
  iam_user   = aws_iam_user.github.name
  depends_on = [module.repo]
}
