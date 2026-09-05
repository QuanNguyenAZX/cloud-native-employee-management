data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

module "vpc" {
  source = "../../modules/vpc"

  name = "employee-prod"

  vpc_cidr = "10.1.0.0/16"

  public_subnet_cidrs = [
    "10.1.1.0/24",
    "10.1.2.0/24",
  ]

  private_subnet_cidrs = [
    "10.1.3.0/24",
    "10.1.4.0/24",
  ]
}

module "security_group" {
  source = "../../modules/security-group"

  name = "employee-prod"

  vpc_id = module.vpc.vpc_id

  ssh_cidr = var.ssh_cidr
}

module "ec2" {
  source = "../../modules/ec2"

  name = "employee-prod-ec2"

  ami_id = data.aws_ami.ubuntu.id

  instance_type = "t3.micro"

  subnet_id = module.vpc.public_subnet_ids[0]

  security_group_id = module.security_group.app_security_group_id

  key_name = "employee-dev-key"
}

module "rds" {
  source = "../../modules/rds"

  name = "employee-prod-db"

  engine         = "postgres"
  engine_version = "17"
  instance_class = "db.t3.micro"

  allocated_storage = 20

  db_name  = "employee"
  username = "postgres"
  password = var.db_password

  subnet_ids = module.vpc.private_subnet_ids

  security_group_id = module.security_group.db_security_group_id
}

module "s3" {
  source = "../../modules/s3"

  bucket_name = "cloud-native-employee-management-prod"
}