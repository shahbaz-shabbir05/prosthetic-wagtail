resource "aws_iam_user" "github" {
  name = "github-website-django-${terraform.workspace}"
}

resource "aws_iam_group" "github" {
  name = "website-django-${terraform.workspace}-group"
}

resource "aws_iam_user_group_membership" "github" {
  user = aws_iam_user.github.name

  groups = [
    aws_iam_group.github.name
  ]
}

resource "aws_iam_access_key" "github" {
  user = aws_iam_user.github.name
}

module "ecs-service" {
  source = "git@github.com:taska-prosthetics/terraform-common.git//modules/ecs_service?ref=53cbf113ed5c4b9c7ce4e0fd83d9de6c3182b2be"

  service_name      = "website-django-${terraform.workspace}"
  container_port    = 8000
  ecs_cluster_id    = "arn:aws:ecs:eu-central-1:846818632671:cluster/shared"
  vpc_id            = "vpc-091e4d4535aee2805"
  health_check_path = "/static/css/taska.css"
  # Listens on the HTTP listener - taska.nz isn't tls between Cloudflare and the ALB
  alb_listener_arn       = "arn:aws:elasticloadbalancing:eu-central-1:846818632671:listener/app/shared/da4b7b6dba30d315/81f371fb271d577f"
  alb_rule_priority      = var.elb_priority
  alb_hostname           = var.hostname
  deploy_iam_user        = aws_iam_user.github.name
  capacity_provider_name = "shared"
  service_desired_count  = 2
  enable_exec            = true
  deploy_group           = aws_iam_group.github.name
}

module "ecs-service-worker" {
  source = "git@github.com:taska-prosthetics/terraform-common.git//modules/ecs_service?ref=53cbf113ed5c4b9c7ce4e0fd83d9de6c3182b2be"

  service_name           = "website-django-worker-${terraform.workspace}"
  ecs_cluster_id         = "arn:aws:ecs:eu-central-1:846818632671:cluster/shared"
  vpc_id                 = "vpc-091e4d4535aee2805"
  deploy_iam_user        = aws_iam_user.github.name
  capacity_provider_name = "shared"
  service_desired_count  = 1
  enable_exec            = true
  deploy_group           = aws_iam_group.github.name
}

module "db" {
  source = "git@github.com:taska-prosthetics/terraform-common.git//modules/rds_db?ref=0c65a3da4d4096b7a24d1e6088546dbd8d907667"

  username           = "website-django-${terraform.workspace}"
  db_name            = "website-django-${terraform.workspace}"
  cluster_id         = "arn:aws:rds:eu-central-1:846818632671:cluster:shared"
  secret_name        = "website-django/${terraform.workspace}/rds"
  execution_role_arn = module.ecs-service.execution_role.name
}

resource "random_password" "django_secret_key" {
  length  = 60
  special = true
}

resource "aws_secretsmanager_secret" "django_config" {
  name = "website-django/${terraform.workspace}/django_config"
}

resource "aws_secretsmanager_secret_version" "django_config" {
  secret_id = aws_secretsmanager_secret.django_config.id
  secret_string = templatefile("${path.module}/django_conf.tftpl", {
    config = {
      DJANGO_SECRET_KEY    = random_password.django_secret_key.result,
      BUNNYCDN_ZONE        = "website-django-${terraform.workspace}-content"
      BUNNYCDN_KEY         = bunnynet_storage_zone.content.password
      CSRF_TRUSTED_ORIGINS = "https://${var.hostname}"
    }
  })
}

resource "aws_secretsmanager_secret" "worker_config" {
  name = "website-django/${terraform.workspace}/worker_config"
}

resource "aws_secretsmanager_secret_version" "worker_config" {
  secret_id = aws_secretsmanager_secret.worker_config.id
  secret_string = templatefile("${path.module}/django_conf.tftpl", {
    config = {
      DJANGO_SECRET_KEY    = random_password.django_secret_key.result,
      BUNNYCDN_ZONE        = "website-django-${terraform.workspace}-content"
      BUNNYCDN_KEY         = bunnynet_storage_zone.content.password
      CSRF_TRUSTED_ORIGINS = "https://${var.hostname}"
    }
  })
}

resource "aws_iam_role_policy" "execution-secrets" {
  name = "website-django-${terraform.workspace}-secrets"
  role = module.ecs-service.execution_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ],
        "Resource" : [
          aws_secretsmanager_secret.django_config.id
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : "secretsmanager:ListSecrets",
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "execution-secrets-worker" {
  name = "website-django-worker-${terraform.workspace}-secrets"
  role = module.ecs-service-worker.execution_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ],
        "Resource" : [
          aws_secretsmanager_secret.worker_config.id,
          module.db.secret-arn
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : "secretsmanager:ListSecrets",
        "Resource" : "*"
      }
    ]
  })
}
