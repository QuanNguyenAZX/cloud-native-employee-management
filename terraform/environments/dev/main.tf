module "security_group" {
  source = "../../modules/security-group"

  environment = var.environment
}

module "iam" {
  source = "../../modules/iam"

  environment = var.environment
}